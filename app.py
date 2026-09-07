import streamlit as st
import subprocess
import json
import glob
import os

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MarketMind AI")
st.subheader("Autonomous Business Research Agent")

request = st.text_area(
    "Research Request",
    value="Research the market for AI-powered customer support software and prepare a business intelligence report.",
    height=120
)

if st.button("🚀 Run Research", type="primary"):

    if not request.strip():
        st.error("Please enter a research request.")
        st.stop()

    st.info("MarketMind is researching...")

    result = subprocess.run(
        [
            "python",
            "-m",
            "src.main",
            "--request",
            request
        ],
        capture_output=True,
        text=True
    )

    st.code(result.stdout)

    if result.returncode != 0:
        st.error("Research run failed.")
        st.code(result.stderr)
        st.stop()

    reports = glob.glob("runs/*/report.json")

    if not reports:
        st.error("No report was generated.")
        st.stop()

    report_path = max(
        reports,
        key=os.path.getmtime
    )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    st.success("Research completed!")

    st.header("📌 Executive Summary")
    st.write(report["executive_summary"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Market Findings",
        len(report["market_overview"])
    )

    col2.metric(
        "Trends",
        len(report["key_trends"])
    )

    col3.metric(
        "Opportunities",
        len(report["opportunities"])
    )

    col4.metric(
        "Risks",
        len(report["risks"])
    )

    st.header("📈 Market Overview")

    for finding in report["market_overview"]:
        st.write("•", finding["statement"])

    st.header("🔥 Key Trends")

    for finding in report["key_trends"]:
        st.write("•", finding["statement"])

    st.header("💡 Opportunities")

    for finding in report["opportunities"]:
        st.write("•", finding["statement"])

    st.header("⚠️ Risks")

    for finding in report["risks"]:
        st.write("•", finding["statement"])

    st.header("🎯 Recommendations")

    for finding in report["recommendations"]:
        st.write("•", finding["statement"])

    st.header("🔍 Limitations & Evidence Gaps")

    for limitation in report["limitations_and_gaps"]:
        st.write("•", limitation)

    st.header("📚 Evidence")

    st.json(report["evidence_appendix"])

    st.header("📊 Run Information")

    st.write(
        f"**Confidence:** {report['confidence_level']}"
    )

    st.write(
        f"**Run Cost:** ${report['run_cost']:.6f}"
    )

    with open(report_path, "rb") as f:
        st.download_button(
            "⬇️ Download Full Report",
            f,
            file_name="marketmind_report.json",
            mime="application/json"
        )