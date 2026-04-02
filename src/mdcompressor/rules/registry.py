from __future__ import annotations

from .base import BaseRule
from .markdown_tables import (
    CompressTableDelimiterRule,
    NormalizeTablePipeSpacingRule,
    RemoveOuterTablePipesRule,
    TrimTableCellPaddingRule,
)
from .markdown_whitespace import (
    CollapseIntraLineSpacesRule,
    CollapseListInterItemBlankLinesRule,
    CollapseBlankLinesRule,
    NormalizeHeadingSpacingRule,
    NormalizeHeadingSuffixHashesRule,
    NormalizeListSpacingRule,
    NormalizeQuoteSpacingRule,
    NormalizeThematicBreakRule,
    TrimTrailingSpacesRule,
)
from .math_aggressive import MathMacroToUnicodeRule
from .math_safe import MathTrimSpacesRule


def _all_rules() -> list[BaseRule]:
    return [
        TrimTrailingSpacesRule(),
        CollapseBlankLinesRule(),
        CollapseIntraLineSpacesRule(),
        CollapseListInterItemBlankLinesRule(),
        NormalizeHeadingSpacingRule(),
        NormalizeHeadingSuffixHashesRule(),
        NormalizeQuoteSpacingRule(),
        NormalizeListSpacingRule(),
        TrimTableCellPaddingRule(),
        NormalizeTablePipeSpacingRule(),
        CompressTableDelimiterRule(),
        RemoveOuterTablePipesRule(),
        NormalizeThematicBreakRule(),
        MathTrimSpacesRule(),
        MathMacroToUnicodeRule(),
    ]


def get_rules(mode: str) -> list[BaseRule]:
    rules = _all_rules()
    if mode == "safe":
        return [r for r in rules if r.risk == "low"]
    return [r for r in rules if r.risk in {"low", "medium", "high"}]
