from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.api.deps import get_or_404, get_or_create_contact_info, resolve_tailored_resume_content
from app.core.config import get_settings
from app.db.session import get_db
from app.models.cover_letter import CoverLetter
from app.models.job_description import JobDescription
from app.models.tailored_resume import TailoredResume
from app.schemas.cover_letter import CoverLetterCreate, CoverLetterRead, CoverLetterUpdate
from app.services.cover_letter_gen import generate_cover_letter
from app.services.filename import build_filename
from app.services.renderer import html_to_pdf, render_html
from app.services.resolve import split_full_name

router = APIRouter(tags=["cover-letters"])

_COVER_LETTER_TEMPLATE = "cover_letter_template.html"


def _active_text(cover_letter: CoverLetter) -> str:
    return (
        cover_letter.edited_text
        if cover_letter.edited_text is not None
        else cover_letter.generated_text
    )


def _build_context(
    db: Session, cover_letter: CoverLetter, job_description: JobDescription
) -> dict[str, Any]:
    contact = get_or_create_contact_info(db)
    body_text = _active_text(cover_letter)
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    return {
        "contact": {
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
            "location": contact.location,
            "links": list(contact.links),
        },
        "company": job_description.company,
        "role_title": job_description.role_title,
        "date": datetime.now(UTC).strftime("%B %d, %Y"),
        "body_paragraphs": paragraphs,
    }


@router.get("/cover-letters", response_model=list[CoverLetterRead])
def list_cover_letters(db: Session = Depends(get_db)) -> list[CoverLetter]:
    return list(db.query(CoverLetter).order_by(CoverLetter.id.desc()).all())


@router.post("/cover-letters", response_model=CoverLetterRead, status_code=201)
def create_cover_letter(
    payload: CoverLetterCreate, db: Session = Depends(get_db)
) -> CoverLetter:
    if not get_settings().enable_cover_letter:
        raise HTTPException(status_code=503, detail="Cover letter generation is disabled")

    tailored_resume = get_or_404(db, TailoredResume, payload.tailored_resume_id)
    job_description = get_or_404(db, JobDescription, tailored_resume.job_description_id)

    resolved_content = tailored_resume.resolved_content
    if resolved_content is None:
        resolved_content = resolve_tailored_resume_content(db, tailored_resume)

    paragraphs = generate_cover_letter(job_description.raw_text, resolved_content)
    generated_text = "\n\n".join(paragraphs)

    cover_letter = CoverLetter(
        tailored_resume_id=tailored_resume.id,
        job_description_id=job_description.id,
        generated_text=generated_text,
        llm_generated=True,
    )
    db.add(cover_letter)
    db.commit()
    db.refresh(cover_letter)
    return cover_letter


@router.get("/cover-letters/{cover_letter_id}", response_model=CoverLetterRead)
def get_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)) -> CoverLetter:
    return get_or_404(db, CoverLetter, cover_letter_id)


@router.patch("/cover-letters/{cover_letter_id}", response_model=CoverLetterRead)
def update_cover_letter(
    cover_letter_id: int, payload: CoverLetterUpdate, db: Session = Depends(get_db)
) -> CoverLetter:
    cover_letter = get_or_404(db, CoverLetter, cover_letter_id)
    if cover_letter.status == "finalized":
        raise HTTPException(status_code=409, detail="Cannot edit a finalized cover letter")
    cover_letter.edited_text = payload.edited_text
    db.commit()
    db.refresh(cover_letter)
    return cover_letter


@router.get("/cover-letters/{cover_letter_id}/preview", response_class=HTMLResponse)
def preview_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)) -> str:
    cover_letter = get_or_404(db, CoverLetter, cover_letter_id)
    job_description = get_or_404(db, JobDescription, cover_letter.job_description_id)
    context = _build_context(db, cover_letter, job_description)
    return render_html(context, template_name=_COVER_LETTER_TEMPLATE)


@router.post("/cover-letters/{cover_letter_id}/finalize", response_model=CoverLetterRead)
def finalize_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)) -> CoverLetter:
    cover_letter = get_or_404(db, CoverLetter, cover_letter_id)
    if cover_letter.status == "finalized":
        raise HTTPException(status_code=409, detail="Cover letter is already finalized")

    job_description = get_or_404(db, JobDescription, cover_letter.job_description_id)
    contact = get_or_create_contact_info(db)
    context = _build_context(db, cover_letter, job_description)

    html = render_html(context, template_name=_COVER_LETTER_TEMPLATE)
    pdf_bytes = html_to_pdf(html)

    first, last = split_full_name(contact.name)
    filename = build_filename(
        first, last, "CoverLetter", job_description.company, job_description.role_title
    )

    output_dir = Path(get_settings().generated_resumes_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = (output_dir / filename).resolve()
    output_path.write_bytes(pdf_bytes)

    cover_letter.rendered_pdf_path = str(output_path)
    cover_letter.rendered_filename = filename
    cover_letter.status = "finalized"
    cover_letter.finalized_at = datetime.now(UTC)

    db.commit()
    db.refresh(cover_letter)
    return cover_letter


@router.get("/cover-letters/{cover_letter_id}/download")
def download_cover_letter(cover_letter_id: int, db: Session = Depends(get_db)) -> FileResponse:
    cover_letter = get_or_404(db, CoverLetter, cover_letter_id)
    if cover_letter.status != "finalized" or not cover_letter.rendered_pdf_path:
        raise HTTPException(status_code=409, detail="Cover letter is not finalized yet")
    return FileResponse(
        cover_letter.rendered_pdf_path,
        media_type="application/pdf",
        filename=cover_letter.rendered_filename,
    )
