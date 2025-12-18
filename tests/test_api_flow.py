import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("backend"))

from main import app  # noqa: E402


client = TestClient(app)


def test_evaluate_endpoint_returns_scores():
    payload = {
        "job_title": "Backend Engineer",
        "job_description": "Build APIs, write tests, collaborate with product, hybrid role",
        "resume_text": "Built APIs with tests and debugging. Collaborated with team and Git.",
        "intern_level": "junior",
    }
    response = client.post("/evaluate/", data=payload)
    assert response.status_code == 200
    body = response.json()
    assert "scores" in body
    assert "keyword_matches" in body
    assert "quality_gates" in body


def test_job_templates_endpoint_includes_levels():
    response = client.get("/evaluate/job-templates")
    assert response.status_code == 200
    data = response.json()
    templates = data.get("templates", {})
    assert "software_engineer" in templates
    assert "levels" in templates["software_engineer"]
