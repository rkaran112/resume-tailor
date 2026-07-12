from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.db.session import get_db
from app.models.application import Application
from app.models.application_status_event import ApplicationStatusEvent
from app.models.cover_letter import CoverLetter
from app.models.job_description import JobDescription
from app.models.tailored_resume import TailoredResume
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusChange,
    ApplicationStatusEventRead,
    ApplicationUpdate,
)

router = APIRouter(tags=["applications"])


def _status_events_for(db: Session, application_id: int) -> list[ApplicationStatusEvent]:
    return list(
        db.query(ApplicationStatusEvent)
        .filter(ApplicationStatusEvent.application_id == application_id)
        .order_by(ApplicationStatusEvent.changed_at)
        .all()
    )


def _to_read(
    application: Application, status_events: list[ApplicationStatusEvent]
) -> ApplicationRead:
    return ApplicationRead(
        id=application.id,
        tailored_resume_id=application.tailored_resume_id,
        cover_letter_id=application.cover_letter_id,
        job_description_id=application.job_description_id,
        company=application.company,
        role_title=application.role_title,
        date_applied=application.date_applied,
        status=application.status,
        notes=application.notes,
        created_at=application.created_at,
        updated_at=application.updated_at,
        status_events=[ApplicationStatusEventRead.model_validate(e) for e in status_events],
    )


@router.get("/applications", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db)) -> list[ApplicationRead]:
    applications = db.query(Application).order_by(Application.date_applied.desc()).all()
    return [
        _to_read(application, _status_events_for(db, application.id))
        for application in applications
    ]


@router.post("/applications", response_model=ApplicationRead, status_code=201)
def create_application(
    payload: ApplicationCreate, db: Session = Depends(get_db)
) -> ApplicationRead:
    get_or_404(db, JobDescription, payload.job_description_id)
    if payload.tailored_resume_id is not None:
        get_or_404(db, TailoredResume, payload.tailored_resume_id)
    if payload.cover_letter_id is not None:
        get_or_404(db, CoverLetter, payload.cover_letter_id)

    application = Application(
        tailored_resume_id=payload.tailored_resume_id,
        cover_letter_id=payload.cover_letter_id,
        job_description_id=payload.job_description_id,
        company=payload.company,
        role_title=payload.role_title,
        date_applied=payload.date_applied,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(application)
    db.flush()

    db.add(ApplicationStatusEvent(application_id=application.id, status=payload.status))
    db.commit()
    db.refresh(application)

    return _to_read(application, _status_events_for(db, application.id))


@router.get("/applications/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)) -> ApplicationRead:
    application = get_or_404(db, Application, application_id)
    return _to_read(application, _status_events_for(db, application.id))


@router.patch("/applications/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)
) -> ApplicationRead:
    application = get_or_404(db, Application, application_id)
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("cover_letter_id") is not None:
        get_or_404(db, CoverLetter, updates["cover_letter_id"])
    for field, value in updates.items():
        setattr(application, field, value)
    db.commit()
    db.refresh(application)
    return _to_read(application, _status_events_for(db, application.id))


@router.post("/applications/{application_id}/status", response_model=ApplicationRead)
def change_application_status(
    application_id: int, payload: ApplicationStatusChange, db: Session = Depends(get_db)
) -> ApplicationRead:
    application = get_or_404(db, Application, application_id)
    application.status = payload.status
    db.add(
        ApplicationStatusEvent(
            application_id=application.id, status=payload.status, note=payload.note
        )
    )
    db.commit()
    db.refresh(application)
    return _to_read(application, _status_events_for(db, application.id))
