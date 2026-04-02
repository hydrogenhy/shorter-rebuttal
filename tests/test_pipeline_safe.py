from mdcompressor.models import CompressionOptions
from mdcompressor.pipeline import compress_text


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
