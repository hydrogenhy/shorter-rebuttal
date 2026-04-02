from __future__ import annotations

import json
from dataclasses import asdict

from .contribution_report import ContributionReport
from .models import CompressionResult


def to_json(result: CompressionResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def get_contribution_report(result: CompressionResult) -> ContributionReport:
    return ContributionReport(result)

