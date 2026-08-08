import json
from dataclasses import dataclass
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.resume_import import ResumeImportPreview
from app.services.resume_import import (
    extract_bank_data,
    extract_bank_data_from_latex,
    mark_duplicates,
)

SAMPLE_EXTRACTED = {
    "contact": {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "location": "Remote",
        "links": [{"label": "GitHub", "url": "https://github.com/janedoe"}],
    },
    "experience": [
        {
            "company": "Acme Corp",
            "title": "Engineer",
            "location": "Remote",
            "start_date": "2022-01-01",
            "end_date": None,
            "bullets": [{"text": "Built Python APIs", "tags": ["python"]}],
        }
    ],
    "skills": [{"name": "Python", "category": "language", "tags": ["backend"]}],
    "projects": [
        {
            "name": "API Service",
            "description": "A Python backend",
            "tech_tags": ["python"],
            "bullets": [{"text": "Shipped v1", "tags": ["python"]}],
        }
    ],
    "education": [
        {
            "institution": "State U",
            "degree": "B.S.",
            "field": "CS",
            "start_date": "2018-01-01",
            "end_date": "2022-01-01",
        }
    ],
}


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


class _FakeMessages:
    def __init__(self, response_json: dict) -> None:
        self._response_json = response_json
        self.last_kwargs: dict | None = None

    def create(self, **kwargs: object) -> object:
        self.last_kwargs = kwargs

        class _FakeResponse:
            content = [_FakeTextBlock(text=json.dumps(self._response_json))]

        return _FakeResponse()


class _FakeClient:
    def __init__(self, response_json: dict) -> None:
        self.messages = _FakeMessages(response_json)


def test_extract_bank_data_sends_pdf_document_block() -> None:
    fake_client = _FakeClient(SAMPLE_EXTRACTED)

    with patch("app.services.resume_import.get_anthropic_client", return_value=fake_client):
        result = extract_bank_data(b"%PDF-1.4 fake pdf bytes")

    assert result == SAMPLE_EXTRACTED
    assert fake_client.messages.last_kwargs is not None
    assert fake_client.messages.last_kwargs["model"] == "claude-opus-4-8"
    content = fake_client.messages.last_kwargs["messages"][0]["content"]
    document_block = next(block for block in content if block["type"] == "document")
    assert document_block["source"]["media_type"] == "application/pdf"
    assert "output_config" in fake_client.messages.last_kwargs


def test_import_disabled_by_default(client: TestClient) -> None:
    resp = client.post(
        "/api/bank/import",
        files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert resp.status_code == 503


def test_import_rejects_non_pdf(client: TestClient) -> None:
    with patch("app.api.routes.resume_import.get_settings") as mock_settings:
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            files={"file": ("resume.txt", b"plain text", "text/plain")},
        )
    assert resp.status_code == 400


def test_import_returns_preview_when_enabled(client: TestClient) -> None:
    with (
        patch("app.api.routes.resume_import.get_settings") as mock_settings,
        patch(
            "app.api.routes.resume_import.extract_bank_data",
            return_value=SAMPLE_EXTRACTED,
        ),
    ):
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["contact"]["name"] == "Jane Doe"
    assert body["experience"][0]["bullets"][0]["text"] == "Built Python APIs"
    assert body["experience"][0]["include"] is True


def _preview_payload() -> dict:
    preview = json.loads(json.dumps(SAMPLE_EXTRACTED))
    preview["contact"]["include"] = True
    for entry in preview["experience"]:
        entry["include"] = True
        for bullet in entry["bullets"]:
            bullet["include"] = True
    for skill in preview["skills"]:
        skill["include"] = True
    for project in preview["projects"]:
        project["include"] = True
        for bullet in project["bullets"]:
            bullet["include"] = True
    for entry in preview["education"]:
        entry["include"] = True
    return preview


