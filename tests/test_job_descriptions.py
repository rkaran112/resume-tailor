from fastapi.testclient import TestClient


def test_create_job_description_extracts_keywords(client: TestClient) -> None:
    resp = client.post(
        "/api/job-descriptions",
        json={
            "company": "Acme Corp",
            "role_title": "Backend Engineer",
            "raw_text": "We need a Python engineer with strong SQL skills.",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["company"] == "Acme Corp"
    assert "python" in body["extracted_keywords"]
    assert "sql" in body["extracted_keywords"]


def test_list_and_get_job_description(client: TestClient) -> None:
    resp = client.post(
        "/api/job-descriptions",
        json={"company": "Acme", "role_title": "Engineer", "raw_text": "Python required."},
    )
    jd_id = resp.json()["id"]

    resp = client.get("/api/job-descriptions")
    assert resp.status_code == 200
    assert any(jd["id"] == jd_id for jd in resp.json())

    resp = client.get(f"/api/job-descriptions/{jd_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == jd_id


def test_get_missing_job_description_404(client: TestClient) -> None:
    resp = client.get("/api/job-descriptions/999999")
    assert resp.status_code == 404


def test_match_selects_content_relevant_to_jd(client: TestClient) -> None:
    exp_resp = client.post(
        "/api/experience-entries",
        json={
            "company": "Acme Corp",
            "title": "Engineer",
            "location": "Remote",
            "start_date": "2022-01-01",
        },
    )
    experience_entry_id = exp_resp.json()["id"]

    client.post(
        "/api/bullets",
        json={
            "experience_entry_id": experience_entry_id,
            "text": "Built Python APIs",
            "tags": ["python"],
        },
    )
    client.post(
        "/api/bullets",
        json={
            "experience_entry_id": experience_entry_id,
            "text": "Organized team lunches",
            "tags": [],
        },
    )

    python_skill_resp = client.post(
        "/api/skills", json={"name": "Python", "category": "language", "tags": ["backend"]}
    )
    client.post("/api/skills", json={"name": "Excel", "category": "tool", "tags": []})

    project_resp = client.post(
        "/api/projects",
        json={"name": "API Service", "description": "A Python backend", "tech_tags": ["python"]},
    )
    client.post(
        "/api/projects",
        json={"name": "Recipe Blog", "description": "A cooking blog", "tech_tags": ["wordpress"]},
    )

    client.post(
        "/api/education-entries",
        json={
            "institution": "State U",
            "degree": "B.S.",
            "field": "CS",
            "start_date": "2018-01-01",
        },
    )

    jd_resp = client.post(
        "/api/job-descriptions",
        json={
            "company": "Acme",
            "role_title": "Engineer",
            "raw_text": "Looking for a Python engineer.",
        },
    )
    jd_id = jd_resp.json()["id"]

    resp = client.post(
        f"/api/job-descriptions/{jd_id}/match",
        json={"bullets_per_experience_entry": 1, "max_skills": 1, "max_projects": 1},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["selected_skill_ids"] == [python_skill_resp.json()["id"]]
    assert body["selected_project_ids"] == [project_resp.json()["id"]]
    assert len(body["selected_experience_bullet_ids"]) == 1
    assert len(body["selected_education_ids"]) == 1
    assert "python" in body["scoring_metadata"]["skills"][str(python_skill_resp.json()["id"])]


def test_match_missing_job_description_404(client: TestClient) -> None:
    resp = client.post("/api/job-descriptions/999999/match", json={})
    assert resp.status_code == 404
