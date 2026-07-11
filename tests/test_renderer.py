from app.services.renderer import html_to_pdf, render_html

SAMPLE_CONTEXT = {
    "contact": {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "location": "Remote",
        "links": [{"label": "GitHub", "url": "https://github.com/janedoe"}],
    },
    "experience": [
        {
            "company": "Acme Corp",
            "title": "Senior Engineer",
            "location": "Remote",
            "start_date": "2022-01",
            "end_date": None,
            "bullets": ["Shipped the tailoring engine", "Reduced latency by 40%"],
        }
    ],
    "projects": [
        {
            "name": "Resume Tailor",
            "description": "A resume tailoring tool",
            "tech_tags": ["Python", "React"],
            "link": "https://github.com/janedoe/resume-tailor",
            "bullets": ["Built the PDF rendering pipeline"],
        }
    ],
    "skills": [{"category": "Languages", "names": ["Python", "TypeScript"]}],
    "education": [
        {
            "institution": "State University",
            "degree": "B.S.",
            "field": "Computer Science",
            "start_date": "2018",
            "end_date": "2022",
            "gpa": "3.8",
        }
    ],
}


def test_render_html_includes_all_sections() -> None:
    html = render_html(SAMPLE_CONTEXT)

    assert "Jane Doe" in html
    assert "Acme Corp" in html
    assert "Shipped the tailoring engine" in html
    assert "Resume Tailor" in html
    assert "Python" in html
    assert "State University" in html


def test_render_html_shows_present_for_missing_end_date() -> None:
    html = render_html(SAMPLE_CONTEXT)
    assert "Present" in html


def test_render_html_escapes_untrusted_content() -> None:
    malicious_contact = {**SAMPLE_CONTEXT["contact"], "name": "<script>alert(1)</script>"}
    context = {**SAMPLE_CONTEXT, "contact": malicious_contact}
    html = render_html(context)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_html_to_pdf_produces_valid_pdf_bytes() -> None:
    html = render_html(SAMPLE_CONTEXT)
    pdf_bytes = html_to_pdf(html)
    assert pdf_bytes.startswith(b"%PDF")
