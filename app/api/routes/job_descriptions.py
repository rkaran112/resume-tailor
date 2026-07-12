from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.db.session import get_db
from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.job_description import JobDescription
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionRead,
    MatchRequest,
    MatchResponse,
)
from app.services.matching import extract_keywords, match_bank_to_job_description

router = APIRouter(tags=["job-descriptions"])


@router.get("/job-descriptions", response_model=list[JobDescriptionRead])
def list_job_descriptions(db: Session = Depends(get_db)) -> list[JobDescription]:
    return list(db.query(JobDescription).order_by(JobDescription.id.desc()).all())


@router.post("/job-descriptions", response_model=JobDescriptionRead, status_code=201)
def create_job_description(
    payload: JobDescriptionCreate, db: Session = Depends(get_db)
) -> JobDescription:
    job_description = JobDescription(
        company=payload.company,
        role_title=payload.role_title,
        raw_text=payload.raw_text,
        extracted_keywords=extract_keywords(payload.raw_text),
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    return job_description


@router.get("/job-descriptions/{job_description_id}", response_model=JobDescriptionRead)
def get_job_description(job_description_id: int, db: Session = Depends(get_db)) -> JobDescription:
    return get_or_404(db, JobDescription, job_description_id)


@router.post("/job-descriptions/{job_description_id}/match", response_model=MatchResponse)
def match_job_description(
    job_description_id: int, payload: MatchRequest, db: Session = Depends(get_db)
) -> MatchResponse:
    job_description = get_or_404(db, JobDescription, job_description_id)

    bullets = list(db.query(Bullet).filter(Bullet.is_active.is_(True)).all())
    skills = list(db.query(Skill).all())
    projects = list(db.query(Project).all())
    education_entries = list(db.query(EducationEntry).all())

    result = match_bank_to_job_description(
        jd_keywords=job_description.extracted_keywords,
        bullets=bullets,
        skills=skills,
        projects=projects,
        education_entries=education_entries,
        bullets_per_experience_entry=payload.bullets_per_experience_entry,
        max_skills=payload.max_skills,
        max_projects=payload.max_projects,
    )
    return MatchResponse(
        selected_experience_bullet_ids=result.selected_experience_bullet_ids,
        selected_project_ids=result.selected_project_ids,
        selected_skill_ids=result.selected_skill_ids,
        selected_education_ids=result.selected_education_ids,
        scoring_metadata=result.scoring_metadata,
    )
