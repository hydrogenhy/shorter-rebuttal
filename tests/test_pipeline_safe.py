from mdcompressor.models import CompressionOptions
from mdcompressor.pipeline import compress_text
from mdcompressor.rules.custom_rules import CustomReplacementRule


def test_safe_mode_compresses_whitespace() -> None:
    src = "##   Title  \n\n\n-   item\n"
    result = compress_text(src, CompressionOptions(mode="safe", verify=False))
    assert "## Title" in result.compressed_text
    assert "- item" in result.compressed_text
    assert result.compressed_chars < result.original_chars


def test_safe_mode_keeps_inline_code() -> None:
    src = "Use `a   b` exactly.\n"
    result = compress_text(src, CompressionOptions(mode="safe", verify=False))
    assert "`a   b`" in result.compressed_text


def test_safe_mode_keeps_space_between_list_marker_and_inline_code() -> None:
    src = "- `inline code (protected)`\n"
    result = compress_text(src, CompressionOptions(mode="safe", verify=False))
    assert "- `inline code (protected)`" in result.compressed_text


def test_aggressive_mode_keeps_space_between_list_marker_and_inline_code() -> None:
    src = "- `inline code (protected)`\n"
    result = compress_text(src, CompressionOptions(mode="aggressive", verify=False))
    assert "- `inline code (protected)`" in result.compressed_text


def test_aggressive_mode_keeps_space_after_punctuation_before_inline_segments() -> None:
    src_code = "Inline: `a+b`\n"
    result_code = compress_text(src_code, CompressionOptions(mode="aggressive", verify=False))
    assert "Inline: `a+b`" in result_code.compressed_text

    src_math = "Inline: $a+b$\n"
    result_math = compress_text(src_math, CompressionOptions(mode="aggressive", verify=False))
    assert "Inline: $a+b$" in result_math.compressed_text


def test_safe_mode_compresses_table_spaces_and_hyphens() -> None:
    src = "| A | B |\n| ---- | :----: |\n|  x  |  y  |\n"
    result = compress_text(src, CompressionOptions(mode="safe", verify=False))
    assert "|A|B|" in result.compressed_text
    assert "|-|:-:|" in result.compressed_text


def test_safe_mode_reduces_extra_newlines_and_spaces() -> None:
    src = "\n\n#   T   ###\n\n\nA  B\n\n\n"
    result = compress_text(src, CompressionOptions(mode="safe", verify=False))
    assert result.compressed_text.startswith("# T")
    assert "\n\n\n" not in result.compressed_text


def test_custom_rules_are_applied_via_compression_options() -> None:
    rule = CustomReplacementRule(
        rule_id="academic-shortcuts",
        description="Replace common academic phrases",
        replacements={"therefore": "∴"},
        targets={"text"},
        risk="low",
    )
    src = "This is true therefore x.\n"
    result = compress_text(
        src,
        CompressionOptions(mode="safe", verify=False, custom_rules=[rule]),
    )
    assert "∴" in result.compressed_text
