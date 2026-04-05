from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import quote

import streamlit as st
from bs4 import BeautifulSoup, NavigableString
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mdcompressor.models import CompressionOptions
from mdcompressor.pipeline import compress_text
from mdcompressor.rules import get_rules
from mdcompressor.report import get_contribution_report


def _render_html(md_text: str) -> str:
    md = MarkdownIt("commonmark", {"html": True})
    md.enable("table")
    md.enable("strikethrough")
    rendered = md.render(md_text)
    return f"""
<!doctype html>
<html>
<head>
    <meta charset=\"utf-8\" />
    <script>
        window.MathJax = {{
            tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }},
            svg: {{ fontCache: 'global' }}
        }};
    </script>
    <script defer src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js\"></script>
    <style>
        body {{
            margin: 0;
            padding: 12px;
            color: #111827;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
        }}
        pre, code {{
            background: #f3f4f6;
            color: #111827;
        }}
        table {{
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 4px 8px;
        }}
    </style>
</head>
<body>
{rendered}
</body>
</html>
"""


def _to_data_uri(html: str) -> str:
    return "data:text/html;charset=utf-8," + quote(html)


def _highlight_render_differences(
    original_md: str,
    compressed_md: str,
    enable_highlight: bool,
) -> tuple[str, str]:
    """Render markdown and highlight visible-text differences with red background."""
    original_html = _render_html(original_md)
    compressed_html = _render_html(compressed_md)

    if not enable_highlight:
        return original_html, compressed_html

    soup_o = BeautifulSoup(original_html, "html.parser")
    soup_c = BeautifulSoup(compressed_html, "html.parser")

    def _text_nodes(soup: BeautifulSoup) -> list[NavigableString]:
        nodes: list[NavigableString] = []
        for node in soup.find_all(string=True):
            if not isinstance(node, NavigableString):
                continue
            if node.parent and node.parent.name in {"script", "style"}:
                continue
            if not node.strip():
                continue
            nodes.append(node)
        return nodes

    def _normalize_visible_text(text: str) -> str:
        # Browser rendering collapses most consecutive whitespace, so compare on normalized visible text.
        return re.sub(r"\s+", " ", text).strip()

    nodes_o = _text_nodes(soup_o)
    nodes_c = _text_nodes(soup_c)
    common_len = min(len(nodes_o), len(nodes_c))

    def _mark(node: NavigableString, soup: BeautifulSoup) -> None:
        span = soup.new_tag("span")
        span["class"] = "diff-highlight"
        span.string = str(node)
        node.replace_with(span)

    for i in range(common_len):
        left = _normalize_visible_text(str(nodes_o[i]))
        right = _normalize_visible_text(str(nodes_c[i]))
        if left != right:
            _mark(nodes_o[i], soup_o)
            _mark(nodes_c[i], soup_c)

    for i in range(common_len, len(nodes_o)):
        _mark(nodes_o[i], soup_o)
    for i in range(common_len, len(nodes_c)):
        _mark(nodes_c[i], soup_c)

    style = """
<style>
  .diff-highlight {
    background: #fecaca;
    color: #7f1d1d;
    border-radius: 2px;
    padding: 0 2px;
  }
</style>
"""
    if soup_o.head:
        soup_o.head.append(BeautifulSoup(style, "html.parser"))
    if soup_c.head:
        soup_c.head.append(BeautifulSoup(style, "html.parser"))

    return str(soup_o), str(soup_c)


st.set_page_config(page_title="Markdown Compressor", layout="wide", initial_sidebar_state="expanded")

st.title("📝 Markdown Character Compressor")
st.write("Compress your Markdown while preserving rendering. Perfect for academic rebuttals with character limits.")

with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.selectbox(
        "Compression Mode",
        ["safe", "aggressive"],
        index=0,
        help="Safe: prioritize rendering stability. Aggressive: prioritize max compression and may need manual review.",
    )
    verify = st.checkbox(
        "Render Equivalence Check",
        value=True,
        help="Compare normalized render output and flag potential mismatches.",
    )
    strict_verify = st.checkbox(
        "Strict Verification",
        value=False,
        help="If enabled, stop output when mismatch is detected (recommended for final submission).",
    )

    if mode == "aggressive":
        st.warning("Aggressive mode can produce higher savings but may trigger render mismatches.")
    
    all_rules = get_rules(mode)
    st.subheader("Rules Configuration")
    selected_rule_ids: list[str] = []

    preset = st.selectbox(
        "Preset",
        ["all-rules", "custom"],
        help="Select rule preset or customize below",
    )
    if preset == "all-rules":
        selected_rule_ids = [r.id for r in all_rules]
    elif preset == "custom":
        selected_rule_ids = []
    
    if not selected_rule_ids:
        st.write("**Individual Rule Selection:**")
        risk_order = {"low": 0, "medium": 1, "high": 2}
        for rule in sorted(all_rules, key=lambda item: (risk_order.get(item.risk, 99), item.id)):
            risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(rule.risk, "⚪")
            default = rule.risk == "low"
            enabled = st.checkbox(
                f"{risk_color} {rule.id}",
                value=default,
                help=f"{rule.description} (risk: {rule.risk})",
            )
            if enabled:
                selected_rule_ids.append(rule.id)

    st.divider()
    st.header("📊 Sample Data")
    use_sample = st.checkbox("Load sample markdown", value=False)

