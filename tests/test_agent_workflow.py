import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from agent_workflow import StudentProfile, load_internships, run_workflow, eligibility_check  # noqa: E402


class InternAgentWorkflowTests(unittest.TestCase):
    def test_dataset_loads_and_ids_are_unique(self):
        data = load_internships()
        self.assertEqual(len(data), 12)
        self.assertFalse(data["internship_id"].duplicated().any())

    def test_standard_profile_passes_critic(self):
        profile = StudentProfile(
            year=2, cgpa=7.5,
            skills=["Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL"],
            interests=["AI/ML", "Data Science"], preferred_location="Pune",
            preferred_work_mode="Any", min_stipend=5000, top_k=3,
        )
        result = run_workflow(profile)
        self.assertTrue(result["validation"]["valid"], result["validation"]["issues"])
        self.assertLessEqual(len(result["recommendations"]), 3)
        self.assertTrue(all(row["eligible"] for row in result["recommendations"]))
        scores = [row["match_score"] for row in result["recommendations"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_ineligible_roles_never_get_recommended(self):
        profile = StudentProfile(
            year=1, cgpa=5.5, skills=["Python"], interests=["AI/ML"],
            preferred_location="Pune", min_stipend=0, top_k=5,
        )
        result = run_workflow(profile)
        self.assertTrue(all(row["eligible"] for row in result["recommendations"]))
        self.assertGreater(len(result["ineligible"]), 0)
        for row in result["ineligible"]:
            self.assertTrue(row["eligibility_blockers"])

    def test_minimum_stipend_is_applied_by_research_stage(self):
        profile = StudentProfile(
            year=3, cgpa=9.0, skills=["Python", "SQL"], interests=["Data Science"],
            preferred_location="Any", min_stipend=13000, top_k=5,
        )
        result = run_workflow(profile)
        self.assertEqual(result["metadata"]["candidate_records"], 2)
        self.assertTrue(all(row["stipend_inr"] >= 13000 for row in result["assessed"]))

    def test_eligibility_reports_cgpa_and_year_blockers(self):
        data = load_internships()
        row = data[data["internship_id"] == "IA012"].iloc[0].to_dict()
        eligible, blockers = eligibility_check(row, StudentProfile(year=2, cgpa=6.0, skills=[], interests=[]))
        self.assertFalse(eligible)
        self.assertEqual(len(blockers), 2)

    def test_all_scores_are_in_range(self):
        profile = StudentProfile(year=3, cgpa=8.3, skills=["Python", "NLP", "SQL"], interests=["NLP"])
        result = run_workflow(profile)
        self.assertTrue(all(0 <= row["match_score"] <= 100 for row in result["assessed"]))
        self.assertTrue(result["validation"]["valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
