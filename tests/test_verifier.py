from mdcompressor.verifier import verify_equivalence


def test_verify_equivalence_pass() -> None:
    a = "# T\n\ntext\n"
    b = "# T\n\ntext\n"
    ok, _ = verify_equivalence(a, b)
    assert ok