default_sample = """# Example: Markdown Compression

## Introduction

This   is   a   sample   markdown   file   with   extra   spaces.

| Column A | Column B |
| -------- | -------- |
|   A1     |   B1     |
|   A2     |   B2     |

Equation: $\\alpha   +   \\beta   =   \\gamma$

> This   is   a   blockquote   with   many   spaces.
"""

if use_sample:
    original_text = default_sample
else:
    sample_file = st.file_uploader("Or upload a Markdown file", type="md")
    if sample_file:
        original_text = sample_file.getvalue().decode("utf-8-sig")
    else:
        original_text = st.text_area("Original Markdown", value=default_sample, height=350, key="editor")

opts = CompressionOptions(
    mode=mode,
    verify=verify,
    strict_verify=strict_verify,
    enabled_rules=selected_rule_ids if selected_rule_ids else None,
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 Original")
    with st.container(height=320, border=True):
        st.code(original_text, language="markdown", line_numbers=True)
    m_before = len(original_text)
    b_before = len(original_text.encode("utf-8"))
    st.metric("Characters", m_before)
    st.metric("Bytes (UTF-8)", b_before)

if st.button("🚀 Compress!", width="stretch", type="primary"):
    with st.spinner("Compressing..."):
        try:
            result = compress_text(original_text, opts)
            st.session_state.last_result = result
        except Exception as e:
            st.error(f"Error during compression: {e}")
            st.stop()

if "last_result" in st.session_state:
    result = st.session_state.last_result

    with col2:
        st.subheader("✨ Compressed")
        with st.container(height=320, border=True):
            st.code(result.compressed_text, language="markdown", line_numbers=True)
        st.metric("Characters", result.compressed_chars, delta=-result.chars_saved)
        st.metric("Bytes (UTF-8)", result.compressed_bytes, delta=-result.bytes_saved)

    st.divider()

    col_stats_1, col_stats_2, col_stats_3 = st.columns(3)
    with col_stats_1:
        st.metric("Chars Saved", result.chars_saved, help="Absolute character reduction")
    with col_stats_2:
        st.metric("Compression Ratio", f"{result.reduction_ratio:.1%}", help="Relative compression percentage")
    with col_stats_3:
        status = "✅ Pass" if result.verify_passed else "⚠️ Mismatch"
        st.metric("Verification", status, help=result.verify_message)

    st.divider()

    st.subheader("📈 Rule Contribution Report")
    contrib_report = get_contribution_report(result)
    ranked = contrib_report.get_ranked_contributions()

    if ranked:
        contrib_df = []
        for item in ranked:
            contrib_df.append({
                "Rank": item.rank,
                "Rule ID": item.rule_id,
                "Chars Saved": item.chars_saved,
                "% of Total": f"{item.percentage_of_total:.1f}%"
            })
        
        st.dataframe(contrib_df, width="stretch", hide_index=True)

        col_chart_1, col_chart_2 = st.columns(2)
        with col_chart_1:
            import pandas as pd
            df_chart = pd.DataFrame([{"rule": item.rule_id, "saved": item.chars_saved} for item in ranked])
            st.bar_chart(df_chart.set_index("rule")["saved"])
        with col_chart_2:
            st.metric("Top Rule", ranked[0].rule_id, delta=f"{ranked[0].chars_saved} chars")
    else:
        st.info("No compression achieved with current rules.")

    st.divider()

    st.subheader("🎨 Rendering Comparison (Side-by-side)")
    render_original_html, render_compressed_html = _highlight_render_differences(
        result.original_text,
        result.compressed_text,
        enable_highlight=not result.verify_passed,
    )

    col_render_1, col_render_2 = st.columns(2)
    with col_render_1:
        st.caption("Original")
        st.iframe(_to_data_uri(render_original_html), height=420)
    with col_render_2:
        st.caption("Compressed")
        st.iframe(_to_data_uri(render_compressed_html), height=420)

    if not verify:
        st.warning("未进行检查，因为这个是 off。")
    elif result.verify_passed:
        st.info("No render mismatch detected. Highlighting is hidden.")
    else:
        st.warning(
            "Potential render mismatch detected. Red highlights mark visible-text differences.\n"
            ":red[This mismatch is detected by the render-equivalence verifier, and it may not affect the rendered text. Manual review is still required.]"
        )
        st.code(result.verify_message, language="text")

    st.divider()

    st.subheader("💾 Export Results")
    col_export_1, col_export_2, col_export_3 = st.columns(3)

    with col_export_1:
        st.download_button(
            label="📥 Download Compressed MD",
            data=result.compressed_text,
            file_name="compressed.md",
            mime="text/markdown"
        )

    with col_export_2:
        import json
        report_json = json.dumps({
            "original_chars": result.original_chars,
            "compressed_chars": result.compressed_chars,
            "chars_saved": result.chars_saved,
            "reduction_ratio": result.reduction_ratio,
            "verify_passed": result.verify_passed
        }, ensure_ascii=False, indent=2)
        st.download_button(
            label="📊 Download Report (JSON)",
            data=report_json,
            file_name="report.json",
            mime="application/json"
        )

    with col_export_3:
        st.download_button(
            label="📋 Download Contribution Report",
            data=json.dumps(contrib_report.to_dict(), ensure_ascii=False, indent=2),
            file_name="contribution.json",
            mime="application/json"
        )

    st.info("Use the copy icon on the compressed preview above to copy the compressed text. The browser blocks direct clipboard access from a normal Streamlit button.")

