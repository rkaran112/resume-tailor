from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import CONTACT_INFO_ID
from app.core.config import get_settings
from app.db.session import get_db
from app.models.bullet import Bullet
from app.models.contact import ContactInfo
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.resume_import import ResumeImportCommitResult, ResumeImportPreview
from app.services.resume_import import (
    extract_bank_data,
    extract_bank_data_from_latex,
    mark_duplicates,
)

router = APIRouter(tags=["resume-import"])

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _detect_import_kind(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".tex":
        return "latex"
    raise HTTPException(status_code=400, detail="Only PDF or LaTeX (.tex) files are supported")


@router.post("/bank/import", response_model=ResumeImportPreview)
async def import_resume(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> ResumeImportPreview:
    if not get_settings().enable_resume_import:
        raise HTTPException(status_code=503, detail="Resume import is disabled")

    kind = _detect_import_kind(file.filename)

    raw_bytes = await file.read()
    if len(raw_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB upload limit")

    if kind == "pdf":
        if not raw_bytes.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="File does not look like a valid PDF")
        extracted = extract_bank_data(raw_bytes)
    else:
        try:
            latex_source = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400, detail="LaTeX file must be UTF-8 encoded"
            ) from exc
        extracted = extract_bank_data_from_latex(latex_source)

    preview = ResumeImportPreview.model_validate(extracted)
    mark_duplicates(
        preview,
        existing_skills=db.query(Skill).all(),
        existing_experience_entries=db.query(ExperienceEntry).all(),
        existing_bullets=db.query(Bullet).all(),
        existing_projects=db.query(Project).all(),
        existing_education_entries=db.query(EducationEntry).all(),
    )
    return preview


@router.post("/bank/import/commit", response_model=ResumeImportCommitResult)
def commit_resume_import(
    payload: ResumeImportPreview, db: Session = Depends(get_db)
) -> ResumeImportCommitResult:
    contact_updated = False
    if payload.contact.include:
        existing = db.get(ContactInfo, CONTACT_INFO_ID)
        contact_data = {
            "name": payload.contact.name,
            "email": payload.contact.email,
            "phone": payload.contact.phone,
            "location": payload.contact.location,
            "links": [link.model_dump() for link in payload.contact.links],
        }
        if existing is None:
            db.add(ContactInfo(id=CONTACT_INFO_ID, **contact_data))
        else:
            for field, value in contact_data.items():
                setattr(existing, field, value)
        contact_updated = True

    experience_entries_created = 0
    bullets_created = 0
    for exp_entry in payload.experience:
        if not exp_entry.include:
            continue
        exp_model = ExperienceEntry(
            company=exp_entry.company,
            title=exp_entry.title,
            location=exp_entry.location,
            start_date=exp_entry.start_date,
            end_date=exp_entry.end_date,
        )
        db.add(exp_model)
        db.flush()
        experience_entries_created += 1
        for bullet in exp_entry.bullets:
            if not bullet.include:
                continue
            db.add(Bullet(experience_entry_id=exp_model.id, text=bullet.text, tags=bullet.tags))
            bullets_created += 1

    skills_created = 0
    for skill in payload.skills:
        if not skill.include:
            continue
        db.add(Skill(name=skill.name, category=skill.category, tags=skill.tags))
        skills_created += 1

    projects_created = 0
    for project in payload.projects:
        if not project.include:
            continue
        project_model = Project(
            name=project.name, description=project.description, tech_tags=project.tech_tags
        )
        db.add(project_model)
        db.flush()
        projects_created += 1
        for bullet in project.bullets:
            if not bullet.include:
                continue
            db.add(Bullet(project_id=project_model.id, text=bullet.text, tags=bullet.tags))
            bullets_created += 1

    education_entries_created = 0
    for edu_entry in payload.education:
        if not edu_entry.include:
            continue
        db.add(
            EducationEntry(
                institution=edu_entry.institution,
                degree=edu_entry.degree,
                field=edu_entry.field,
                start_date=edu_entry.start_date,
                end_date=edu_entry.end_date,
                gpa=edu_entry.gpa or None,
            )
        )
        education_entries_created += 1

    db.commit()

    return ResumeImportCommitResult(
        contact_updated=contact_updated,
        experience_entries_created=experience_entries_created,
        bullets_created=bullets_created,
        skills_created=skills_created,
        projects_created=projects_created,
        education_entries_created=education_entries_created,
    )
