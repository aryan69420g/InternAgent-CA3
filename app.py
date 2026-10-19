from __future__ import annotations

import json
import pandas as pd
import plotly.express as px
import streamlit as st

from agent_workflow import (
    DOMAIN_OPTIONS, LOCATION_OPTIONS, SKILL_OPTIONS, WORK_MODE_OPTIONS,
    StudentProfile, load_internships, run_workflow, to_display_records,
)

st.set_page_config(page_title="InternAgent | CA-3 PoC", page_icon="🎯", layout="wide")

st.markdown("""
<style>
:root { --navy:#12243A; --blue:#3F73F1; --teal:#15A897; --muted:#62728A; }
.block-container {padding-top:1.4rem; padding-bottom:2rem; max-width: 1400px;}
.hero { padding: 1.5rem 1.8rem; border-radius: 18px; background: linear-gradient(120deg,#12243A 0%,#223F65 68%,#2A7778 100%); color: white; margin-bottom: 1.15rem; }
.hero h1 {font-size:2.1rem; margin:0 0 .35rem 0; color:white; letter-spacing:-.03em;}
.hero p {margin:0; color:#D9E5F5; font-size:1rem;}
.small-label {color:#62728A; font-size:.82rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700;}
.agent-card {border:1px solid #E3E9F2; border-radius:14px; padding:14px 16px; height:100%; background:#FFFFFF;}
.agent-title {font-weight:700; color:#12243A; font-size:1rem; margin-bottom:5px;}
.agent-desc {font-size:.88rem; color:#62728A; line-height:1.4;}
.metric-note {font-size:.78rem; color:#62728A;}
.footnote {font-size:.78rem; color:#62728A; border-top:1px solid #E3E9F2; padding-top:12px; margin-top:22px;}
[data-testid="stMetric"] {border:1px solid #E3E9F2; border-radius:12px; padding:10px 12px; background:#FBFCFE;}
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
    st.caption("Use a synthetic profile for the classroom demo. No personal records are sent anywhere.")
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
            year=year, cgpa=cgpa, skills=skills, interests=interests,
            preferred_location=location, preferred_work_mode=work_mode,
            min_stipend=min_stipend, top_k=top_k,
        )
        with st.spinner("Agents are planning, researching, matching, and validating..."):
            st.session_state.workflow_result = run_workflow(profile)
    except Exception as exc:
        st.session_state.workflow_result = {"error": str(exc)}

result = st.session_state.workflow_result
if not result:
    st.info("Complete or keep the sample student profile in the sidebar, then click **Run agent workflow** to start the agents.")
    sample = load_internships()
    c1, c2, c3 = st.columns(3)
    c1.metric("Synthetic opportunities", len(sample))
    c2.metric("Agent stages", "4")
    c3.metric("External API calls", "0")
    st.markdown("### Agent team")
    cols = st.columns(4)
    agent_summary = [
        ("🧭 Planner Agent", "Creates a sequenced plan for research, screening, matching, and validation."),
        ("🔎 Research Agent", "Searches the synthetic internship dataset and applies the minimum-stipend filter."),
        ("🎯 Matching Agent", "Checks academic eligibility and ranks suitable roles with an explainable score."),
        ("🛡️ Critic Agent", "Independently checks scores, eligibility, ranking, duplicate IDs, and top-k count."),
    ]
    for col, (title, desc) in zip(cols, agent_summary):
        with col:
            st.markdown(f'<div class="agent-card"><div class="agent-title">{title}</div><div class="agent-desc">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("### Architecture")
    st.image("docs/architecture.png", use_container_width=True)
    st.caption("All internship records are fictional sample data for the CA-3 demonstration.")
    st.stop()

if "error" in result:
    st.error(f"Workflow failed: {result['error']}")
    st.stop()

summary = result.get("summary", {})
recommendations = result.get("recommendations", [])
validation = result.get("validation", {})

m1, m2, m3, m4 = st.columns(4)
m1.metric("Source opportunities", summary.get("source_count", 0))
m2.metric("Eligible opportunities", summary.get("eligible_count", 0))
m3.metric("Recommendations returned", len(recommendations))
m4.metric("Critic checks", f"{validation.get('checks_passed', 0)}/{validation.get('checks_total', 0)}")

st.markdown("## 🏆 Recommended internships")
if recommendations:
    df = pd.DataFrame(to_display_records(recommendations))
    if "match_score" in df.columns:
        fig = px.bar(df, x="match_score", y="role", orientation="h", color="match_score", range_color=(0, 100),
                     labels={"match_score": "Match score", "role": "Internship role"}, title="Explainable match scores")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    for i, item in enumerate(recommendations, 1):
        with st.expander(f"#{i} · {item.get('role', 'Internship')} — {item.get('match_score', 0):.1f}% match", expanded=(i == 1)):
            left, right = st.columns([2, 1])
            with left:
                st.markdown(f"**Organization:** {item.get('company', '—')} (fictional demo data)")
                st.markdown(f"**Domain:** {item.get('domain', '—')} · **Location:** {item.get('location', '—')} · **Mode:** {item.get('work_mode', '—')}")
                st.markdown(f"**Stipend:** ₹{item.get('stipend', 0):,}/month · **Duration:** {item.get('duration_months', '—')} months")
                st.markdown("**Skill gaps to work on:** " + (", ".join(item.get("missing_skills", [])) or "None identified"))
                st.caption(item.get("explanation", ""))
            with right:
                st.metric("Match score", f"{item.get('match_score', 0):.1f}%")
                st.metric("Eligibility", "PASS" if item.get("eligible", False) else "FAIL")
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download recommendations (CSV)", csv_data, "internagent_recommendations.csv", "text/csv")
    st.download_button("Download full workflow result (JSON)", json.dumps(result, indent=2, ensure_ascii=False, default=str),
                       "internagent_workflow_result.json", "application/json")
else:
    st.warning("No internship matched these profile filters. Try lowering the minimum stipend or adjusting profile preferences.")

st.markdown("## 🧭 Agent execution trace")
for step in result.get("trace", []):
    with st.expander(f"{step.get('agent', 'Agent')} · {step.get('status', 'complete')}", expanded=False):
        st.write(step.get("summary", ""))
        if step.get("details"):
            st.json(step["details"])

st.markdown("## 🛡️ Critic validation")
if validation.get("passed", False):
    st.success("All critic validation checks passed. Recommendations are ready to display.")
else:
    st.error("Critic validation identified issues. Review the checks and workflow trace before relying on the recommendations.")
for check in validation.get("checks", []):
    label = check.get("name", "Validation check")
    detail = check.get("details", "")
    if check.get("passed", False):
        st.write(f"✅ **{label}:** {detail}")
    else:
        st.write(f"❌ **{label}:** {detail}")

with st.expander("Eligibility watchlist: why some roles were excluded"):
    exclusions = result.get("excluded", [])
    if exclusions:
        st.dataframe(pd.DataFrame(exclusions), use_container_width=True, hide_index=True)
    else:
        st.caption("No roles were excluded after the current filter settings.")

st.markdown('<div class="footnote">CA-3 academic proof of concept · synthetic data only · not a live job board and not an automated hiring decision.</div>', unsafe_allow_html=True)
