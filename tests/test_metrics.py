from mdcompressor.metrics import measure_text


def test_measure_text_counts_chars_and_bytes() -> None:
    m = measure_text("abc你好")
    assert m.chars == 5
    assert m.bytes_utf8 == len("abc你好".encode("utf-8"))
