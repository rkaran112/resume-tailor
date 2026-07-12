from datetime import date

from pydantic import BaseModel


class ImportedContactLink(BaseModel):
    label: str
    url: str


class ImportedContact(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    links: list[ImportedContactLink] = []
    include: bool = True


class ImportedBullet(BaseModel):
    text: str
    tags: list[str] = []
    include: bool = True


class ImportedExperienceEntry(BaseModel):
    company: str
    title: str
    location: str
    start_date: date
    end_date: date | None = None
    bullets: list[ImportedBullet] = []
    include: bool = True


class ImportedSkill(BaseModel):
    name: str
    category: str
    tags: list[str] = []
    include: bool = True


class ImportedProject(BaseModel):
    name: str
    description: str
    tech_tags: list[str] = []
    bullets: list[ImportedBullet] = []
    include: bool = True


class ImportedEducationEntry(BaseModel):
    institution: str
    degree: str
    field: str
    start_date: date
    end_date: date | None = None
    include: bool = True


class ResumeImportPreview(BaseModel):
    contact: ImportedContact
    experience: list[ImportedExperienceEntry] = []
    skills: list[ImportedSkill] = []
    projects: list[ImportedProject] = []
    education: list[ImportedEducationEntry] = []


class ResumeImportCommitResult(BaseModel):
    contact_updated: bool
    experience_entries_created: int
    bullets_created: int
    skills_created: int
    projects_created: int
    education_entries_created: int
