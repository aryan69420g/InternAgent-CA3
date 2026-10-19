# InternAgent — 5-minute presentation script

Target: **4:40–4:55 minutes**. Speak naturally; do not read every line.

## Slide 1 — Title (0:00–0:20)
“Good morning. Our project is InternAgent, an Agentic AI proof of concept in education and career development. It helps students go from a profile to ranked internship recommendations, checks eligibility, and validates its own outputs. It uses Python and Streamlit, a synthetic dataset, and no paid API.”

## Slide 2 — Problem (0:20–0:55)
“Students manually compare listings, interpret academic requirements, and work out which skills they are missing. This is repetitive and easy to get wrong. InternAgent automates retrieval, eligibility checking, ranking, explanation, and validation.”

## Slide 3 — Architecture (0:55–1:45)
“The Planner creates a task list. The Research Agent reads our synthetic CSV and applies a minimum-stipend filter. The Matching Agent checks academic-year and CGPA eligibility and calculates fit. The Critic independently recomputes scores and checks eligibility, unique IDs, range, sort order, and result count. The orchestrator passes structured outputs between stages and allows one repair/revalidation pass.”

## Slide 4 — Agent responsibilities (1:45–2:30)
“These are actual functional stages with defined inputs and outputs, not just chatbot labels. Eligibility and ranking are separate: year and minimum CGPA are hard gates, while skill overlap affects the match score. The score weights skills at 55%, domain interest at 20%, location and work mode at 10%, and CGPA buffer at 15%.”

## Slide 5 — Demo (2:30–3:40)
“I’ll use the default synthetic profile: year two, CGPA 7.5, Python, Machine Learning, Pandas, Scikit-learn and SQL, and interests in AI/ML and Data Science. The app produces up to three recommendations and shows the score breakdown, skill gaps, stipend and duration. The Critic reports five out of five checks. Scores are rule-based fit scores, not hiring probabilities.”

Demo sequence: enter/keep profile → click **Run agent workflow** → show ranked score chart → expand a recommendation → show Critic checks and execution trace → show excluded roles and download options.

## Slide 6 — Reliability (3:40–4:25)
“The Critic checks unique IDs, eligibility, score bounds and independent recomputation, descending order and top-k count. Six automated unit tests cover dataset sanity, score ranges, eligibility failures, sorting and stipend filtering.”

## Slide 7 — Limitations and close (4:25–4:55)
“The main limitations are the synthetic dataset, exact label matching and simplified eligibility rules. Future scope includes verified listings, semantic matching, LangGraph, optional local-model explanations and application tracking. The key point is that agentic behaviour comes from planning, tool use, decision rules and verification—not merely adding a chat box. Thank you.”

---

# Likely viva questions

**1. Why is this Agentic AI instead of a chatbot?**  
It has planning, tool execution, eligibility-based decisions, structured handoffs and an independent Critic Agent.

**2. Are these real internships?**  
No. The 12 entries and company names are synthetic demo data.

**3. What makes the system autonomous?**  
The orchestrator runs the stages without the user manually performing each subtask, within explicit rules and a bounded retry policy.

**4. Why not use an LLM for everything?**  
Eligibility and scoring are business rules, so deterministic functions are more auditable and testable. A local model could later improve explanations without overriding hard constraints.

**5. How is the score calculated?**  
55% required-skill overlap, 20% domain-interest match, 10% location/work-mode fit and 15% academic buffer. Academic-year and CGPA checks are separate.

**6. Why can an eligible student still lack skills?**  
The demo defines eligibility through academic year and minimum CGPA. Skills rank the eligible roles and surface learning gaps.

**7. What does the Critic Agent check?**  
Unique IDs, eligibility rules, score range and independent recomputation, descending ordering, and top-k result count.

**8. How was the project evaluated?**  
Six automated unit tests plus the runtime Critic checks for the sample profile.

**9. What is the biggest limitation?**  
The dataset is synthetic and exact skill labels do not measure skill depth.

**10. How would you extend it?**  
Use verified listing sources, semantic skill matching, LangGraph state orchestration, optional local-model explanations and application tracking.
