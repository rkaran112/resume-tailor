"""Renders a hardcoded sample resume to HTML and PDF for visual review of resume_template.html.

Usage: uv run python scripts/render_sample_resume.py
"""

from pathlib import Path

from app.services.renderer import html_to_pdf, render_html

SAMPLE_CONTEXT = {
    "contact": {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "(555) 123-4567",
        "location": "Remote",
        "links": [
            {"label": "GitHub", "url": "https://github.com/janedoe"},
            {"label": "LinkedIn", "url": "https://linkedin.com/in/janedoe"},
        ],
    },
    "experience": [
        {
            "company": "Acme Corp",
            "title": "Senior Software Engineer",
            "location": "Remote",
            "start_date": "Jan 2022",
            "end_date": None,
            "bullets": [
                "Designed and shipped a deterministic content-matching engine that tailors "
                "resume bullets to job descriptions, replacing a fully manual process",
                "Reduced API p95 latency by 40% by introducing connection pooling and query "
                "batching across the core service",
                "Mentored two junior engineers, both promoted within a year",
            ],
        },
        {
            "company": "Globex Inc",
            "title": "Software Engineer",
            "location": "New York, NY",
            "start_date": "Jun 2019",
            "end_date": "Dec 2021",
            "bullets": [
                "Built an internal analytics dashboard used by 200+ employees daily",
                "Migrated a legacy monolith to a service-oriented architecture",
            ],
        },
    ],
    "projects": [
        {
            "name": "Resume Tailor",
            "description": "A deterministic resume tailoring and job-application tracker.",
            "tech_tags": ["Python", "FastAPI", "React", "Playwright"],
            "link": "https://github.com/janedoe/resume-tailor",
            "bullets": ["Built the fixed HTML/CSS-to-PDF rendering pipeline"],
        },
    ],
    "skills": [
        {"category": "Languages", "names": ["Python", "TypeScript", "SQL"]},
        {"category": "Frameworks", "names": ["FastAPI", "React", "SQLAlchemy"]},
        {"category": "Tools", "names": ["Docker", "Postgres", "GitHub Actions"]},
    ],
    "education": [
        {
            "institution": "State University",
            "degree": "B.S.",
            "field": "Computer Science",
            "start_date": "2015",
            "end_date": "2019",
            "gpa": "3.8",
        },
    ],
}


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent / "scratch"
    output_dir.mkdir(exist_ok=True)

    html = render_html(SAMPLE_CONTEXT)
    (output_dir / "sample_resume.html").write_text(html, encoding="utf-8")

    pdf_bytes = html_to_pdf(html)
    (output_dir / "sample_resume.pdf").write_bytes(pdf_bytes)

    print(f"Wrote {output_dir / 'sample_resume.html'}")
    print(f"Wrote {output_dir / 'sample_resume.pdf'}")


if __name__ == "__main__":
    main()
