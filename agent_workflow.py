"""Deterministic multi-stage agent workflow for the InternAgent CA-3 PoC.

All internship records are synthetic. This module intentionally uses Python
functions as transparent, tool-like agents so the workflow works without a
paid LLM API and is easy to explain and test.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import math
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "internships.csv"

SKILL_OPTIONS = [
    "Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL", "Statistics",
    "Excel", "Power BI", "DSA", "Git", "REST APIs", "Testing", "NLP",
    "Transformers", "PyTorch", "OpenCV", "Deep Learning", "MediaPipe", "Linux",
    "Networking", "Security", "Time Series", "Data Visualization", "A/B Testing",
    "Tableau", "Selenium", "CI/CD", "LLM Evaluation", "Prompt Engineering",
]
DOMAIN_OPTIONS = [
    "AI/ML", "Data Science", "Software Development", "NLP", "Finance",
    "Computer Vision", "Business Intelligence", "Cybersecurity", "IoT Analytics",
    "Product Analytics", "QA Automation", "Generative AI",
]
LOCATION_OPTIONS = ["Pune", "Mumbai", "Bengaluru", "Hyderabad", "Remote", "Any"]
WORK_MODE_OPTIONS = ["Any", "Remote", "Hybrid", "On-site"]


@dataclass
class StudentProfile:
    year: int
    cgpa: float
    skills: list[str]
    interests: list[str]
    preferred_location: str = "Pune"
    preferred_work_mode: str = "Any"
    min_stipend: int = 0
    top_k: int = 3

    def normalized(self) -> "StudentProfile":
        return StudentProfile(
            year=int(self.year),
            cgpa=float(self.cgpa),
            skills=sorted({normalize_text(x) for x in self.skills if normalize_text(x)}),
            interests=sorted({normalize_text(x) for x in self.interests if normalize_text(x)}),
            preferred_location=self.preferred_location or "Any",
            preferred_work_mode=self.preferred_work_mode or "Any",
            min_stipend=max(0, int(self.min_stipend)),
            top_k=max(1, min(5, int(self.top_k))),
        )


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def parse_skills(value: Any) -> list[str]:
    """Parse a semicolon-separated CSV cell into clean skill names."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]


