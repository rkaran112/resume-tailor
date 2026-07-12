import json
from dataclasses import dataclass

from app.services.llm_client import MODEL_ID, get_anthropic_client

_SYSTEM_PROMPT = """You rewrite resume bullet points to better match a job description.

Rules:
- Reword or reorder only. Never add skills, tools, technologies, numbers, or claims that are
  not already present in the original bullet.
- Keep each rewritten bullet close to the original length.
- Return exactly one rewritten bullet per original bullet, in the same order, pairing each
  with its original text.
"""

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "bullets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original": {"type": "string"},
                    "suggested": {"type": "string"},
                },
                "required": ["original", "suggested"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["bullets"],
    "additionalProperties": False,
}

_FLAG_MIN_RATIO = 0.5
_FLAG_MAX_RATIO = 1.8


@dataclass
class EnhancedBullet:
    original: str
    suggested: str
    flagged: bool


def _is_flagged(original: str, suggested: str) -> bool:
    if not original:
        return True
    ratio = len(suggested) / len(original)
    return ratio < _FLAG_MIN_RATIO or ratio > _FLAG_MAX_RATIO


def enhance_bullets(job_description_text: str, bullets: list[str]) -> list[EnhancedBullet]:
    """Rewords already-selected bullets to better match the JD. Never sees the full bank —
    only the JD text and the bullets the matching engine already picked. Guardrailed via the
    system prompt (reword only) and a post-hoc length-deviation flag for manual review."""
    if not bullets:
        return []

    client = get_anthropic_client()
    user_content = (
        f"Job description:\n{job_description_text}\n\n"
        "Resume bullets to rewrite (reword only — do not add new skills, tools, numbers, "
        "or claims):\n" + "\n".join(f"- {bullet}" for bullet in bullets)
    )

    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": _RESPONSE_SCHEMA}},
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break

    parsed = json.loads(text)

    return [
        EnhancedBullet(
            original=item["original"],
            suggested=item["suggested"],
            flagged=_is_flagged(item["original"], item["suggested"]),
        )
        for item in parsed["bullets"]
    ]
