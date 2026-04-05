from __future__ import annotations

import difflib
import re

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

from .parser_segments import split_segments


_MATH_MACRO_MAP = {
    r"\\alpha": "α",
    r"\\beta": "β",
    r"\\gamma": "γ",
    r"\\delta": "δ",
    r"\\epsilon": "ε",
    r"\\varepsilon": "ε",
    r"\\theta": "θ",
    r"\\vartheta": "ϑ",
    r"\\lambda": "λ",
    r"\\mu": "μ",
    r"\\nu": "ν",
    r"\\sigma": "σ",
    r"\\Sigma": "Σ",
    r"\\omega": "ω",
    r"\\Omega": "Ω",
    r"\\pi": "π",
    r"\\phi": "φ",
    r"\\varphi": "φ",
    r"\\psi": "ψ",
    r"\\times": "×",
    r"\\cdot": "·",
    r"\\pm": "±",
    r"\\to": "→",
    r"\\rightarrow": "→",
    r"\\leftarrow": "←",
    r"\\leftrightarrow": "↔",
    r"\\infty": "∞",
    r"\\approx": "≈",
    r"\\leq": "≤",
    r"\\geq": "≥",
    r"\\neq": "≠",
}


def _renderer(profile: str) -> MarkdownIt:
    if profile == "gfm":
        md = MarkdownIt("commonmark", {"html": True})
        md.enable("table")
        md.enable("strikethrough")
        return md
    return MarkdownIt("commonmark", {"html": True})


def _normalize_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        if tag.attrs:
            ordered = {}
            for key in sorted(tag.attrs.keys()):
                ordered[key] = tag.attrs[key]
            tag.attrs = ordered

    normalized = str(soup)
    normalized = " ".join(normalized.split())
    return normalized


def _normalize_math_segment(seg_text: str) -> str:
    text = seg_text

    # Remove delimiters first.
    if text.startswith("$$") and text.endswith("$$"):
        text = text[2:-2]
    elif text.startswith("\\[") and text.endswith("\\]"):
        text = text[2:-2]
    elif text.startswith("$") and text.endswith("$"):
        text = text[1:-1]
    elif text.startswith("\\(") and text.endswith("\\)"):
        text = text[2:-2]

    # Canonicalize selected macros so macro/unicode forms compare equally.
    for src, dst in _MATH_MACRO_MAP.items():
        text = text.replace(src, dst)

    # Ignore redundant whitespace in math expressions.
    text = re.sub(r"\s+", "", text)
    return text


def _canonicalize_for_verification(text: str) -> tuple[str, list[str]]:
    segments = split_segments(text)
    math_norm: list[str] = []
    out_parts: list[str] = []
    idx = 0

    for seg in segments:
        if seg.kind in {"math_inline", "math_block"}:
            out_parts.append(f"@@MATH_{idx}@@")
            math_norm.append(_normalize_math_segment(seg.text))
            idx += 1
        else:
            out_parts.append(seg.text)

    canonical = "".join(out_parts)

    # Treat optional spaces between punctuation and inline math as equivalent,
    # e.g. "Equation: $x$" and "Equation:$x$".
    canonical = re.sub(r"([:;,!?])\s+(@@MATH_\d+@@)", r"\1\2", canonical)
    canonical = re.sub(r"(@@MATH_\d+@@)\s+([,.;:!?])", r"\1\2", canonical)

    return canonical, math_norm


def _truncate(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _first_diff_snippet(before: str, after: str, context: int = 24) -> str:
    matcher = difflib.SequenceMatcher(a=before, b=after)
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            continue
        before_snip = _truncate(before[max(0, a0 - context) : min(len(before), a1 + context)])
        after_snip = _truncate(after[max(0, b0 - context) : min(len(after), b1 + context)])
        return f"before=`{before_snip}`; after=`{after_snip}`"
    return ""


def verify_equivalence(before_text: str, after_text: str, profile: str = "gfm") -> tuple[bool, str]:
    before_canon, before_math = _canonicalize_for_verification(before_text)
    after_canon, after_math = _canonicalize_for_verification(after_text)

    if before_math != after_math:
        max_len = max(len(before_math), len(after_math))
        for idx in range(max_len):
            left = before_math[idx] if idx < len(before_math) else "<missing>"
            right = after_math[idx] if idx < len(after_math) else "<missing>"
            if left != right:
                snippet = _first_diff_snippet(left, right)
                detail = f"; first diff: {snippet}" if snippet else ""
                return False, f"render mismatch in math segment {idx}{detail}"

    md = _renderer(profile)
    before_html = md.render(before_canon)
    after_html = md.render(after_canon)

    before_norm = _normalize_html(before_html)
    after_norm = _normalize_html(after_html)

    if before_norm == after_norm:
        return True, "ok"

    snippet = _first_diff_snippet(before_norm, after_norm)
    hint = "render mismatch after normalization"
    if snippet:
        hint = f"{hint}; first diff: {snippet}"
    return False, hint
