# CA-3 Project Brief: InternAgent

## Project title
**InternAgent: Agentic AI Internship Matching and Eligibility Assistant**

## Domain and justification
**Domain:** Education and career development.

Students compare internships across eligibility constraints, skills, location, stipend and expected duration. This can be repetitive and error-prone. The task suits an Agentic AI proof of concept because it decomposes into planning, retrieval, rule-based decisions and independent validation.

## Problem statement
Students need to find internships relevant to their skills and goals, verify academic eligibility and determine missing qualifications. InternAgent accepts a student profile, retrieves candidate listings from a synthetic dataset, checks academic eligibility, ranks roles, explains the score and validates the output before displaying it.

## Existing challenge
- Manual comparison of internship listings is time-consuming.
- Eligibility criteria may be overlooked.
- Rankings without explanations are difficult to trust.
- Students may not know which required skills they are missing.
- A plain chatbot response does not demonstrate a structured and auditable workflow.

## Proposed solution
1. **Planner Agent:** creates an ordered task plan.
2. **Research Agent:** loads the synthetic CSV and filters by minimum stipend.
3. **Matching & Eligibility Agent:** enforces year and CGPA rules, ranks roles and surfaces skill gaps.
4. **Critic / Validation Agent:** independently recomputes scores and validates eligibility, ranking, unique IDs and top-k count.
5. **Orchestrator:** runs stages in order and permits one repair/revalidation pass.

The Streamlit UI shows recommendations, score explanations, a validation report, execution trace, ineligible watchlist and CSV/JSON exports.

## Success criteria
- Application launches with Streamlit.
- The agents execute in a defined order.
- Ineligible roles are not recommended.
- Match scores remain between 0 and 100 and are sorted descending.
- Critic checks succeed or report issues.
- Students can inspect skill gaps and eligibility blockers.
- Automated unit tests pass against the synthetic dataset.

## Dataset and privacy
The PoC includes 12 fictional internship listings and company names. It uses no external source, paid API, or live scraping. The workflow runs locally with the profile entered in Streamlit.

## Technology
Python, Streamlit, Pandas, Plotly, CSV and unittest. LangChain, LangGraph, MCP and paid LLM APIs are optional, not required.

## Evaluation evidence
Six unit tests cover dataset sanity, eligibility, score bounds, ranking, stipend filtering and end-to-end validation. The included default Year 2 / CGPA 7.5 profile returns three ranked recommendations with five Critic checks passing.

## Limitations and future scope
The dataset is synthetic and small; skill matching uses exact normalized labels; eligibility rules are simplified. Future work could introduce verified listings, semantic skill matching, an explicit LangGraph state graph, local-model explanations and application tracking.
