# 📝 Markdown Character Compressor

🌐 **Language** | [English](#markdown-character-compressor) | [中文](./README_CN.md)

A powerful tool to compress Markdown files with render-aware verification. `safe` mode prioritizes rendering stability, while `aggressive` mode targets higher compression with possible mismatch risk.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## ✨ Features

- 🖥️ **Two operating modes:** Command-line one-shot conversion and interactive GUI
- 🎯 **Rule-based compression:** Safe and aggressive modes with 15+ configurable rules
- ✅ **Render equivalence verification:** Detects potential rendering mismatches before final output
- 📊 **Detailed rule contribution report:** See exactly which rules saved how many characters
- 🔧 **Custom rule support:** Add your own character replacements or functions
- 🌍 **Multi-language support:** Handles UTF-8 Chinese, English, math symbols, etc.

## 📦 Installation

```bash
pip install -e .
```

## 🚀 Quick Start

### 🎨 GUI Mode (Recommend)

Interactive side-by-side editor and preview (embedded HTML iframe rendering):

```bash
streamlit run ui/app.py
```

### 💻 CLI Mode

One-command conversion:

```bash
python main.py source.md target.md
```

With options:

```bash
python main.py source.md target.md --mode aggressive --contribution report.json
```


## 🎛️ Mode Guidance

- `safe` (recommended default): Uses low-risk rules and is best for final submissions that require stable rendering.
- `aggressive`: Enables medium/high-risk rules for stronger compression; can introduce render mismatches in some edge cases.
- Recommended workflow: run `aggressive` first, then switch to `safe` or disable risky rules if verification reports mismatch.

## ⚙️ CLI Options

```
--mode safe|aggressive        Compression mode (safe = stability, aggressive = max savings)
--verify/--no-verify          Enable render equivalence check (default: enabled)
--strict-verify               Fail if verification fails
--report FILE                 Output detailed JSON report
--contribution FILE           Output rule contribution breakdown
--only-rule RULE_ID           Run only specific rules (repeatable)
--skip-rule RULE_ID           Skip specific rules (repeatable)
```

## 📋 Compression Rules

### 🟢 Low Risk (Safe Mode)
- Trim trailing spaces
- Collapse blank lines (3+ → 2)
- Normalize heading/quote/list marker spacing
- Remove heading closing hashes
- Compress table delimiters and cells
- Trim table cell padding
- Math space compression

### 🟡 Medium Risk (Aggressive Mode)
- Collapse intra-line repeated spaces
- Collapse list inter-item blank lines
- Normalize thematic breaks
- Remove outer table pipes
- Advanced math space compression

These rules may alter edge-case parsing in some renderers.

### 🔴 High Risk (Aggressive Mode)
- LaTeX macro to UTF-8 conversion: `\alpha` → `α`, `\rightarrow` → `→`, etc.
- Advanced formula optimization

These rules can increase compression significantly, but are the most likely source of render mismatch.

Supported macro replacements include:
- Greek letters: α, β, γ, δ, λ, π, σ, Σ, ω, Ω, φ, ψ, ε, θ, μ, ν
- Math operators: ×, ·, ±, ≤, ≥, ≠, ≈
- Arrows: →, ←, ↔, ∞

## 📤 Output Example

Running with contribution report:

```
=== Rule Contribution Report ===
Total chars saved: 642

 1. collapse-intra-line-spaces        368 chars ( 57.3%)
 2. trim-table-cell-padding           136 chars ( 21.2%)
 3. math-trim-spaces                   42 chars (  6.5%)
 4. math-macro-to-unicode              42 chars (  6.5%)
 ...
```

## 🔧 Custom Rules

Custom rules can be used directly from the CLI with a Python file that exports `CUSTOM_RULES`.

```bash
python main.py file.md out.md --custom-rules my_rules.py
```

The Python file should define:

```python
CUSTOM_RULES = [rule1, rule2, ...]
```

### User-Defined Replacements

```python
from mdcompressor.rules.custom_rules import CustomReplacementRule

rule = CustomReplacementRule(
    rule_id="my-shorthand",
    description="Replace common phrases",
    replacements={
        "therefore": "∴",
        "because": "∵",
    },
    targets={"text"},
    risk="medium"
)
```

### User-Defined Functions

```python
from mdcompressor.rules.custom_rules import CustomFunctionRule

def my_compressor(text: str) -> str:
    return text.replace("  ", " ")

rule = CustomFunctionRule(
    rule_id="my-function",
    description="Custom compression",
    func=my_compressor,
    targets={"text"},
    risk="low"
)
```

You can place both replacement and function rules into the same `CUSTOM_RULES` list and load them together from the CLI.

## 📐 Renderer Profile

Default: GitHub Flavored Markdown (GFM)
- Tables enabled
- Strikethrough supported
- Math: passed through as text (not rendered)

## ✔️ Verification

The tool compares normalized HTML before/after:
- Removes semantic-free whitespace
- Normalizes attribute order
- Detects structural changes

Strict verification (`--strict-verify`) will reject output if rendering differs.

Notes:
- `safe` mode should be preferred when visual equivalence is mandatory.
- `aggressive` mode may trigger mismatch on formula-heavy content or renderer-specific edge cases.
- If mismatch occurs, keep verification enabled and disable risky rules incrementally.

## 💡 Use Cases

### 📚 Academic Rebuttal
```bash
python main.py rebuttal.md rebuttal.compressed.md --mode aggressive --contribution report.json
```

This typically achieves higher savings, but always review verification results before submission.

### 📖 Development Docs
```bash
python main.py docs.md docs.min.md --mode safe
```

Safe mode preserves all rendering and is suitable for versioning.

### 📦 Batch Processing

See `Sample.md` for a comprehensive example with:
- 5-level headings
- Multiple tables  
- Inline and display math
- Lists (nested, ordered, unordered)
- Code blocks
- Blockquotes
- Links and formatting

## 🎨 GUI Features

- 👁️ Real-time preview with original and compressed markdown
- 📊 Side-by-side character and byte counts
- 🎚️ Rule enable/disable toggles
- 🔄 Mode switch (safe/aggressive)
- 📄 Side-by-side rendered preview comparison
- 📈 Rule contribution breakdown
- 📋 Copy and export buttons

## 🏗️ Technical Details

### Architecture
- 🔀 Segment parser: Protects code, math, and HTML from unsafe transformations
- ⚙️ Pipeline: Applies rules per-segment, avoiding false positives
- ✔️ Verifier: Renders and compares normalized HTML before/after
- 📊 Report: Tracks per-rule contribution and generates rankings

### Performance
- ⚡ 5-20KB files: <200ms on standard laptop
- 🔍 Verification: Included in total time
- 🎯 Incremental: Can apply rules selectively

## ⚠️ Limitations

- HTML content is passed through as-is; no verification inside HTML blocks
- Some renderers may interpret markdown differently
- Math rendering depends on renderer support (no actual math execution)
- Unicode symbol support varies by platform

## 🔄 Renderer Compatibility

Tested with:
- GitHub (GFM)
- Jupyter Notebook
- Pandoc (markdown mode)
- Standard CommonMark

Note: Different renderers may handle edge cases differently. Always verify output visually.

## 🤝 Contributing

To add new rules:

1. Create a subclass of `BaseRule` in `src/mdcompressor/rules/`
2. Implement the `apply()` method
3. Register in `src/mdcompressor/rules/registry.py`
4. Add tests in `tests/`

See existing rules for patterns.

## 📄 License

MIT
