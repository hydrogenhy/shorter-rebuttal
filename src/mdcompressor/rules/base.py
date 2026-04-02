from __future__ import annotations

from dataclasses import dataclass

from ..models import RiskLevel, RuleResult


@dataclass
class BaseRule:
    id: str
    description: str
    risk: RiskLevel
    targets: set[str]

    def apply(self, text: str) -> tuple[str, RuleResult]:
        raise NotImplementedError
