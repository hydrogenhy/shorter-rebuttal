from __future__ import annotations

from .models import Metrics


def measure_text(text: str) -> Metrics:
    return Metrics(chars=len(text), bytes_utf8=len(text.encode("utf-8")))
