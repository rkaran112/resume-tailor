from functools import lru_cache

import anthropic

from app.core.config import get_settings

MODEL_ID = "claude-opus-4-8"


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    """Uses the .env-provided key when set; otherwise falls back to the zero-arg
    client, which resolves credentials from the environment (ANTHROPIC_API_KEY,
    ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile)."""
    key = get_settings().anthropic_api_key
    if key:
        return anthropic.Anthropic(api_key=key)
    return anthropic.Anthropic()
