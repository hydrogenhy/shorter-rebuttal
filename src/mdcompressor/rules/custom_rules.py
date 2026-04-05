from __future__ import annotations

from typing import Callable, Optional

from ..models import RuleResult
from .base import BaseRule


class CustomReplacementRule(BaseRule):
    """User-defined character/string replacement rule."""

    def __init__(
        self,
        rule_id: str,
        description: str,
        replacements: dict[str, str],
        targets: set[str],
        risk: str = "medium",
    ) -> None:
        super().__init__(
            id=rule_id,
            description=description,
            risk=risk,
            targets=targets,
        )
        self.replacements = replacements

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = text
        for src, dst in self.replacements.items():
            out = out.replace(src, dst)
        return out, RuleResult(self.id, out != text, len(text) - len(out), f"custom replacement")


class CustomFunctionRule(BaseRule):
    """User-defined function-based rule."""

    def __init__(
        self,
        rule_id: str,
        description: str,
        func: Callable[[str], str],
        targets: set[str],
        risk: str = "medium",
    ) -> None:
        super().__init__(
            id=rule_id,
            description=description,
            risk=risk,
            targets=targets,
        )
        self.func = func

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = self.func(text)
        return out, RuleResult(self.id, out != text, len(text) - len(out), "custom function")
