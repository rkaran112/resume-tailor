from collections.abc import Sequence
from datetime import date
from typing import Any

from app.models.bullet import Bullet
from app.models.contact import ContactInfo
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill


def _format_date(value: date | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%b %Y")


def split_full_name(full_name: str) -> tuple[str, str]:
    """Splits "First Last Middle" into (first, "Last Middle"). Best-effort — a single
    `name` field on ContactInfo has no structured first/last split to draw on."""
    parts = full_name.strip().split(" ", 1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""
    return first, last


def build_resolved_content(
    contact_info: ContactInfo,
    experience_entries: Sequence[ExperienceEntry],
    bullets: Sequence[Bullet],
    projects: Sequence[Project],
    skills: Sequence[Skill],
    education_entries: Sequence[EducationEntry],
    selected_experience_bullet_ids: Sequence[int],
    selected_project_ids: Sequence[int],
    selected_skill_ids: Sequence[int],
    selected_education_ids: Sequence[int],
) -> dict[str, Any]:
    """Denormalizes selected bank content into the plain-dict context shape
    app.services.renderer.render_html expects."""
    selected_bullet_id_set = set(selected_experience_bullet_ids)
    selected_project_id_set = set(selected_project_ids)
    selected_skill_id_set = set(selected_skill_ids)
    selected_education_id_set = set(selected_education_ids)

    bullets_by_experience_entry: dict[int, list[Bullet]] = {}
    bullets_by_project: dict[int, list[Bullet]] = {}
    for bullet in bullets:
        if bullet.experience_entry_id is not None:
            bullets_by_experience_entry.setdefault(bullet.experience_entry_id, []).append(bullet)
        elif bullet.project_id is not None:
            bullets_by_project.setdefault(bullet.project_id, []).append(bullet)

    experience = [
        {
            "company": entry.company,
            "title": entry.title,
            "location": entry.location,
            "start_date": _format_date(entry.start_date),
            "end_date": _format_date(entry.end_date),
            "bullets": [
                bullet.text
                for bullet in bullets_by_experience_entry.get(entry.id, [])
                if bullet.id in selected_bullet_id_set
            ],
        }
        for entry in sorted(experience_entries, key=lambda e: e.display_order)
    ]

    selected_projects = sorted(
        (project for project in projects if project.id in selected_project_id_set),
        key=lambda p: p.display_order,
    )
    project_entries = [
        {
            "name": project.name,
            "description": project.description,
            "tech_tags": list(project.tech_tags),
            "link": project.link,
            "bullets": [bullet.text for bullet in bullets_by_project.get(project.id, [])],
        }
        for project in selected_projects
    ]

    skills_by_category: dict[str, list[str]] = {}
    for skill in skills:
        if skill.id in selected_skill_id_set:
            skills_by_category.setdefault(skill.category, []).append(skill.name)
    skill_groups = [
        {"category": category, "names": names} for category, names in skills_by_category.items()
    ]

    education_out = [
        {
            "institution": entry.institution,
            "degree": entry.degree,
            "field": entry.field,
            "start_date": _format_date(entry.start_date),
            "end_date": _format_date(entry.end_date),
            "gpa": entry.gpa,
        }
        for entry in education_entries
        if entry.id in selected_education_id_set
    ]

    return {
        "contact": {
            "name": contact_info.name,
            "email": contact_info.email,
            "phone": contact_info.phone,
            "location": contact_info.location,
            "links": list(contact_info.links),
        },
        "experience": experience,
        "projects": project_entries,
        "skills": skill_groups,
        "education": education_out,
    }
