import base64
import json
from collections.abc import Sequence
from typing import Any, cast

from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.resume_import import ResumeImportPreview
from app.services.llm_client import MODEL_ID, get_anthropic_client

_SYSTEM_PROMPT = """You extract structured resume content from an uploaded resume for a personal
resume-tailoring tool's content bank. The resume is supplied either as a PDF document or as raw
LaTeX source -- follow the additional rules below when it's LaTeX.

Rules:
- Extract only what is literally present in the document. Never invent employers, titles,
  dates, locations, metrics, skills, or projects that are not stated in the source.
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
- If a field genuinely isn't present in the document (e.g. no phone number, no GPA), use an empty
  string for required string fields, or an empty array for list fields.
"""

_LATEX_ADDENDUM = """The document above is raw LaTeX source, not rendered text. Additional rules for
this input type:
- Ignore the preamble entirely (\\documentclass, \\usepackage, \\newcommand definitions, \\geometry,
  color/font setup) -- none of it is resume content.
- Ignore comment lines (unescaped % to end of line).
- Extract only the literal human-readable text that would render on the page: content inside
  \\item, \\textbf{}, \\section*{}, table cells, and similar. Strip LaTeX markup/escapes from the
  extracted text (e.g. "\\&" -> "&", "\\%" -> "%").
- Custom macros (e.g. a personal \\cvitem{Company}{Title}{Dates} command) may be resolved into
  their literal arguments when the mapping is unambiguous from how the macro is invoked, but never
  invent or guess a value for an argument that isn't textually present.
- If \\input{...} or \\include{...} references another file that isn't in the provided source, its
  content is simply unavailable -- do not fabricate what it might contain.
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
                    "gpa": {"type": "string"},
                },
                "required": ["institution", "degree", "field", "start_date", "end_date", "gpa"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["contact", "experience", "skills", "projects", "education"],
    "additionalProperties": False,
}


def _run_extraction(system_prompt: str, content_blocks: list[dict[str, Any]]) -> dict[str, Any]:
    client = get_anthropic_client()
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": _RESPONSE_SCHEMA}},
        system=system_prompt,
        messages=cast(Any, [{"role": "user", "content": content_blocks}]),
    )
    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break
    parsed: dict[str, Any] = json.loads(text)
    return parsed


def extract_bank_data(pdf_bytes: bytes) -> dict[str, Any]:
    """Extracts structured bank content from a resume PDF, grounded strictly in what's on the
    page -- returns a plain dict matching ResumeImportPreview's shape. Never writes to the DB;
    the caller is responsible for showing this as a reviewable preview before committing."""
    encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    content: list[dict[str, Any]] = [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": encoded,
            },
        },
        {"type": "text", "text": "Extract this resume's content into the structured schema."},
    ]
    return _run_extraction(_SYSTEM_PROMPT, content)


def extract_bank_data_from_latex(latex_source: str) -> dict[str, Any]:
    """Same contract as extract_bank_data, for a resume supplied as raw LaTeX source instead of
    a PDF -- the source is sent as a plain text block and the model is instructed to ignore
    LaTeX markup/preamble/comments and extract only the literal rendered content."""
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"The following is the raw LaTeX source of a resume:\n\n"
                f"```latex\n{latex_source}\n```"
            ),
        },
        {
            "type": "text",
            "text": "Extract this resume's content into the structured schema, following the "
            "LaTeX-specific rules in the system prompt.",
        },
    ]
    return _run_extraction(_SYSTEM_PROMPT + "\n\n" + _LATEX_ADDENDUM, content)


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def mark_duplicates(
    preview: ResumeImportPreview,
    *,
    existing_skills: Sequence[Skill],
    existing_experience_entries: Sequence[ExperienceEntry],
    existing_bullets: Sequence[Bullet],
    existing_projects: Sequence[Project],
    existing_education_entries: Sequence[EducationEntry],
) -> ResumeImportPreview:
    """Flags each non-contact preview item as already_exists via deterministic, case-insensitive
    text matching against the current bank, and sets include accordingly: off by default for
    items that already exist (avoids creating a duplicate row -- commit never merges), on by
    default for genuinely new items (matching prior behavior). Contact is excluded -- it's a
    singleton upsert with different semantics. Mutates and returns preview."""
    skill_keys = {_normalize(s.name) for s in existing_skills}
    exp_keys = {(_normalize(e.company), _normalize(e.title)) for e in existing_experience_entries}
    bullet_keys = {_normalize(b.text) for b in existing_bullets}
    project_keys = {_normalize(p.name) for p in existing_projects}
    edu_keys = {
        (_normalize(e.institution), _normalize(e.degree)) for e in existing_education_entries
    }

    for skill in preview.skills:
        skill.already_exists = _normalize(skill.name) in skill_keys
        skill.include = not skill.already_exists

    for entry in preview.experience:
        entry.already_exists = (_normalize(entry.company), _normalize(entry.title)) in exp_keys
        entry.include = not entry.already_exists
        for bullet in entry.bullets:
            bullet.already_exists = _normalize(bullet.text) in bullet_keys
            bullet.include = not bullet.already_exists

    for project in preview.projects:
        project.already_exists = _normalize(project.name) in project_keys
        project.include = not project.already_exists
        for bullet in project.bullets:
            bullet.already_exists = _normalize(bullet.text) in bullet_keys
            bullet.include = not bullet.already_exists

    for edu_entry in preview.education:
        edu_entry.already_exists = (
            _normalize(edu_entry.institution),
            _normalize(edu_entry.degree),
        ) in edu_keys
        edu_entry.include = not edu_entry.already_exists

    return preview