def test_commit_writes_bank_rows(client: TestClient) -> None:
    payload = _preview_payload()

    resp = client.post("/api/bank/import/commit", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["contact_updated"] is True
    assert body["experience_entries_created"] == 1
    assert body["skills_created"] == 1
    assert body["projects_created"] == 1
    assert body["education_entries_created"] == 1
    assert body["bullets_created"] == 2  # one experience bullet + one project bullet

    assert client.get("/api/contact-info").json()["name"] == "Jane Doe"
    assert len(client.get("/api/experience-entries").json()) == 1
    assert len(client.get("/api/skills").json()) == 1
    assert len(client.get("/api/projects").json()) == 1
    assert len(client.get("/api/education-entries").json()) == 1
    assert len(client.get("/api/bullets").json()) == 2


def test_commit_skips_unchecked_items(client: TestClient) -> None:
    payload = _preview_payload()
    payload["contact"]["include"] = False
    payload["skills"][0]["include"] = False
    payload["experience"][0]["bullets"][0]["include"] = False

    resp = client.post("/api/bank/import/commit", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["contact_updated"] is False
    assert body["skills_created"] == 0
    assert body["bullets_created"] == 1  # project bullet only, experience bullet excluded

    assert client.get("/api/skills").json() == []
    assert client.get("/api/contact-info").json()["name"] == ""


# ---- LaTeX extraction ----


def test_extract_bank_data_from_latex_sends_text_content_block() -> None:
    fake_client = _FakeClient(SAMPLE_EXTRACTED)
    latex_source = "\\documentclass{article}\\begin{document}Jane Doe\\end{document}"

    with patch("app.services.resume_import.get_anthropic_client", return_value=fake_client):
        result = extract_bank_data_from_latex(latex_source)

    assert result == SAMPLE_EXTRACTED
    assert fake_client.messages.last_kwargs is not None
    content = fake_client.messages.last_kwargs["messages"][0]["content"]
    assert all(block["type"] == "text" for block in content)
    assert any(latex_source in block["text"] for block in content)
    assert "LaTeX" in fake_client.messages.last_kwargs["system"]
    assert "output_config" in fake_client.messages.last_kwargs


def test_import_accepts_tex_upload(client: TestClient) -> None:
    with (
        patch("app.api.routes.resume_import.get_settings") as mock_settings,
        patch(
            "app.api.routes.resume_import.extract_bank_data_from_latex",
            return_value=SAMPLE_EXTRACTED,
        ) as fake_extract,
    ):
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            # Deliberately wrong/unreliable content_type -- proves extension-based
            # detection, not the content_type header, is what gates this.
            files={"file": ("resume.tex", b"\\documentclass{article}", "application/octet-stream")},
        )

    assert resp.status_code == 200
    assert resp.json()["contact"]["name"] == "Jane Doe"
    fake_extract.assert_called_once()


def test_import_rejects_docx(client: TestClient) -> None:
    with patch("app.api.routes.resume_import.get_settings") as mock_settings:
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            files={
                "file": (
                    "resume.docx",
                    b"fake docx bytes",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
    assert resp.status_code == 400


def test_import_rejects_pdf_extension_with_non_pdf_bytes(client: TestClient) -> None:
    with patch("app.api.routes.resume_import.get_settings") as mock_settings:
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            files={"file": ("resume.pdf", b"not actually a pdf", "application/pdf")},
        )
    assert resp.status_code == 400


# ---- Duplicate detection ----


def _sample_preview() -> ResumeImportPreview:
    return ResumeImportPreview.model_validate(SAMPLE_EXTRACTED)


def test_mark_duplicates_flags_matching_skill_case_insensitively() -> None:
    preview = _sample_preview()
    existing_skill = Skill(id=1, name="python", category="language", tags=[])

    mark_duplicates(
        preview,
        existing_skills=[existing_skill],
        existing_experience_entries=[],
        existing_bullets=[],
        existing_projects=[],
        existing_education_entries=[],
    )

    assert preview.skills[0].already_exists is True
    assert preview.skills[0].include is False


def test_mark_duplicates_flags_matching_experience_by_company_and_title() -> None:
    preview = _sample_preview()
    existing_entry = ExperienceEntry(
        id=1,
        company="ACME CORP",
        title="engineer",
        location="Remote",
        start_date=date(2022, 1, 1),
    )

    mark_duplicates(
        preview,
        existing_skills=[],
        existing_experience_entries=[existing_entry],
        existing_bullets=[],
        existing_projects=[],
        existing_education_entries=[],
    )

    assert preview.experience[0].already_exists is True
    assert preview.experience[0].include is False


def test_mark_duplicates_flags_matching_bullet_by_text() -> None:
    preview = _sample_preview()
    existing_bullet = Bullet(id=1, experience_entry_id=1, text="built python apis", tags=[])

    mark_duplicates(
        preview,
        existing_skills=[],
        existing_experience_entries=[],
        existing_bullets=[existing_bullet],
        existing_projects=[],
        existing_education_entries=[],
    )

    assert preview.experience[0].bullets[0].already_exists is True
    assert preview.experience[0].bullets[0].include is False


def test_mark_duplicates_flags_matching_project_by_name() -> None:
    preview = _sample_preview()
    existing_project = Project(id=1, name="api service", description="", tech_tags=[])

    mark_duplicates(
        preview,
        existing_skills=[],
        existing_experience_entries=[],
        existing_bullets=[],
        existing_projects=[existing_project],
        existing_education_entries=[],
    )

    assert preview.projects[0].already_exists is True
    assert preview.projects[0].include is False


def test_mark_duplicates_flags_matching_education_by_institution_and_degree() -> None:
    preview = _sample_preview()
    existing_entry = EducationEntry(
        id=1,
        institution="state u",
        degree="b.s.",
        field="CS",
        start_date=date(2018, 1, 1),
    )

    mark_duplicates(
        preview,
        existing_skills=[],
        existing_experience_entries=[],
        existing_bullets=[],
        existing_projects=[],
        existing_education_entries=[existing_entry],
    )

    assert preview.education[0].already_exists is True
    assert preview.education[0].include is False


def test_mark_duplicates_marks_non_matching_items_as_new() -> None:
    preview = _sample_preview()

    mark_duplicates(
        preview,
        existing_skills=[],
        existing_experience_entries=[],
        existing_bullets=[],
        existing_projects=[],
        existing_education_entries=[],
    )

    assert preview.skills[0].already_exists is False
    assert preview.skills[0].include is True
    assert preview.experience[0].already_exists is False
    assert preview.experience[0].include is True
    assert preview.experience[0].bullets[0].already_exists is False
    assert preview.projects[0].already_exists is False
    assert preview.education[0].already_exists is False


def test_import_route_flags_duplicates_against_seeded_bank(client: TestClient) -> None:
    # Seed the bank via the real CRUD routes, with different casing than the
    # extraction result to prove matching is case-insensitive end to end.
    client.post("/api/skills", json={"name": "PYTHON", "category": "language", "tags": []})
    exp_resp = client.post(
        "/api/experience-entries",
        json={
            "company": "acme corp",
            "title": "ENGINEER",
            "location": "Remote",
            "start_date": "2022-01-01",
        },
    )
    client.post(
        "/api/bullets",
        json={
            "experience_entry_id": exp_resp.json()["id"],
            "text": "BUILT PYTHON APIS",
            "tags": [],
        },
    )
    client.post(
        "/api/projects", json={"name": "api service", "description": "", "tech_tags": []}
    )
    client.post(
        "/api/education-entries",
        json={
            "institution": "STATE U",
            "degree": "b.s.",
            "field": "CS",
            "start_date": "2018-01-01",
        },
    )

    with (
        patch("app.api.routes.resume_import.get_settings") as mock_settings,
        patch(
            "app.api.routes.resume_import.extract_bank_data", return_value=SAMPLE_EXTRACTED
        ),
    ):
        mock_settings.return_value.enable_resume_import = True
        resp = client.post(
            "/api/bank/import",
            files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["skills"][0]["already_exists"] is True
    assert body["skills"][0]["include"] is False
    assert body["experience"][0]["already_exists"] is True
    assert body["experience"][0]["include"] is False
    assert body["experience"][0]["bullets"][0]["already_exists"] is True
    assert body["projects"][0]["already_exists"] is True
    assert body["education"][0]["already_exists"] is True
    # Contact is never dedup-checked -- no already_exists key on it.
    assert "already_exists" not in body["contact"]
