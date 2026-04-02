from __future__ import annotations

import re

from ..models import RuleResult
from .base import BaseRule


class CompressTableDelimiterRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="compress-table-delimiter",
            description="Compress table delimiter hyphens",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        lines = text.splitlines(keepends=True)
        out_lines: list[str] = []
        for line in lines:
            if "|" in line and "-" in line and re.search(r"^[|:\- \t]+\r?\n?$", line):
                core = line.rstrip("\r\n")
                eol = line[len(core):]
                parts = core.split("|")
                new_parts: list[str] = []
                for p in parts:
                    s = p.strip()
                    if not s:
                        new_parts.append(p)
                        continue
                    left = s.startswith(":")
                    right = s.endswith(":")
                    mid = "-"
                    if left and right:
                        repl = ":-:"
                    elif left:
                        repl = ":-"
                    elif right:
                        repl = "-:"
                    else:
                        repl = mid
                    new_parts.append(repl)
                out_lines.append("|".join(new_parts) + eol)
            else:
                out_lines.append(line)
        out = "".join(out_lines)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class TrimTableCellPaddingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="trim-table-cell-padding",
            description="Trim optional spaces around table cell content",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        lines = text.splitlines(keepends=True)
        out_lines: list[str] = []
        for line in lines:
            if "|" not in line:
                out_lines.append(line)
                continue
            core = line.rstrip("\r\n")
            eol = line[len(core):]
            parts = core.split("|")
            if len(parts) < 3:
                out_lines.append(line)
                continue
            new_parts = [parts[0]]
            for cell in parts[1:-1]:
                new_parts.append(cell.strip())
            new_parts.append(parts[-1])
            out_lines.append("|".join(new_parts) + eol)
        out = "".join(out_lines)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class NormalizeTablePipeSpacingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="normalize-table-pipe-spacing",
            description="Remove spaces around table pipes",
            risk="low",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        lines = text.splitlines(keepends=True)
        out_lines: list[str] = []
        for line in lines:
            core = line.rstrip("\r\n")
            eol = line[len(core):]
            if core.count("|") >= 2:
                compact = re.sub(r"[ \t]*\|[ \t]*", "|", core)
                out_lines.append(compact + eol)
            else:
                out_lines.append(line)
        out = "".join(out_lines)
        return out, RuleResult(self.id, out != text, len(text) - len(out))


class RemoveOuterTablePipesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="remove-outer-table-pipes",
            description="Remove optional leading and trailing table border pipes",
            risk="medium",
            targets={"text"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        lines = text.splitlines(keepends=True)
        out_lines: list[str] = []
        for line in lines:
            core = line.rstrip("\r\n")
            eol = line[len(core):]
            stripped = core.strip()
            if core.count("|") >= 2 and stripped.startswith("|") and stripped.endswith("|"):
                new_core = stripped[1:-1]
                out_lines.append(new_core + eol)
            else:
                out_lines.append(line)
        out = "".join(out_lines)
        return out, RuleResult(self.id, out != text, len(text) - len(out))
