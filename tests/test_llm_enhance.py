import json
from dataclasses import dataclass
from unittest.mock import patch

from app.services.llm_enhance import _is_flagged, enhance_bullets


def test_is_flagged_true_for_large_length_deviation() -> None:
    assert _is_flagged("Built the thing", "Built") is True
    assert _is_flagged("Built the thing", "Built the thing and everything else too" * 3) is True


def test_is_flagged_false_for_similar_length() -> None:
    assert _is_flagged("Built the thing well", "Constructed the thing nicely") is False


def test_enhance_bullets_empty_input_skips_api_call() -> None:
    with patch("app.services.llm_enhance.get_anthropic_client") as mock_get_client:
        result = enhance_bullets("some JD text", [])
    assert result == []
    mock_get_client.assert_not_called()


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


def test_enhance_bullets_parses_response_and_flags() -> None:
    fake_response = {
        "bullets": [
            {"original": "Built Python APIs", "suggested": "Developed Python APIs"},
            {"original": "Wrote docs", "suggested": "Wrote extensive documentation covering"},
        ]
    }
    fake_client = _FakeClient(fake_response)

    with patch("app.services.llm_enhance.get_anthropic_client", return_value=fake_client):
        results = enhance_bullets("Python engineer needed.", ["Built Python APIs", "Wrote docs"])

    assert len(results) == 2
    assert results[0].original == "Built Python APIs"
    assert results[0].suggested == "Developed Python APIs"
    assert results[0].flagged is False

    assert results[1].original == "Wrote docs"
    assert results[1].flagged is True

    assert fake_client.messages.last_kwargs is not None
    assert fake_client.messages.last_kwargs["model"] == "claude-opus-4-8"
    assert "output_config" in fake_client.messages.last_kwargs
