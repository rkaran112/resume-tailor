from unittest.mock import patch

from fastapi.testclient import TestClient

from app.services.llm_enhance import EnhancedBullet


def _seed_bank(client: TestClient) -> dict:
    client.put(
        "/api/contact-info",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-1234",
            "location": "Remote",
            "links": [],
        },
    )
    exp = client.post(
        "/api/experience-entries",
        json={
            "company": "Acme Corp",
            "title": "Engineer",
            "location": "Remote",
            "start_date": "2022-01-01",
        },
    ).json()
    bullet = client.post(
        "/api/bullets",
        json={"experience_entry_id": exp["id"], "text": "Built Python APIs", "tags": ["python"]},
    ).json()
    skill = client.post(
        "/api/skills", json={"name": "Python", "category": "language", "tags": ["backend"]}
    ).json()
    project = client.post(
        "/api/projects",
        json={"name": "API Service", "description": "A Python backend", "tech_tags": ["python"]},
    ).json()
    education = client.post(
        "/api/education-entries",
        json={
            "institution": "State U",
            "degree": "B.S.",
            "field": "CS",
            "start_date": "2018-01-01",
        },
    ).json()
    return {
        "exp": exp,
        "bullet": bullet,
        "skill": skill,
        "project": project,
        "education": education,
    }


def _create_draft(client: TestClient, bank: dict) -> dict:
    jd = client.post(
        "/api/job-descriptions",
        json={
            "company": "Real Co",
            "role_title": "Engineer",
            "raw_text": "Python engineer needed.",
        },
    ).json()
    resp = client.post(
        "/api/tailored-resumes",
        json={
            "job_description_id": jd["id"],
            "selected_experience_bullet_ids": [bank["bullet"]["id"]],
            "selected_project_ids": [bank["project"]["id"]],
            "selected_skill_ids": [bank["skill"]["id"]],
            "selected_education_ids": [bank["education"]["id"]],
            "scoring_metadata": {"skills": {str(bank["skill"]["id"]): ["python"]}},
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_create_and_get_tailored_resume(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    assert draft["status"] == "draft"
    assert draft["resolved_content"] is None

    resp = client.get(f"/api/tailored-resumes/{draft['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == draft["id"]


def test_create_tailored_resume_missing_job_description_404(client: TestClient) -> None:
    resp = client.post("/api/tailored-resumes", json={"job_description_id": 999999})
    assert resp.status_code == 404


def test_patch_draft_updates_selection(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.patch(
        f"/api/tailored-resumes/{draft['id']}", json={"selected_skill_ids": []}
    )
    assert resp.status_code == 200
    assert resp.json()["selected_skill_ids"] == []


def test_preview_renders_selected_content(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.get(f"/api/tailored-resumes/{draft['id']}/preview")
    assert resp.status_code == 200
    assert "Jane Doe" in resp.text
    assert "Built Python APIs" in resp.text
    assert "State U" in resp.text


def test_finalize_produces_pdf_and_locks_editing(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.post(f"/api/tailored-resumes/{draft['id']}/finalize")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "finalized"
    assert body["finalized_at"] is not None
    assert body["rendered_filename"] == "Jane_Doe_Resume_Real_Co_Engineer.pdf"
    assert body["resolved_content"]["contact"]["name"] == "Jane Doe"

    # editing a finalized resume is rejected
    resp = client.patch(
        f"/api/tailored-resumes/{draft['id']}", json={"selected_skill_ids": []}
    )
    assert resp.status_code == 409

    # finalizing again is rejected
    resp = client.post(f"/api/tailored-resumes/{draft['id']}/finalize")
    assert resp.status_code == 409

    # download works and returns a real PDF
    resp = client.get(f"/api/tailored-resumes/{draft['id']}/download")
    assert resp.status_code == 200
    assert resp.content.startswith(b"%PDF")


def test_download_before_finalize_rejected(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.get(f"/api/tailored-resumes/{draft['id']}/download")
    assert resp.status_code == 409


def test_enhance_disabled_by_default(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.post(f"/api/tailored-resumes/{draft['id']}/enhance")
    assert resp.status_code == 503


def test_enhance_when_enabled_returns_suggestions(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    fake_results = [
        EnhancedBullet(
            original="Built Python APIs", suggested="Developed Python APIs", flagged=False
        )
    ]

    with (
        patch("app.api.routes.tailored_resumes.get_settings") as mock_settings,
        patch("app.api.routes.tailored_resumes.enhance_bullets", return_value=fake_results),
    ):
        mock_settings.return_value.enable_llm_enhance = True
        resp = client.post(f"/api/tailored-resumes/{draft['id']}/enhance")

    assert resp.status_code == 200
    body = resp.json()
    assert body["bullets"][0]["bullet_id"] == bank["bullet"]["id"]
    assert body["bullets"][0]["suggested"] == "Developed Python APIs"
    assert body["bullets"][0]["flagged"] is False


def test_accept_enhanced_bullets_applies_to_preview(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.post(
        f"/api/tailored-resumes/{draft['id']}/enhanced-bullets",
        json={"accepted": {str(bank["bullet"]["id"]): "Developed robust Python APIs"}},
    )
    assert resp.status_code == 200
    assert resp.json()["llm_enhanced"] is True

    resp = client.get(f"/api/tailored-resumes/{draft['id']}/preview")
    assert resp.status_code == 200
    assert "Developed robust Python APIs" in resp.text
    assert "Built Python APIs" not in resp.text


def test_enhance_and_accept_rejected_when_finalized(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    client.post(f"/api/tailored-resumes/{draft['id']}/finalize")

    with patch("app.api.routes.tailored_resumes.get_settings") as mock_settings:
        mock_settings.return_value.enable_llm_enhance = True
        resp = client.post(f"/api/tailored-resumes/{draft['id']}/enhance")
    assert resp.status_code == 409

    resp = client.post(
        f"/api/tailored-resumes/{draft['id']}/enhanced-bullets", json={"accepted": {}}
    )
    assert resp.status_code == 409
