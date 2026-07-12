import base64
import json
from typing import Any

from app.services.llm_client import MODEL_ID, get_anthropic_client

_SYSTEM_PROMPT = """You extract structured resume content from an uploaded PDF for a personal
resume-tailoring tool's content bank.

Rules:
- Extract only what is literally present in the document. Never invent employers, titles,
  dates, locations, metrics, skills, or projects that are not stated in the PDF.
- Preserve bullet wording as closely as possible -- light cleanup only (e.g. fixing obvious
  OCR artifacts), never embellishment or rewriting.
- Normalize dates to YYYY-MM-01 when only a month/year is given (day is unknown). If a date is
  "Present"/ongoing/current, set end_date to null.
- For every bullet, skill, and project, infer a short list of lowercase single- or two-word
  keyword tags describing its technologies/domain (e.g. "python", "ci/cd", "machine learning").
  These tags are only used for keyword search/matching later, not treated as factual claims, but
  should still be grounded in what the bullet/skill/project actually describes.
- Each work-experience bullet belongs to exactly one experience entry; each project bullet
  belongs to exactly one project. Do not duplicate a bullet across sections.
- If a field genuinely isn't present in the document (e.g. no phone number), use an empty
  string for required string fields, or an empty array for list fields.
"""

_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "contact": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "location": {"type": "string"},
                "links": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "url": {"type": "string"},
                        },
                        "required": ["label", "url"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["name", "email", "phone", "location", "links"],
            "additionalProperties": False,
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "title": {"type": "string"},
                    "location": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": ["string", "null"]},
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["text", "tags"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "company",
                    "title",
                    "location",
                    "start_date",
                    "end_date",
                    "bullets",
                ],
                "additionalProperties": False,
            },
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "category", "tags"],
                "additionalProperties": False,
            },
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tech_tags": {"type": "array", "items": {"type": "string"}},
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["text", "tags"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["name", "description", "tech_tags", "bullets"],
                "additionalProperties": False,
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": ["string", "null"]},
                },
                "required": ["institution", "degree", "field", "start_date", "end_date"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["contact", "experience", "skills", "projects", "education"],
    "additionalProperties": False,
}


def extract_bank_data(pdf_bytes: bytes) -> dict[str, Any]:
    """Extracts structured bank content from a resume PDF, grounded strictly in what's on the
    page -- returns a plain dict matching ResumeImportPreview's shape. Never writes to the DB;
    the caller is responsible for showing this as a reviewable preview before committing."""
    client = get_anthropic_client()
    encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": _RESPONSE_SCHEMA}},
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": encoded,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Extract this resume's content into the structured schema.",
                    },
                ],
            }
        ],
    )
    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break
    parsed: dict[str, Any] = json.loads(text)
    return parsed
