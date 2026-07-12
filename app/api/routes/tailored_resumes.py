from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.api.deps import get_or_404, get_or_create_contact_info
from app.core.config import get_settings
from app.db.session import get_db
from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.job_description import JobDescription
from app.models.project import Project
from app.models.skill import Skill
from app.models.tailored_resume import TailoredResume
from app.schemas.tailored_resume import (
    TailoredResumeCreate,
    TailoredResumeRead,
    TailoredResumeUpdate,
)
from app.services.filename import build_filename
from app.services.renderer import html_to_pdf, render_html
from app.services.resolve import build_resolved_content, split_full_name

router = APIRouter(tags=["tailored-resumes"])


def _resolve_content_for(db: Session, tailored_resume: TailoredResume) -> dict[str, Any]:
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
    )


@router.get("/tailored-resumes", response_model=list[TailoredResumeRead])
def list_tailored_resumes(db: Session = Depends(get_db)) -> list[TailoredResume]:
    return list(db.query(TailoredResume).order_by(TailoredResume.id.desc()).all())


@router.post("/tailored-resumes", response_model=TailoredResumeRead, status_code=201)
def create_tailored_resume(
    payload: TailoredResumeCreate, db: Session = Depends(get_db)
) -> TailoredResume:
    get_or_404(db, JobDescription, payload.job_description_id)
    tailored_resume = TailoredResume(
        job_description_id=payload.job_description_id,
        selected_experience_bullet_ids=payload.selected_experience_bullet_ids,
        selected_project_ids=payload.selected_project_ids,
        selected_skill_ids=payload.selected_skill_ids,
        selected_education_ids=payload.selected_education_ids,
        scoring_metadata=payload.scoring_metadata,
    )
    db.add(tailored_resume)
    db.commit()
    db.refresh(tailored_resume)
    return tailored_resume


@router.get("/tailored-resumes/{tailored_resume_id}", response_model=TailoredResumeRead)
def get_tailored_resume(tailored_resume_id: int, db: Session = Depends(get_db)) -> TailoredResume:
    return get_or_404(db, TailoredResume, tailored_resume_id)


@router.patch("/tailored-resumes/{tailored_resume_id}", response_model=TailoredResumeRead)
def update_tailored_resume(
    tailored_resume_id: int, payload: TailoredResumeUpdate, db: Session = Depends(get_db)
) -> TailoredResume:
    tailored_resume = get_or_404(db, TailoredResume, tailored_resume_id)
    if tailored_resume.status == "finalized":
        raise HTTPException(status_code=409, detail="Cannot edit a finalized tailored resume")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tailored_resume, field, value)
    db.commit()
    db.refresh(tailored_resume)
    return tailored_resume


@router.get("/tailored-resumes/{tailored_resume_id}/preview", response_class=HTMLResponse)
def preview_tailored_resume(tailored_resume_id: int, db: Session = Depends(get_db)) -> str:
    tailored_resume = get_or_404(db, TailoredResume, tailored_resume_id)
    context = _resolve_content_for(db, tailored_resume)
    return render_html(context)


@router.post("/tailored-resumes/{tailored_resume_id}/finalize", response_model=TailoredResumeRead)
def finalize_tailored_resume(
    tailored_resume_id: int, db: Session = Depends(get_db)
) -> TailoredResume:
    tailored_resume = get_or_404(db, TailoredResume, tailored_resume_id)
    if tailored_resume.status == "finalized":
        raise HTTPException(status_code=409, detail="Tailored resume is already finalized")

    job_description = get_or_404(db, JobDescription, tailored_resume.job_description_id)
    contact = get_or_create_contact_info(db)
    resolved_content = _resolve_content_for(db, tailored_resume)

    html = render_html(resolved_content)
    pdf_bytes = html_to_pdf(html)

    first, last = split_full_name(contact.name)
    filename = build_filename(
        first, last, "Resume", job_description.company, job_description.role_title
    )

    output_dir = Path(get_settings().generated_resumes_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = (output_dir / filename).resolve()
    output_path.write_bytes(pdf_bytes)

    tailored_resume.resolved_content = resolved_content
    tailored_resume.rendered_pdf_path = str(output_path)
    tailored_resume.rendered_filename = filename
    tailored_resume.status = "finalized"
    tailored_resume.finalized_at = datetime.now(UTC)

    db.commit()
    db.refresh(tailored_resume)
    return tailored_resume


@router.get("/tailored-resumes/{tailored_resume_id}/download")
def download_tailored_resume(
    tailored_resume_id: int, db: Session = Depends(get_db)
) -> FileResponse:
    tailored_resume = get_or_404(db, TailoredResume, tailored_resume_id)
    if tailored_resume.status != "finalized" or not tailored_resume.rendered_pdf_path:
        raise HTTPException(status_code=409, detail="Tailored resume is not finalized yet")
    return FileResponse(
        tailored_resume.rendered_pdf_path,
        media_type="application/pdf",
        filename=tailored_resume.rendered_filename,
    )
