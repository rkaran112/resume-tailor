from unittest.mock import patch

from fastapi.testclient import TestClient

FAKE_PARAGRAPHS = [
    "I am excited to apply for the Engineer role at Real Co.",
    "At Acme Corp, I built Python APIs that improved reliability.",
    "I look forward to discussing this opportunity further.",
]


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
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _create_cover_letter(client: TestClient, tailored_resume_id: int) -> dict:
    with (
        patch("app.api.routes.cover_letters.get_settings") as mock_settings,
        patch(
            "app.api.routes.cover_letters.generate_cover_letter",
            return_value=FAKE_PARAGRAPHS,
        ),
    ):
        mock_settings.return_value.enable_cover_letter = True
        resp = client.post(
            "/api/cover-letters", json={"tailored_resume_id": tailored_resume_id}
        )
    assert resp.status_code == 201
    return resp.json()


def test_create_disabled_by_default(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    resp = client.post("/api/cover-letters", json={"tailored_resume_id": draft["id"]})
    assert resp.status_code == 503


def test_create_when_enabled_generates_draft(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)

    cover_letter = _create_cover_letter(client, draft["id"])
    assert cover_letter["status"] == "draft"
    assert cover_letter["llm_generated"] is True
    assert cover_letter["edited_text"] is None
    assert "\n\n".join(FAKE_PARAGRAPHS) == cover_letter["generated_text"]

    resp = client.get(f"/api/cover-letters/{cover_letter['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cover_letter["id"]


def test_edit_draft_updates_edited_text(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    cover_letter = _create_cover_letter(client, draft["id"])

    resp = client.patch(
        f"/api/cover-letters/{cover_letter['id']}",
        json={"edited_text": "A hand-edited opening.\n\nA hand-edited closing."},
    )
    assert resp.status_code == 200
    assert resp.json()["edited_text"] == "A hand-edited opening.\n\nA hand-edited closing."


def test_preview_renders_active_text(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    cover_letter = _create_cover_letter(client, draft["id"])

    resp = client.get(f"/api/cover-letters/{cover_letter['id']}/preview")
    assert resp.status_code == 200
    assert "Jane Doe" in resp.text
    assert "Real Co" in resp.text
    assert FAKE_PARAGRAPHS[0] in resp.text

    client.patch(
        f"/api/cover-letters/{cover_letter['id']}",
        json={"edited_text": "A hand-edited paragraph."},
    )
    resp = client.get(f"/api/cover-letters/{cover_letter['id']}/preview")
    assert "A hand-edited paragraph." in resp.text
    assert FAKE_PARAGRAPHS[0] not in resp.text


def test_finalize_produces_pdf_and_locks_editing(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    cover_letter = _create_cover_letter(client, draft["id"])

    resp = client.post(f"/api/cover-letters/{cover_letter['id']}/finalize")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "finalized"
    assert body["finalized_at"] is not None
    assert body["rendered_filename"] == "Jane_Doe_CoverLetter_Real_Co_Engineer.pdf"

    resp = client.patch(
        f"/api/cover-letters/{cover_letter['id']}", json={"edited_text": "Nope"}
    )
    assert resp.status_code == 409

    resp = client.post(f"/api/cover-letters/{cover_letter['id']}/finalize")
    assert resp.status_code == 409

    resp = client.get(f"/api/cover-letters/{cover_letter['id']}/download")
    assert resp.status_code == 200
    assert resp.content.startswith(b"%PDF")


def test_download_before_finalize_rejected(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    cover_letter = _create_cover_letter(client, draft["id"])

    resp = client.get(f"/api/cover-letters/{cover_letter['id']}/download")
    assert resp.status_code == 409


def test_create_uses_finalized_resume_snapshot(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    client.post(f"/api/tailored-resumes/{draft['id']}/finalize")

    with (
        patch("app.api.routes.cover_letters.get_settings") as mock_settings,
        patch(
            "app.api.routes.cover_letters.generate_cover_letter",
            return_value=FAKE_PARAGRAPHS,
        ) as mock_generate,
    ):
        mock_settings.return_value.enable_cover_letter = True
        resp = client.post("/api/cover-letters", json={"tailored_resume_id": draft["id"]})

    assert resp.status_code == 201
    resolved_content_arg = mock_generate.call_args[0][1]
    assert resolved_content_arg["contact"]["name"] == "Jane Doe"


def test_application_links_cover_letter(client: TestClient) -> None:
    bank = _seed_bank(client)
    draft = _create_draft(client, bank)
    cover_letter = _create_cover_letter(client, draft["id"])

    jd_id = draft["job_description_id"]
    resp = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "tailored_resume_id": draft["id"],
            "cover_letter_id": cover_letter["id"],
            "company": "Real Co",
            "role_title": "Engineer",
            "date_applied": "2026-07-12",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["cover_letter_id"] == cover_letter["id"]
