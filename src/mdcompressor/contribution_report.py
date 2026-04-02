from __future__ import annotations

from dataclasses import dataclass

from .models import CompressionResult, RuleResult


@dataclass
class RuleContribution:
    rule_id: str
    description: str
    chars_saved: int
    percentage_of_total: float
    rank: int


class ContributionReport:
    def __init__(self, result: CompressionResult) -> None:
        self.result = result
        self.total_saved = result.chars_saved

    def get_ranked_contributions(self) -> list[RuleContribution]:
        if self.total_saved == 0:
            return []

        contributions: list[tuple[int, RuleResult]] = [
            (i, rule) for i, rule in enumerate(self.result.rules_applied) if rule.chars_saved > 0
        ]
        contributions.sort(key=lambda x: x[1].chars_saved, reverse=True)

        ranked = []
        for rank, (_, rule) in enumerate(contributions, 1):
            pct = (rule.chars_saved / self.total_saved) * 100 if self.total_saved > 0 else 0.0
            ranked.append(
                RuleContribution(
                    rule_id=rule.rule_id,
                    description=rule.notes or rule.rule_id,
                    chars_saved=rule.chars_saved,
                    percentage_of_total=pct,
                    rank=rank,
                )
            )
        return ranked

    def to_markdown_table(self) -> str:
        ranked = self.get_ranked_contributions()
        if not ranked:
            return "No rule contribution data available."

        lines = [
            "| Rank | Rule ID | Chars Saved | % of Total |",
            "| --- | --- | --- | --- |",
        ]
        for item in ranked:
            lines.append(
                f"| {item.rank} | {item.rule_id} | {item.chars_saved} | {item.percentage_of_total:.1f}% |"
            )
        return "\n".join(lines)

    def to_text_summary(self) -> str:
        ranked = self.get_ranked_contributions()
        if not ranked:
            return "No rule contribution data available."

        lines = ["=== Rule Contribution Report ==="]
        lines.append(f"Total chars saved: {self.total_saved}")
        lines.append("")
        for item in ranked:
            lines.append(
                f"{item.rank:2d}. {item.rule_id:30s} {item.chars_saved:6d} chars ({item.percentage_of_total:5.1f}%)"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_saved": self.total_saved,
            "original_chars": self.result.original_chars,
            "compressed_chars": self.result.compressed_chars,
            "reduction_ratio": self.result.reduction_ratio,
            "rule_contributions": [
                {
                    "rank": r.rank,
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "chars_saved": r.chars_saved,
                    "percentage": r.percentage_of_total,
                }
                for r in self.get_ranked_contributions()
            ],
        }
