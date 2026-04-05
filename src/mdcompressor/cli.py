from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional, cast

import typer

from .models import CompressionOptions
from .pipeline import compress_text
from .report import to_json, get_contribution_report
from .rules.base import BaseRule

app = typer.Typer(add_completion=False)


def _load_custom_rules_from_file(path: Path) -> list[BaseRule]:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise typer.BadParameter(f"Unable to load custom rules from: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    custom_rules = getattr(module, "CUSTOM_RULES", None)
    if custom_rules is None:
        raise typer.BadParameter(f"{path} must define CUSTOM_RULES")
    if not isinstance(custom_rules, list):
        raise typer.BadParameter(f"CUSTOM_RULES in {path} must be a list")

    for item in custom_rules:
        if not isinstance(item, BaseRule):
            raise typer.BadParameter(f"CUSTOM_RULES in {path} must contain BaseRule instances")

    return cast(list[BaseRule], custom_rules)


@app.command()
def run(
    source: Path = typer.Argument(..., exists=True, help="Source markdown file"),
    target: Path = typer.Argument(..., help="Target markdown file"),
    mode: str = typer.Option("safe", help="Compression mode: safe or aggressive"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Enable render equivalence check"),
    strict_verify: bool = typer.Option(False, help="Fail if verification fails"),
    report: Optional[Path] = typer.Option(None, help="Optional JSON report output path"),
    contribution: Optional[Path] = typer.Option(None, help="Optional rule contribution report path"),
    only_rule: list[str] = typer.Option(None, help="Only run these rule IDs"),
    skip_rule: list[str] = typer.Option(None, help="Skip these rule IDs"),
    custom_rules: Optional[Path] = typer.Option(
        None,
        "--custom-rules",
        exists=True,
        help="Load custom rules from a Python file exporting CUSTOM_RULES",
    ),
) -> None:
    text = source.read_text(encoding="utf-8")

    loaded_custom_rules = _load_custom_rules_from_file(custom_rules) if custom_rules else None

    options = CompressionOptions(
        mode=mode, verify=verify, strict_verify=strict_verify,
        enabled_rules=only_rule or None,
        disabled_rules=skip_rule or None,
        custom_rules=loaded_custom_rules,
    )

    result = compress_text(text, options)

    target.write_text(result.compressed_text, encoding="utf-8")

    typer.echo(f"source: {source}")
    typer.echo(f"target: {target}")
    typer.echo(f"chars: {result.original_chars} -> {result.compressed_chars} (saved {result.chars_saved})")
    typer.echo(f"bytes: {result.original_bytes} -> {result.compressed_bytes} (saved {result.bytes_saved})")
    typer.echo(f"ratio: {result.reduction_ratio:.2%}")
    if verify:
        typer.echo(f"verify: {result.verify_passed} ({result.verify_message})")
    else:
        typer.echo(f"verify: off ({result.verify_message})")

    contrib_report = get_contribution_report(result)
    typer.echo("")
    typer.echo(contrib_report.to_text_summary())

    if report:
        report.write_text(to_json(result), encoding="utf-8")
        typer.echo(f"json report: {report}")

    if contribution:
        import json

        contribution.write_text(
            json.dumps(contrib_report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        typer.echo(f"contribution report: {contribution}")


if __name__ == "__main__":
    app()
