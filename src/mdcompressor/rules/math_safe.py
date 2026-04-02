from __future__ import annotations

import re

from ..models import RuleResult
from .base import BaseRule


class MathTrimSpacesRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="math-trim-spaces",
            description="Trim redundant spaces in math segments",
            risk="medium",
            targets={"math_inline", "math_block"},
        )

    def apply(self, text: str) -> tuple[str, RuleResult]:
        body = text
        if text.startswith("$$") and text.endswith("$$") and len(text) >= 4:
            inner = text[2:-2]
            inner = re.sub(r"[ \t]{2,}", " ", inner)
            inner = re.sub(r"\s*([=+\-*/<>])\s*", r"\1", inner)
            out = "$$" + inner.strip() + "$$"
        elif text.startswith("$") and text.endswith("$") and len(text) >= 2:
            inner = text[1:-1]
            inner = re.sub(r"[ \t]{2,}", " ", inner)
            inner = re.sub(r"\s*([=+\-*/<>])\s*", r"\1", inner)
            out = "$" + inner.strip() + "$"
        elif text.startswith("\\(") and text.endswith("\\)"):
            inner = text[2:-2]
            inner = re.sub(r"[ \t]{2,}", " ", inner)
            out = "\\(" + inner.strip() + "\\)"
        elif text.startswith("\\[") and text.endswith("\\]"):
            inner = text[2:-2]
            inner = re.sub(r"[ \t]{2,}", " ", inner)
            out = "\\[" + inner.strip() + "\\]"
        else:
            out = body
        return out, RuleResult(self.id, out != text, len(text) - len(out))
