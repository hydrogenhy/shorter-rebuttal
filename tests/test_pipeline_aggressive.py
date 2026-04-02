from mdcompressor.models import CompressionOptions
from mdcompressor.pipeline import compress_text


def test_aggressive_mode_math_macro_to_utf8() -> None:
    src = "Eq: $\\alpha + \\beta \\rightarrow \\gamma$\n"
    result = compress_text(src, CompressionOptions(mode="aggressive", verify=False))
    assert "α" in result.compressed_text
    assert "β" in result.compressed_text
    assert "→" in result.compressed_text


def test_aggressive_mode_remove_outer_table_pipes() -> None:
    src = "| A | B |\n| --- | --- |\n| x | y |\n"
    result = compress_text(src, CompressionOptions(mode="aggressive", verify=False))
    assert result.compressed_text.splitlines()[0] == "A|B"
