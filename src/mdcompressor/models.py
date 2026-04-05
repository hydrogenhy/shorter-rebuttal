from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rules.base import BaseRule

RiskLevel = Literal["low", "medium", "high"]
Mode = Literal["safe", "aggressive"]
SegmentType = Literal[
    "fenced_code",
    "inline_code",
    "math_block",
    "math_inline",
    "html_block",
    "text",
]


@dataclass
class CompressionOptions:
    mode: Mode = "safe"
    verify: bool = True
    strict_verify: bool = False
    renderer_profile: str = "gfm"
    enabled_rules: Optional[list[str]] = None
    disabled_rules: Optional[list[str]] = None
    custom_rules: Optional[list["BaseRule"]] = None


@dataclass
class RuleResult:
    rule_id: str
    changed: bool
    chars_saved: int
    notes: str = ""


@dataclass
class Metrics:
    chars: int
    bytes_utf8: int


@dataclass
class Segment:
    kind: SegmentType
    text: str


@dataclass
class CompressionResult:
    original_text: str
    compressed_text: str
    original_chars: int
    compressed_chars: int
    original_bytes: int
    compressed_bytes: int
    rules_applied: list[RuleResult] = field(default_factory=list)
    verify_passed: bool = True
    verify_message: str = "ok"

    @property
    def chars_saved(self) -> int:
        return self.original_chars - self.compressed_chars

    @property
    def bytes_saved(self) -> int:
        return self.original_bytes - self.compressed_bytes

    @property
    def reduction_ratio(self) -> float:
        if self.original_chars == 0:
            return 0.0
        return self.chars_saved / self.original_chars
