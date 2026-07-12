from typing import Any, TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.bullet import Bullet
from app.models.contact import ContactInfo
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.models.tailored_resume import TailoredResume
from app.services.resolve import build_resolved_content

ModelT = TypeVar("ModelT")

CONTACT_INFO_ID = 1


def get_or_404(db: Session, model: type[ModelT], obj_id: int) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {obj_id} not found")
    return obj


def get_or_create_contact_info(db: Session) -> ContactInfo:
    contact = db.get(ContactInfo, CONTACT_INFO_ID)
    if contact is None:
        contact = ContactInfo(
            id=CONTACT_INFO_ID, name="", email="", phone="", location="", links=[]
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


def resolve_tailored_resume_content(
    db: Session, tailored_resume: TailoredResume
) -> dict[str, Any]:
    """Live-computes the current resolved_content for a draft tailored resume (or re-derives
    the same shape for a finalized one) -- shared by tailored_resumes.py (preview/finalize)
    and cover_letters.py (grounding the LLM draft in the same resume content)."""
    contact = get_or_create_contact_info(db)
    experience_entries = list(db.query(ExperienceEntry).all())
    bullets = list(db.query(Bullet).filter(Bullet.is_active.is_(True)).all())
    projects = list(db.query(Project).all())
    skills = list(db.query(Skill).all())
    education_entries = list(db.query(EducationEntry).all())

    return build_resolved_content(
        contact_info=contact,
        experience_entries=experience_entries,
        bullets=bullets,
        projects=projects,
        skills=skills,
        education_entries=education_entries,
        selected_experience_bullet_ids=tailored_resume.selected_experience_bullet_ids,
        selected_project_ids=tailored_resume.selected_project_ids,
        selected_skill_ids=tailored_resume.selected_skill_ids,
        selected_education_ids=tailored_resume.selected_education_ids,
        llm_enhanced_bullets=tailored_resume.llm_enhanced_bullets,
    )
