from __future__ import annotations

import re

from .models import Segment

_FENCE_RE = re.compile(r"(^```[\s\S]*?^```[ \t]*$)", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"(`[^`\n]+`)")
_MATH_BLOCK_RE = re.compile(r"(\$\$[\s\S]*?\$\$|\\\\\[[\s\S]*?\\\\\])", re.MULTILINE)
_MATH_INLINE_RE = re.compile(r"(\$[^$\n]+\$|\\\\\([^\n]+?\\\\\))")
_HTML_BLOCK_RE = re.compile(r"(^<[^>\n]+>[\s\S]*?^</[^>\n]+>[ \t]*$)", re.MULTILINE)


def _split_by_pattern(parts: list[Segment], pattern: re.Pattern[str], kind: str) -> list[Segment]:
    out: list[Segment] = []
    for seg in parts:
        if seg.kind != "text":
            out.append(seg)
            continue
        last = 0
        text = seg.text
        for match in pattern.finditer(text):
            if match.start() > last:
                out.append(Segment(kind="text", text=text[last:match.start()]))
            out.append(Segment(kind=kind, text=match.group(0)))
            last = match.end()
        if last < len(text):
            out.append(Segment(kind="text", text=text[last:]))
    return out


def split_segments(text: str) -> list[Segment]:
    parts = [Segment(kind="text", text=text)]
    parts = _split_by_pattern(parts, _FENCE_RE, "fenced_code")
    parts = _split_by_pattern(parts, _MATH_BLOCK_RE, "math_block")
    parts = _split_by_pattern(parts, _HTML_BLOCK_RE, "html_block")
    parts = _split_by_pattern(parts, _INLINE_CODE_RE, "inline_code")
    parts = _split_by_pattern(parts, _MATH_INLINE_RE, "math_inline")
    return parts


def merge_segments(segments: list[Segment]) -> str:
    return "".join(seg.text for seg in segments)
