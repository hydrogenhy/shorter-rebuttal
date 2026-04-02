# Custom Rules Guide

## Overview

The Markdown Compressor supports user-defined rules for custom character replacements and transformations.

## Method 1: Replacement Rules

For simple string-to-string replacements:

```python
from mdcompressor.rules.custom_rules import CustomReplacementRule
from mdcompressor.pipeline import compress_text
from mdcompressor.models import CompressionOptions

# Define your custom rule
my_rule = CustomReplacementRule(
    rule_id="my-shortcuts",
    description="Replace common academic phrases",
    replacements={
        "therefore": "∴",
        "because": "∵",
        "implies": "⟹",
        "if and only if": "⟺",
    },
    targets={"text"},  # Apply to text segments only
    risk="low"  # Can be "low", "medium", "high"
)

# Apply it to existing rules
from mdcompressor.rules.registry import get_rules

text = "This is true because x."
opts = CompressionOptions(mode="safe")
all_rules = get_rules(opts.mode)
all_rules.append(my_rule)

# Note: You'd need to integrate this into the pipeline
# For now, you can manually apply:
result = compress_text(text, opts)
```

## Method 2: Function-Based Rules

For complex transformations:

```python
from mdcompressor.rules.custom_rules import CustomFunctionRule
import re

def compress_repeated_chars(text: str) -> str:
    """Compress repeated special chars"""
    text = re.sub(r'\.{4,}', '…', text)  # .... → …
    text = re.sub(r'-{4,}', '—', text)   # ---- → —
    return text

my_func_rule = CustomFunctionRule(
    rule_id="char-compression",
    description="Compress repeated characters to unicode",
    func=compress_repeated_chars,
    targets={"text"},
    risk="medium"
)
```

## Method 3: Via CLI (Planned)

In future versions, a config file will support custom rules:

```yaml
# custom_rules.yaml
rules:
  - id: academic-shortcuts
    description: Academic symbols
    type: replacement
    targets: [text]
    replacements:
      "therefore": "∴"
      "because": "∵"
    risk: low
```

Then use:
```bash
python main.py file.md out.md --custom-rules custom_rules.yaml
```

## Segment Types

Specify which content types the rule applies to:

- `text`: Plain markdown text (safe target)
- `inline_code`: Backtick-enclosed code (usually don't modify)
- `fenced_code`: Code blocks (usually don't modify)
- `math_inline`: Inline math expressions
- `math_block`: Display math blocks
- `html_block`: Raw HTML blocks (usually don't modify)

## Risk Levels

- **low**: Always safe, no rendering impact expected
- **medium**: May affect rendering in edge cases
- **high**: Potentially risky, verify afterwards

## Examples

### Example 1: Math Symbol Shortcuts

```python
math_shortcuts = CustomReplacementRule(
    rule_id="math-symbols",
    description="Replace common math notation",
    replacements={
        r"\infty": "∞",
        r"\partial": "∂",
        r"\nabla": "∇",
        r"\sum": "Σ",
        r"\prod": "Π",
    },
    targets={"math_inline", "math_block"},
    risk="high"
)
```

### Example 2: Link Compression

```python
def compress_links(text: str) -> str:
    # Compress markdown links [text](url) → [t](url) for very short text
    # (Risky! Just an example)
    return text

link_compressor = CustomFunctionRule(
    rule_id="link-short",
    description="Shorten link text (risky)",
    func=compress_links,
    targets={"text"},
    risk="high"
)
```

### Example 3: Remove Trailing Comments

```python
def remove_html_comments(text: str) -> str:
    import re
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

comment_remover = CustomFunctionRule(
    rule_id="remove-comments",
    description="Remove HTML comments",
    func=remove_html_comments,
    targets={"text", "html_block"},
    risk="low"
)
```

## Integration into CLI

To use custom rules via CLI in future versions:

```bash
# Standalone compression
python main.py file.md out.md --load-custom-rules my_rules.py

# This will import custom rules from my_rules.py
# Expected format in my_rules.py:
# CUSTOM_RULES = [rule1, rule2, ...]
```

## Best Practices

1. **Test with small input first:** Verify behavior before large batches
2. **Use strict verification:** `--strict-verify` ensures rendering doesn't change
3. **Document replacements:** Keep a list of what your rules do
4. **Risk assessment:** Mark high-risk rules and review output carefully
5. **Target segmentation:** Limit rules to appropriate segment types

## Limitations

- Currently, custom rules must be registered programmatically
- No UI support yet for dynamic rule creation
- Rules are applied in registration order (watch for interdependencies)

## Future Roadmap

- Config file format (YAML/JSON)
- UI form for creating custom rules
- Rule conflict detection
- Dry-run mode for testing
- Rule composition (combine rules)
