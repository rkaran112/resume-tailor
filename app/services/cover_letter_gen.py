import json
from typing import Any

from app.services.llm_client import MODEL_ID, get_anthropic_client

_SYSTEM_PROMPT = """You write the body of a professional cover letter for a job application,
grounded strictly in the candidate's resume content provided below.

Rules:
- Only reference employers, projects, skills, and achievements that appear in the supplied
  resume content. Never invent employers, dates, skills, tools, or metrics not present there.
- Write 3-4 concise paragraphs: an opening expressing interest in the role, one or two
  paragraphs connecting specific resume experience to the job description's requirements, and
  a brief closing paragraph.
- Do not include a greeting ("Dear Hiring Manager") or a sign-off ("Sincerely,") -- those are
  added separately by the document template.
"""

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "paragraphs": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["paragraphs"],
    "additionalProperties": False,
}


def generate_cover_letter(job_description_text: str, resolved_content: dict[str, Any]) -> list[str]:
    """Drafts cover letter body paragraphs grounded strictly in resolved_content -- the
    resume's already-selected/finalized content -- and the JD. Never sees the full bank."""
    client = get_anthropic_client()
    user_content = (
        f"Job description:\n{job_description_text}\n\n"
        "Candidate's resume content (the only source of truth for claims):\n"
        f"{json.dumps(resolved_content, indent=2)}"
    )

    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=2048,
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
    return list(parsed["paragraphs"])
