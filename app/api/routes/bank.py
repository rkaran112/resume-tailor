from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.bullet import Bullet
from app.models.contact import ContactInfo
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.schemas.bullet import BulletBase, BulletCreate, BulletRead, BulletUpdate
from app.schemas.contact import ContactInfoRead, ContactInfoUpsert
from app.schemas.education import (
    EducationEntryCreate,
    EducationEntryRead,
    EducationEntryUpdate,
)
from app.schemas.experience import (
    ExperienceEntryCreate,
    ExperienceEntryRead,
    ExperienceEntryUpdate,
)
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.skill import SkillCreate, SkillRead, SkillUpdate

router = APIRouter(tags=["bank"])

CONTACT_INFO_ID = 1

ModelT = TypeVar("ModelT")


def _get_or_404(db: Session, model: type[ModelT], obj_id: int) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {obj_id} not found")
    return obj


# ---- Skills ----


@router.get("/skills", response_model=list[SkillRead])
def list_skills(db: Session = Depends(get_db)) -> list[Skill]:
    return list(db.query(Skill).order_by(Skill.id).all())


@router.post("/skills", response_model=SkillRead, status_code=201)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)) -> Skill:
    skill = Skill(**payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/skills/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: int, db: Session = Depends(get_db)) -> Skill:
    return _get_or_404(db, Skill, skill_id)


@router.patch("/skills/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: int, payload: SkillUpdate, db: Session = Depends(get_db)) -> Skill:
    skill = _get_or_404(db, Skill, skill_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db)) -> None:
    skill = _get_or_404(db, Skill, skill_id)
    db.delete(skill)
    db.commit()


# ---- Experience entries ----


@router.get("/experience-entries", response_model=list[ExperienceEntryRead])
def list_experience_entries(db: Session = Depends(get_db)) -> list[ExperienceEntry]:
    return list(db.query(ExperienceEntry).order_by(ExperienceEntry.display_order).all())


@router.post("/experience-entries", response_model=ExperienceEntryRead, status_code=201)
def create_experience_entry(
    payload: ExperienceEntryCreate, db: Session = Depends(get_db)
) -> ExperienceEntry:
    entry = ExperienceEntry(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/experience-entries/{entry_id}", response_model=ExperienceEntryRead)
def get_experience_entry(entry_id: int, db: Session = Depends(get_db)) -> ExperienceEntry:
    return _get_or_404(db, ExperienceEntry, entry_id)


@router.patch("/experience-entries/{entry_id}", response_model=ExperienceEntryRead)
def update_experience_entry(
    entry_id: int, payload: ExperienceEntryUpdate, db: Session = Depends(get_db)
) -> ExperienceEntry:
    entry = _get_or_404(db, ExperienceEntry, entry_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/experience-entries/{entry_id}", status_code=204)
def delete_experience_entry(entry_id: int, db: Session = Depends(get_db)) -> None:
    entry = _get_or_404(db, ExperienceEntry, entry_id)
    db.delete(entry)
    db.commit()


# ---- Projects ----


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return list(db.query(Project).order_by(Project.display_order).all())


@router.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    return _get_or_404(db, Project, project_id)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)
) -> Project:
    project = _get_or_404(db, Project, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> None:
    project = _get_or_404(db, Project, project_id)
    db.delete(project)
    db.commit()


# ---- Education entries ----


@router.get("/education-entries", response_model=list[EducationEntryRead])
def list_education_entries(db: Session = Depends(get_db)) -> list[EducationEntry]:
    return list(db.query(EducationEntry).order_by(EducationEntry.id).all())


@router.post("/education-entries", response_model=EducationEntryRead, status_code=201)
def create_education_entry(
    payload: EducationEntryCreate, db: Session = Depends(get_db)
) -> EducationEntry:
    entry = EducationEntry(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/education-entries/{entry_id}", response_model=EducationEntryRead)
def get_education_entry(entry_id: int, db: Session = Depends(get_db)) -> EducationEntry:
    return _get_or_404(db, EducationEntry, entry_id)


@router.patch("/education-entries/{entry_id}", response_model=EducationEntryRead)
def update_education_entry(
    entry_id: int, payload: EducationEntryUpdate, db: Session = Depends(get_db)
) -> EducationEntry:
    entry = _get_or_404(db, EducationEntry, entry_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/education-entries/{entry_id}", status_code=204)
def delete_education_entry(entry_id: int, db: Session = Depends(get_db)) -> None:
    entry = _get_or_404(db, EducationEntry, entry_id)
    db.delete(entry)
    db.commit()


# ---- Bullets ----


@router.get("/bullets", response_model=list[BulletRead])
def list_bullets(db: Session = Depends(get_db)) -> list[Bullet]:
    return list(db.query(Bullet).order_by(Bullet.id).all())


@router.post("/bullets", response_model=BulletRead, status_code=201)
def create_bullet(payload: BulletCreate, db: Session = Depends(get_db)) -> Bullet:
    bullet = Bullet(**payload.model_dump())
    db.add(bullet)
    db.commit()
    db.refresh(bullet)
    return bullet


@router.get("/bullets/{bullet_id}", response_model=BulletRead)
def get_bullet(bullet_id: int, db: Session = Depends(get_db)) -> Bullet:
    return _get_or_404(db, Bullet, bullet_id)


@router.patch("/bullets/{bullet_id}", response_model=BulletRead)
def update_bullet(bullet_id: int, payload: BulletUpdate, db: Session = Depends(get_db)) -> Bullet:
    bullet = _get_or_404(db, Bullet, bullet_id)
    updates = payload.model_dump(exclude_unset=True)
    merged = {
        "experience_entry_id": bullet.experience_entry_id,
        "project_id": bullet.project_id,
        "text": bullet.text,
        "tags": bullet.tags,
        "impact_metric": bullet.impact_metric,
        "is_active": bullet.is_active,
        **updates,
    }
    try:
        BulletBase(**merged)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    for field, value in updates.items():
        setattr(bullet, field, value)
    db.commit()
    db.refresh(bullet)
    return bullet


@router.delete("/bullets/{bullet_id}", status_code=204)
def delete_bullet(bullet_id: int, db: Session = Depends(get_db)) -> None:
    bullet = _get_or_404(db, Bullet, bullet_id)
    db.delete(bullet)
    db.commit()


# ---- Contact info (singleton) ----


@router.get("/contact-info", response_model=ContactInfoRead)
def get_contact_info(db: Session = Depends(get_db)) -> ContactInfo:
    contact = db.get(ContactInfo, CONTACT_INFO_ID)
    if contact is None:
        contact = ContactInfo(
            id=CONTACT_INFO_ID, name="", email="", phone="", location="", links=[]
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


@router.put("/contact-info", response_model=ContactInfoRead)
def upsert_contact_info(
    payload: ContactInfoUpsert, db: Session = Depends(get_db)
) -> ContactInfo:
    contact = db.get(ContactInfo, CONTACT_INFO_ID)
    data = payload.model_dump()
    data["links"] = [link for link in data["links"]]
    if contact is None:
        contact = ContactInfo(id=CONTACT_INFO_ID, **data)
        db.add(contact)
    else:
        for field, value in data.items():
            setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact
