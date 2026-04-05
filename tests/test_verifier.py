from mdcompressor.verifier import verify_equivalence


def test_verify_equivalence_pass() -> None:
    a = "# T\n\ntext\n"
    b = "# T\n\ntext\n"
    ok, _ = verify_equivalence(a, b)
    assert ok


def test_verify_equivalence_reports_math_diff() -> None:
    a = "Inline: $a+b$\n"
    b = "Inline: $a-b$\n"
    ok, message = verify_equivalence(a, b)
    assert not ok
    assert "math segment" in message
    assert "a+b" in message or "a-b" in message


def test_verify_equivalence_reports_html_diff() -> None:
    a = "# T\n\ntext\n"
    b = "## T\n\ntext\n"
    ok, message = verify_equivalence(a, b)
    assert not ok
    assert "first diff" in message or "render mismatch after normalization" in message
