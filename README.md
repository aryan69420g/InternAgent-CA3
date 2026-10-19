# InternAgent — Agentic AI Internship Matching & Eligibility Assistant

**CA-3 Proof of Concept | Domain: Education & Career Development**

InternAgent is an explainable, deterministic multi-agent workflow that helps students discover suitable internships from a synthetic dataset. It checks academic eligibility, ranks eligible opportunities with transparent scores, explains skill gaps, and validates recommendations before display.

> **Demo-data notice:** All 12 internship records and company names are fictional. This is not a live internship search service. The app makes no external API calls and needs no paid LLM.

## Project deliverables

- app.py — Streamlit interface, score visualization, agent execution trace and downloads.
- agent_workflow.py — Planner, Research, Matching/Eligibility, Critic and orchestration logic.
- data/internships.csv — 12 fictional opportunities and eligibility requirements.
- tests/test_agent_workflow.py — six automated tests.
- docs/architecture.md — editable Mermaid architecture diagram.
- CA3_Agentic_AI_Presentation.pptx — seven-slide presentation for a five-minute demo.
- CA3_Technical_Report.docx — editable technical report.
- PRESENTER_NOTES.md — talk track and viva questions.
- PROJECT_BRIEF.md — problem statement, domain justification, solution and evaluation.
- .github/workflows/tests.yml — GitHub Actions test workflow.

## Run locally

Use Python 3.10+ (Python 3.11 recommended).

### Windows PowerShell

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    streamlit run app.py

### macOS / Linux

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    streamlit run app.py

Open the local URL shown by Streamlit, usually http://localhost:8501. Keep the default profile for the first demonstration and click **Run agent workflow**.

## Run tests

    python -m unittest discover -s tests -v

The workflow tests do not require the Streamlit UI to be launched.

## Agent roles

| Stage | Responsibility | Tool / output |
|---|---|---|
| Planner Agent | Converts the request into an ordered execution plan. | Structured task plan |
| Research Agent | Loads the synthetic CSV and applies the requested minimum-stipend preference. | Pandas CSV read and filter |
| Matching & Eligibility Agent | Applies academic-year and CGPA constraints, computes a weighted score, and identifies skill gaps. | Rule-based Python functions |
| Critic / Validation Agent | Independently recomputes scores and checks eligibility, order, unique IDs and top-k result count. | Independent verification checks |
| Orchestrator | Passes structured data between stages and performs one repair/revalidation pass if validation fails. | run_workflow() |

The agents are distinct functional stages with explicit inputs, outputs and checks. The PoC uses deterministic Python functions so its decisions are auditable and testable without paid APIs.

## Score and eligibility

Eligibility is a hard gate: students must satisfy the role's academic-year range and minimum CGPA. Skills influence ranking, not eligibility.

The weighted match score comprises:
- 55% required-skill overlap
- 20% domain-interest alignment
- 10% location and work-mode fit
- 15% CGPA buffer above the role minimum

The score is clamped to 0–100. The Critic validates unique IDs, eligibility, score bounds and independent recomputation, descending ranking, and top-k count.

## Demo scenario

The default profile is Year 2, CGPA 7.5, with Python, Machine Learning, Pandas, Scikit-learn and SQL skills; AI/ML and Data Science interests; Pune preference; and a ₹5,000 minimum stipend.

During the demonstration, show the planner tasks, source filtering, top recommendations with score explanations, the Critic's validation report, excluded roles and the CSV/JSON downloads.

## Limitations and future scope

The dataset is synthetic and small. Skill matching uses normalized labels and does not estimate skill depth. Eligibility rules are simplified and do not reflect all employer policies. Future versions could use verified live listings, semantic skill matching, LangGraph orchestration, an optional local Ollama model for explanations, and application tracking.

Repository: https://github.com/aryan69420g/InternAgent-CA3
