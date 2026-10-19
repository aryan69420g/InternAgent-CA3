# InternAgent architecture

Diagram (Mermaid):

    flowchart TD
      A[Student Profile in Streamlit] --> B[Planner Agent]
      B --> C[Research Agent]
      C --> D[Read Synthetic CSV and Apply Stipend Filter]
      D --> E[Matching and Eligibility Agent]
      E --> F{Year and CGPA Eligible?}
      F -->|No| G[Eligibility Watchlist]
      F -->|Yes| H[Weighted Match Score and Skill Gaps]
      H --> I[Critic / Validation Agent]
      I --> J{Checks Pass?}
      J -->|No| K[One Repair and Revalidation Pass]
      K --> I
      J -->|Yes| L[Ranked Recommendations]
      L --> M[Streamlit Dashboard, Trace, CSV / JSON Exports]

## Data flow

1. Streamlit captures an academic profile and preferences.
2. The Planner Agent produces a sequence of tasks.
3. The Research Agent loads the synthetic internship CSV and filters by requested minimum stipend.
4. The Matching & Eligibility Agent applies academic year and minimum-CGPA rules, computes a transparent score and reports skill gaps.
5. The Critic Agent independently recomputes scores and verifies unique IDs, eligibility, bounds, descending rank, and requested result count.
6. If checks fail, the orchestrator attempts one repair/revalidation pass. Validated recommendations appear in the UI; academically ineligible opportunities remain in the watchlist.

All sample data are fictional. The application uses no paid AI API.
