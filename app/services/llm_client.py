from functools import lru_cache

import anthropic

MODEL_ID = "claude-opus-4-8"


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    """Zero-arg client — resolves credentials from the environment
    (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile)."""
    return anthropic.Anthropic()
