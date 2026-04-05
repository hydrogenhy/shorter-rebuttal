from __future__ import annotations

import re

from ..models import RuleResult
from .base import BaseRule


class TrimTrailingSpacesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="trim-trailing-spaces",
            description="Trim trailing spaces",
            risk="low",
            targets={"text", "math_inline", "math_block"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        def _trim_line(line: str) -> str:
            core = line.rstrip("\r\n")
            eol = line[len(core):]

            # Preserve the required separator after markdown markers so that
            # segmented processing does not merge `- ` with inline code/math.
            if re.match(r"^[ \t]*(?:>+|#{1,6}|[-*+]|\d+\.)[ \t]+$", core):
                return re.sub(r"[ \t]+$", "", core) + " " + eol

            # Also preserve a single separator after punctuation when the text
            # segment ends immediately before an inline code/math segment.
            if re.match(r".*[:;,!?][ \t]+$", core):
                return re.sub(r"[ \t]+$", "", core) + " " + eol

            return re.sub(r"[ \t]+$", "", core) + eol

        out = "".join(_trim_line(line) for line in text.splitlines(keepends=True))

        return out, RuleResult(self.id, out != text, len(text) - len(out))


class CollapseBlankLinesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="collapse-blank-lines",
            description="Collapse 3+ blank lines to 2",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"\n{3,}", "\n\n", text)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeHeadingSpacingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-heading-spacing",
            description="Normalize heading marker spacing",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"^(#{1,6})[ \t]{2,}", r"\1 ", text, flags=re.MULTILINE)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeQuoteSpacingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-quote-spacing",
            description="Normalize blockquote spacing",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"^(>+)[ \t]{2,}", r"\1 ", text, flags=re.MULTILINE)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeListSpacingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-list-spacing",
            description="Normalize list marker spacing",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"^([ \t]*[-*+])[ \t]{2,}", r"\1 ", text, flags=re.MULTILINE)
        out = re.sub(r"^([ \t]*\d+\.)[ \t]{2,}", r"\1 ", out, flags=re.MULTILINE)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class TrimDocumentEdgesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="trim-document-edges",
            description="Remove extra blank lines at document head/tail",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"\A(?:[ \t]*\r?\n)+", "", text)
        out = re.sub(r"(?:\r?\n[ \t]*)+\Z", "\n", out)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeHeadingSuffixHashesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-heading-suffix-hashes",
            description="Remove optional closing hashes in ATX headings",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = re.sub(r"^(#{1,6}\s.*?)[ \t]+#+[ \t]*$", r"\1", text, flags=re.MULTILINE)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeThematicBreakRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-thematic-break",
            description="Normalize thematic break lines to ---",
            risk="medium",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        pattern = re.compile(r"^(\s*)([*_-])(?:\s*\2){2,}\s*$", re.MULTILINE)
        out = pattern.sub(r"\1---", text)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class CollapseIntraLineSpacesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="collapse-intra-line-spaces",
            description="Collapse repeated spaces in plain text lines",
            risk="medium",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        lines = text.splitlines(keepends=True)
        out_lines: list[str] = []
        for line in lines:
            core = line.rstrip("\r\n")
            eol = line[len(core):]

            if not core:
                out_lines.append(line)
                continue
            if core.endswith("  "):
                out_lines.append(line)
                continue
            if "|" in core:
                out_lines.append(line)
                continue

            # Keep truly indented code blocks intact, but allow nested list items
            # such as "    - Second   level   item   1" to be compressed.
            stripped = core.lstrip(" \t")
            indent = core[: len(core) - len(stripped)]
            if indent.startswith("\t"):
                out_lines.append(line)
                continue
            if len(indent) >= 4 and not re.match(r"(?:[-*+]|\d+\.)\s+", stripped):
                out_lines.append(line)
                continue

            out_core = re.sub(r"(?<=\S) {2,}(?=\S)", " ", core)
            out_lines.append(out_core + eol)

        out = "".join(out_lines)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class CollapseListInterItemBlankLinesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="collapse-list-interitem-blank-lines",
            description="Collapse repeated blank lines between adjacent list items",
            risk="medium",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        pattern = re.compile(
            r"(^[ \t]*(?:[-*+]\s+|\d+\.\s+).+?\r?\n)(?:[ \t]*\r?\n){2,}(?=^[ \t]*(?:[-*+]\s+|\d+\.\s+))",
            re.MULTILINE,
        )
        out = pattern.sub(r"\1\n", text)
        return out, RuleResult(self.id, out != text, len(text) - len(out))
