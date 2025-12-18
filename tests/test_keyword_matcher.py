import os
import sys

sys.path.append(os.path.abspath("backend"))

from services.keyword_matcher import KeywordMatcher  # noqa: E402


def test_overqualification_boosts_score():
    matcher = KeywordMatcher()
    resume_path = os.path.join("tests", "fixtures", "resume_overqualified.txt")
    jd_path = os.path.join("tests", "fixtures", "jd_hybrid.txt")
    with open(resume_path, "r", encoding="utf-8") as f:
        resume = f.read()
    with open(jd_path, "r", encoding="utf-8") as f:
        jd = f.read()

    result = matcher.evaluate(resume_text=resume, job_description=jd, intern_level="freshman")

    assert result["score"] >= 95
    assert "missing_keywords" in result


def test_recency_and_impact_boosts():
    matcher = KeywordMatcher()
    resume = "2024 - improved latency by 25% and added tests. git, debugging, unit tests."
    jd = "backend engineer intern working on APIs and testing."

    result = matcher.evaluate(resume_text=resume, job_description=jd, intern_level="junior")

    # Recency + impact bumps should push score above baseline coverage.
    assert result["score"] >= 70
