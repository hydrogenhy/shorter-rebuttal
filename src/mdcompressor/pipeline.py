from __future__ import annotations

from typing import Optional

from .metrics import measure_text
from .models import CompressionOptions, CompressionResult, RuleResult
from .parser_segments import merge_segments, split_segments
from .rules import get_rules
from .verifier import verify_equivalence


def _filter_rules(all_rules, options: CompressionOptions):
    rules = all_rules
    if options.enabled_rules:
        allow = set(options.enabled_rules)
        rules = [r for r in rules if r.id in allow]
    if options.disabled_rules:
        block = set(options.disabled_rules)
        rules = [r for r in rules if r.id not in block]
    return rules


def compress_text(text: str, options: Optional[CompressionOptions] = None) -> CompressionResult:
    options = options or CompressionOptions()
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")

    segments = split_segments(text)
    rules = _filter_rules(get_rules(options.mode), options)
    if options.custom_rules:
        rules = rules + list(options.custom_rules)

    rule_stats: dict[str, RuleResult] = {
        r.id: RuleResult(rule_id=r.id, changed=False, chars_saved=0, notes="") for r in rules
    }

    for i, seg in enumerate(segments):
        current = seg.text
        for rule in rules:
            if seg.kind not in rule.targets:
                continue
            new_text, rr = rule.apply(current)
            if rr.changed:
                stat = rule_stats[rule.id]
                stat.changed = True
                stat.chars_saved += rr.chars_saved
                if rr.notes:
                    stat.notes = rr.notes
            current = new_text
        segments[i].text = current

    compressed = merge_segments(segments)

    before = measure_text(text)
    after = measure_text(compressed)

    verify_passed = True
    verify_msg = "skipped"
    if options.verify:
        verify_passed, verify_msg = verify_equivalence(text, compressed, options.renderer_profile)

    if options.strict_verify and not verify_passed:
        raise ValueError(f"verification failed: {verify_msg}")

    return CompressionResult(
        original_text=text,
        compressed_text=compressed,
        original_chars=before.chars,
        compressed_chars=after.chars,
        original_bytes=before.bytes_utf8,
        compressed_bytes=after.bytes_utf8,
        rules_applied=[rule_stats[r.id] for r in rules],
        verify_passed=verify_passed,
        verify_message=verify_msg,
    )
