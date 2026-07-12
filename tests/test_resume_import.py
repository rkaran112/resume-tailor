import json
from dataclasses import dataclass
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.services.resume_import import extract_bank_data

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
