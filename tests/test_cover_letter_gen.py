import json
from dataclasses import dataclass
from unittest.mock import patch

from app.services.cover_letter_gen import generate_cover_letter

SAMPLE_RESOLVED_CONTENT = {
    "contact": {"name": "Jane Doe", "email": "jane@example.com"},
    "experience": [
        {"company": "Acme", "title": "Engineer", "bullets": ["Built Python APIs"]},
    ],
    "skills": [{"category": "Languages", "names": ["Python"]}],
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


def test_generate_cover_letter_parses_paragraphs() -> None:
    fake_response = {
        "paragraphs": [
            "I am excited to apply for the Backend Engineer role at Real Co.",
            "At Acme, I built Python APIs that improved system reliability.",
            "I look forward to bringing this experience to your team.",
        ]
    }
    fake_client = _FakeClient(fake_response)

    with patch("app.services.cover_letter_gen.get_anthropic_client", return_value=fake_client):
        paragraphs = generate_cover_letter(
            "Backend Engineer needed with Python experience.", SAMPLE_RESOLVED_CONTENT
        )

    assert paragraphs == fake_response["paragraphs"]
    assert fake_client.messages.last_kwargs is not None
    assert fake_client.messages.last_kwargs["model"] == "claude-opus-4-8"
    assert "Acme" in fake_client.messages.last_kwargs["messages"][0]["content"]
    assert "output_config" in fake_client.messages.last_kwargs