def load_internships(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load and minimally validate the synthetic opportunity dataset."""
    data = pd.read_csv(path)
    required = {
        "internship_id", "company", "role", "domain", "location", "work_mode",
        "stipend_inr", "required_skills", "preferred_skills", "min_year", "max_year",
        "min_cgpa", "duration_weeks",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Internship dataset is missing required columns: {', '.join(sorted(missing))}")
    if data["internship_id"].duplicated().any():
        raise ValueError("Internship IDs must be unique.")
    if (data["min_year"] > data["max_year"]).any():
        raise ValueError("Each internship's minimum year must be <= maximum year.")
    if (data["stipend_inr"] < 0).any() or (data["min_cgpa"] < 0).any() or (data["min_cgpa"] > 10).any():
        raise ValueError("Stipend and CGPA values are outside the supported range.")
    return data.fillna("")


def planner_agent(profile: StudentProfile) -> dict[str, Any]:
    """Turn the user goal into an ordered execution plan."""
    p = profile.normalized()
    tasks = [
        "Interpret student profile and preferences",
        "Retrieve internships that meet the minimum stipend preference",
        "Check year and CGPA eligibility for each opportunity",
        "Score eligible opportunities against skills, interests and preferences",
        "Independently validate eligibility, ranking and score calculations",
    ]
    return {
        "agent": "Planner Agent",
        "goal": "Find suitable internships and explain why each one matches.",
        "tasks": tasks,
        "profile_summary": {
            "year": p.year,
            "cgpa": round(p.cgpa, 2),
            "skills_provided": len(p.skills),
            "interests": p.interests,
            "min_stipend": p.min_stipend,
            "requested_results": p.top_k,
        },
    }


def research_agent(data: pd.DataFrame, profile: StudentProfile) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Retrieve candidate records with a tool-like data operation."""
    p = profile.normalized()
    source_count = len(data)
    candidates = data[data["stipend_inr"].astype(float) >= p.min_stipend].copy()
    log = {
        "agent": "Research Agent",
        "tool": "load_internships() + stipend filter",
        "source_records": int(source_count),
        "candidate_records": int(len(candidates)),
        "filtered_out": int(source_count - len(candidates)),
        "note": "The dataset is synthetic; stipend filtering is a user preference, not an eligibility rule.",
    }
    return candidates.reset_index(drop=True), log


def eligibility_check(row: dict[str, Any], profile: StudentProfile) -> tuple[bool, list[str]]:
    """Check hard eligibility rules only; skills affect ranking, not eligibility."""
    p = profile.normalized()
    blockers: list[str] = []
    min_year = int(float(row["min_year"]))
    max_year = int(float(row["max_year"]))
    min_cgpa = float(row["min_cgpa"])
    if not min_year <= p.year <= max_year:
        blockers.append(f"Requires year {min_year}–{max_year}; your year is {p.year}.")
    if p.cgpa + 1e-9 < min_cgpa:
        blockers.append(f"Requires CGPA {min_cgpa:.1f}; your CGPA is {p.cgpa:.1f}.")
    return not blockers, blockers


def _preference_fit(row: dict[str, Any], profile: StudentProfile) -> tuple[float, float, float]:
    p = profile.normalized()
    location = str(row["location"])
    mode = str(row["work_mode"])
    if p.preferred_location == "Any":
        location_score = 100.0
    elif location == p.preferred_location or mode == "Remote":
        location_score = 100.0
    else:
        location_score = 25.0
    if p.preferred_work_mode == "Any":
        mode_score = 100.0
    elif mode == p.preferred_work_mode:
        mode_score = 100.0
    else:
        mode_score = 35.0
    return location_score, mode_score, (location_score + mode_score) / 2.0


def _skill_details(row: dict[str, Any], profile: StudentProfile) -> tuple[list[str], list[str], float]:
    required = parse_skills(row.get("required_skills", ""))
    student_skills = {normalize_text(s) for s in profile.normalized().skills}
    matching = [skill for skill in required if normalize_text(skill) in student_skills]
    missing = [skill for skill in required if normalize_text(skill) not in student_skills]
    score = 100.0 * len(matching) / max(1, len(required))
    return matching, missing, score


def _score_components(row: dict[str, Any], profile: StudentProfile) -> dict[str, float]:
    p = profile.normalized()
    _, _, skill_score = _skill_details(row, p)
    interests = {normalize_text(x) for x in p.interests}
    interest_score = 100.0 if normalize_text(row["domain"]) in interests else 25.0
    _, _, preference_score = _preference_fit(row, p)
    min_cgpa = float(row["min_cgpa"])
    # Eligibility is checked separately; this component rewards a modest CGPA buffer.
    academic_score = min(100.0, 60.0 + max(0.0, p.cgpa - min_cgpa) * 20.0)
    total = skill_score * 0.55 + interest_score * 0.20 + preference_score * 0.10 + academic_score * 0.15
    return {
        "skill_match": round(skill_score, 2),
        "interest_match": round(interest_score, 2),
        "preference_fit": round(preference_score, 2),
        "academic_fit": round(academic_score, 2),
        "match_score": round(max(0.0, min(100.0, total)), 2),
    }


def matching_agent(candidates: pd.DataFrame, profile: StudentProfile) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply hard gates, then rank candidates with transparent weighted scoring."""
    p = profile.normalized()
    assessed: list[dict[str, Any]] = []
    for _, series in candidates.iterrows():
        row = series.to_dict()
        eligible, blockers = eligibility_check(row, p)
        matching, missing, _ = _skill_details(row, p)
        row.update(_score_components(row, p))
        row["eligible"] = bool(eligible)
        row["eligibility_blockers"] = blockers
        row["matching_skills"] = matching
        row["missing_skills"] = missing
        row["stipend_inr"] = int(float(row["stipend_inr"]))
        row["min_year"] = int(float(row["min_year"]))
        row["max_year"] = int(float(row["max_year"]))
        row["min_cgpa"] = float(row["min_cgpa"])
        assessed.append(row)
    assessed.sort(key=lambda item: (item["eligible"], item["match_score"], item["stipend_inr"]), reverse=True)
    eligible_rows = [r for r in assessed if r["eligible"]]
    log = {
        "agent": "Matching & Eligibility Agent",
        "tool": "eligibility_check() + weighted score function",
        "assessed_records": len(assessed),
        "eligible_records": len(eligible_rows),
        "ineligible_records": len(assessed) - len(eligible_rows),
        "score_formula": "55% required-skill overlap + 20% domain interest + 10% location/work-mode fit + 15% academic buffer",
    }
    return assessed, log


def _critic_recompute_score(row: dict[str, Any], profile: StudentProfile) -> float:
    """Independent implementation used by the Critic Agent for spot-checking.

    It intentionally does not call the Matching Agent's scoring helper.
    """
    p = profile.normalized()
    student_skill_set = {normalize_text(s) for s in p.skills}
    required = parse_skills(row.get("required_skills", ""))
    common = sum(1 for skill in required if normalize_text(skill) in student_skill_set)
    skill_pct = 100.0 * common / max(1, len(required))
    domain_pct = 100.0 if normalize_text(row.get("domain", "")) in {normalize_text(i) for i in p.interests} else 25.0
    role_mode = str(row.get("work_mode", ""))
    role_location = str(row.get("location", ""))
    loc_pct = 100.0 if p.preferred_location == "Any" or role_location == p.preferred_location or role_mode == "Remote" else 25.0
    mode_pct = 100.0 if p.preferred_work_mode == "Any" or role_mode == p.preferred_work_mode else 35.0
    pref_pct = (loc_pct + mode_pct) / 2.0
    buffer = max(0.0, p.cgpa - float(row["min_cgpa"]))
    academic_pct = min(100.0, 60.0 + buffer * 20.0)
    return round(max(0.0, min(100.0, skill_pct * 0.55 + domain_pct * 0.20 + pref_pct * 0.10 + academic_pct * 0.15)), 2)


def critic_agent(
    assessed: list[dict[str, Any]], recommendations: list[dict[str, Any]], profile: StudentProfile, top_k: int
) -> dict[str, Any]:
    """Independently validate rules, scores, ordering and uniqueness."""
    issues: list[str] = []
    checks: list[dict[str, Any]] = []
    ids = [str(item["internship_id"]) for item in assessed]
    unique_ok = len(ids) == len(set(ids))
    checks.append({"check": "Unique internship IDs", "passed": unique_ok})
    if not unique_ok:
        issues.append("Duplicate internship IDs were found in the assessed results.")

    elig_ok = True
    for item in recommendations:
        should_be_eligible, blockers = eligibility_check(item, profile)
        if not should_be_eligible or not bool(item["eligible"]):
            elig_ok = False
            issues.append(f"Ineligible internship {item['internship_id']} appeared in recommendations.")
        if blockers:
            issues.append(f"Eligibility rules disagree for {item['internship_id']}.")
    checks.append({"check": "Recommendations pass year and CGPA rules", "passed": elig_ok})

    score_ok = True
    for item in assessed:
        score = float(item["match_score"])
        if score < 0.0 or score > 100.0:
            score_ok = False
            issues.append(f"Score for {item['internship_id']} is outside 0–100.")
        expected = _critic_recompute_score(item, profile)
        if abs(expected - score) > 0.02:
            score_ok = False
            issues.append(f"Score mismatch for {item['internship_id']}: displayed {score}, recomputed {expected}.")
    checks.append({"check": "Match scores are bounded and independently reproduced", "passed": score_ok})

    sort_ok = all(
        float(recommendations[index]["match_score"]) >= float(recommendations[index + 1]["match_score"])
        for index in range(len(recommendations) - 1)
    )
    checks.append({"check": "Recommendations sorted by descending score", "passed": sort_ok})
    if not sort_ok:
        issues.append("Recommendations are not sorted by descending match score.")

    top_ok = len(recommendations) <= top_k and len(recommendations) == min(top_k, sum(bool(x["eligible"]) for x in assessed))
    checks.append({"check": "Result count respects requested top-k", "passed": top_ok})
    if not top_ok:
        issues.append("Recommendation count does not match the requested top-k policy.")

    return {
        "agent": "Critic / Validation Agent",
        "valid": not issues,
        "checks_passed": sum(bool(c["passed"]) for c in checks),
        "checks_total": len(checks),
        "checks": checks,
        "issues": issues,
        "summary": "All validation checks passed." if not issues else "Validation found issues that require repair.",
    }


def run_workflow(profile: StudentProfile, data_path: str | Path = DEFAULT_DATA_PATH) -> dict[str, Any]:
    """Orchestrate the agents and perform one deterministic repair pass if needed."""
    p = profile.normalized()
    plan = planner_agent(p)
    data = load_internships(data_path)
    candidates, research_log = research_agent(data, p)
    assessed, matching_log = matching_agent(candidates, p)
    eligible = [item for item in assessed if item["eligible"]]
    recommendations = eligible[: p.top_k]
    validation = critic_agent(assessed, recommendations, p, p.top_k)
    retries = 0
    if not validation["valid"]:
        # Repair policy: rebuild rows from source data and rerun the transparent matching stage once.
        retries = 1
        assessed, matching_log = matching_agent(candidates, p)
        eligible = [item for item in assessed if item["eligible"]]
        recommendations = eligible[: p.top_k]
        validation = critic_agent(assessed, recommendations, p, p.top_k)
    ineligible = [item for item in assessed if not item["eligible"]]
    execution_log = [
        {"agent": "Planner Agent", "status": "completed", "detail": f"Created {len(plan['tasks'])} ordered tasks."},
        {"agent": "Research Agent", "status": "completed", "detail": f"Retrieved {len(candidates)} of {len(data)} records based on stipend preference."},
        {"agent": "Matching & Eligibility Agent", "status": "completed", "detail": f"Checked {len(assessed)} records; {len(eligible)} pass academic/year rules."},
        {"agent": "Critic / Validation Agent", "status": "passed" if validation["valid"] else "failed", "detail": validation["summary"]},
    ]
    if retries:
        execution_log.insert(-1, {"agent": "Workflow Repair", "status": "completed", "detail": "One repair/revalidation pass was triggered."})
    return {
        "plan": plan,
        "recommendations": recommendations,
        "assessed": assessed,
        "ineligible": ineligible,
        "validation": validation,
        "execution_log": execution_log,
        "metadata": {
            "source_records": int(len(data)),
            "candidate_records": int(len(candidates)),
            "recommendation_count": int(len(recommendations)),
            "eligible_count": int(len(eligible)),
            "ineligible_count": int(len(ineligible)),
            "repair_passes": retries,
        },
        "profile": asdict(p),
    }


def to_display_records(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return compact serializable fields for UI tables and CSV export."""
    out = []
    for row in rows:
        out.append({
            "ID": row["internship_id"],
            "Company": row["company"],
            "Role": row["role"],
            "Domain": row["domain"],
            "Location": f"{row['location']} · {row['work_mode']}",
            "Stipend (₹/month)": int(row["stipend_inr"]),
            "Match score": float(row["match_score"]),
        })
    return out
