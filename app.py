from __future__ import annotations

import json
import pandas as pd
import plotly.express as px
import streamlit as st

from agent_workflow import (
    DOMAIN_OPTIONS,
    LOCATION_OPTIONS,
    SKILL_OPTIONS,
    WORK_MODE_OPTIONS,
    StudentProfile,
    load_internships,
    run_workflow,
    to_display_records,
)

st.set_page_config(page_title="InternAgent | CA-3 PoC", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1.4rem; padding-bottom:2rem; max-width:1400px;}
.hero {padding:1.5rem 1.8rem; border-radius:18px; background:linear-gradient(120deg,#12243A 0%,#223F65 68%,#2A7778 100%); color:white; margin-bottom:1.15rem;}
.hero h1 {font-size:2.1rem; margin:0 0 .35rem 0; color:white; letter-spacing:-.03em;}
.hero p {margin:0; color:#D9E5F5; font-size:1rem;}
.agent-card {border:1px solid #E3E9F2; border-radius:14px; padding:14px 16px; height:100%; background:#FFFFFF;}
.agent-title {font-weight:700; color:#12243A; font-size:1rem; margin-bottom:5px;}
.agent-desc {font-size:.88rem; color:#62728A; line-height:1.4;}
[data-testid="stMetric"] {border:1px solid #E3E9F2; border-radius:12px; padding:10px 12px; background:#FBFCFE;}
.footnote {font-size:.78rem; color:#62728A; border-top:1px solid #E3E9F2; padding-top:12px; margin-top:22px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#9DE5DA;font-weight:700;margin-bottom:8px;">CA-3 · Agentic AI Proof of Concept</div>
  <h1>🎯 InternAgent</h1>
  <p>An explainable multi-agent workflow to match students with internship opportunities, check eligibility, and validate recommendations.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 👤 Student profile")
    st.caption("Use a synthetic profile for this classroom demo. No profile data is sent to external services.")
    with st.form("profile_form"):
        year = st.selectbox("Current academic year", [1, 2, 3, 4], index=1)
        cgpa = st.slider("Current CGPA", 5.0, 10.0, 7.5, 0.1)
        skills = st.multiselect(
            "Skills you have", SKILL_OPTIONS,
            default=["Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL"],
        )
        interests = st.multiselect(
            "Domains of interest", DOMAIN_OPTIONS,
            default=["AI/ML", "Data Science"],
        )
        location = st.selectbox("Preferred location", LOCATION_OPTIONS, index=0)
        work_mode = st.selectbox("Preferred work mode", WORK_MODE_OPTIONS, index=0)
        min_stipend = st.slider("Minimum monthly stipend (₹)", 0, 30000, 5000, 1000)
        top_k = st.selectbox("Recommendations to show", [1, 2, 3, 4, 5], index=2)
        submitted = st.form_submit_button("Run agent workflow", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("**Scoring logic**")
    st.caption("55% required-skill overlap · 20% domain interest · 10% location/work-mode fit · 15% academic buffer")
    st.caption("Eligibility is a separate hard gate: academic year and minimum CGPA.")

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

if submitted:
    try:
        profile = StudentProfile(
            year=year,
            cgpa=cgpa,
            skills=skills,
            interests=interests,
            preferred_location=location,
            preferred_work_mode=work_mode,
            min_stipend=min_stipend,
            top_k=top_k,
        )
        with st.spinner("Agents are planning, researching, matching, and validating..."):
            st.session_state.workflow_result = run_workflow(profile)
    except Exception as exc:
        st.session_state.workflow_result = {"error": str(exc)}

result = st.session_state.workflow_result
if not result:
    sample = load_internships()
    c1, c2, c3 = st.columns(3)
    c1.metric("Synthetic opportunities", len(sample))
    c2.metric("Agent stages", 4)
    c3.metric("External API calls", 0)
    st.info("Keep the sample profile or adjust it in the sidebar, then click **Run agent workflow**.")
    st.markdown("### Agent team")
    cols = st.columns(4)
    agent_summary = [
        ("🧭 Planner Agent", "Breaks the request into ordered tasks."),
        ("🔎 Research Agent", "Retrieves synthetic listings and applies the stipend preference."),
        ("🎯 Matching & Eligibility Agent", "Applies academic rules, calculates fit scores, and identifies skill gaps."),
        ("🛡️ Critic Agent", "Rechecks eligibility, scores, ordering, unique IDs, and result count."),
    ]
    for col, (title, desc) in zip(cols, agent_summary):
        with col:
            st.markdown(
                f'<div class="agent-card"><div class="agent-title">{title}</div><div class="agent-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("### Architecture")
    st.image("docs/architecture.png", use_container_width=True)
    st.caption("All internship listings and company names are fictional, for demonstration only.")
    st.stop()

if "error" in result:
    st.error(f"Workflow failed: {result['error']}")
    st.stop()

metadata = result.get("metadata", {})
recommendations = result.get("recommendations", [])
validation = result.get("validation", {})

m1, m2, m3, m4 = st.columns(4)
m1.metric("Source opportunities", metadata.get("source_records", 0))
m2.metric("Eligible opportunities", metadata.get("eligible_count", 0))
m3.metric("Recommendations", len(recommendations))
m4.metric("Critic checks", f"{validation.get('checks_passed', 0)}/{validation.get('checks_total', 0)}")

st.markdown("## 🏆 Recommended internships")
if recommendations:
    chart_df = pd.DataFrame([
        {"Role": item["role"], "Match score": float(item["match_score"])}
        for item in recommendations
    ])
    fig = px.bar(
        chart_df, x="Match score", y="Role", orientation="h",
        range_x=[0, 100], text="Match score", title="Explainable match scores",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

    for index, item in enumerate(recommendations, 1):
        with st.expander(f"#{index} · {item['role']} — {item['match_score']:.1f}% match", expanded=index == 1):
            left, right = st.columns([2, 1])
            with left:
                st.markdown(f"**Organization:** {item['company']} *(fictional sample data)*")
                st.markdown(f"**Domain:** {item['domain']} · **Location:** {item['location']} · **Mode:** {item['work_mode']}")
                st.markdown(f"**Stipend:** ₹{int(item['stipend_inr']):,}/month · **Duration:** {item['duration_weeks']} weeks")
                st.markdown("**Skills matched:** " + (", ".join(item["matching_skills"]) or "No required skills matched yet"))
                st.markdown("**Skill gaps to work on:** " + (", ".join(item["missing_skills"]) or "None identified"))
                st.caption(
                    "Score components — "
                    f"skills {item['skill_match']:.1f}% · domain {item['interest_match']:.1f}% · "
                    f"preferences {item['preference_fit']:.1f}% · academic buffer {item['academic_fit']:.1f}%"
                )
            with right:
                st.metric("Match score", f"{item['match_score']:.1f}%")
                st.metric("Eligibility", "PASS" if item["eligible"] else "FAIL")

    export_df = pd.DataFrame(to_display_records(recommendations))
    st.download_button(
        "Download recommendations (CSV)",
        export_df.to_csv(index=False).encode("utf-8"),
        "internagent_recommendations.csv",
        "text/csv",
    )
    st.download_button(
        "Download workflow result (JSON)",
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        "internagent_workflow_result.json",
        "application/json",
    )
else:
    st.warning("No internship matched the current filters. Try lowering the minimum stipend or adjusting the profile.")

st.markdown("## 🧭 Agent execution trace")
for step in result.get("execution_log", []):
    with st.expander(f"{step.get('agent', 'Agent')} · {step.get('status', 'complete')}"):
        st.write(step.get("detail", ""))

st.markdown("## 🛡️ Critic validation")
if validation.get("valid", False):
    st.success("All critic validation checks passed. Recommendations are ready to display.")
else:
    st.error("The Critic Agent identified issues. Inspect the checks before relying on recommendations.")
for check in validation.get("checks", []):
    label = check.get("check", "Validation check")
    status = "✅" if check.get("passed", False) else "❌"
    st.write(f"{status} **{label}**")

with st.expander("Eligibility watchlist: why roles were excluded"):
    exclusions = result.get("ineligible", [])
    if exclusions:
        exclusion_rows = [
            {
                "ID": row["internship_id"],
                "Company": row["company"],
                "Role": row["role"],
                "Required year": f"{row['min_year']}–{row['max_year']}",
                "Minimum CGPA": row["min_cgpa"],
                "Reason": " ".join(row["eligibility_blockers"]),
            }
            for row in exclusions
        ]
        st.dataframe(pd.DataFrame(exclusion_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No roles were excluded by the academic eligibility rules.")

st.markdown(
    '<div class="footnote">CA-3 academic proof of concept · synthetic data only · not a live job board or automated hiring decision.</div>',
    unsafe_allow_html=True,
)
