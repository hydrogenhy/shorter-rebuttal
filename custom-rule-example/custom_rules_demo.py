from mdcompressor.rules.custom_rules import CustomFunctionRule, CustomReplacementRule


def collapse_double_spaces(text: str) -> str:
    return text.replace("  ", " ")


CUSTOM_RULES = [
    CustomReplacementRule(
        rule_id="academic-shortcuts",
        description="Replace common academic phrases",
        replacements={
            "therefore": "∴",
            "because": "∵",
            "if and only if": "⟺",
        },
        targets={"text"},
        risk="low",
    ),
    CustomFunctionRule(
        rule_id="collapse-double-spaces",
        description="Collapse repeated double spaces in plain text",
        func=collapse_double_spaces,
        targets={"text"},
        risk="low",
    ),
]
