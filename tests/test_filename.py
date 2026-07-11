from app.services.filename import build_filename


def test_basic_resume_filename() -> None:
    result = build_filename("Jane", "Doe", "Resume", "Acme Corp", "Software Engineer")
    assert result == "Jane_Doe_Resume_Acme_Corp_Software_Engineer.pdf"


def test_basic_cover_letter_filename() -> None:
    result = build_filename("Jane", "Doe", "CoverLetter", "Acme Corp", "Software Engineer")
    assert result == "Jane_Doe_CoverLetter_Acme_Corp_Software_Engineer.pdf"


def test_strips_filesystem_unsafe_chars_but_keeps_ampersand() -> None:
    result = build_filename("Jane", "Doe", "Resume", "Acme/Co & Sons", "R&D: Lead")
    assert "/" not in result
    assert ":" not in result
    assert "Acme_Co_&_Sons" in result
    assert "R&D_Lead" in result


def test_collapses_extra_whitespace() -> None:
    result = build_filename("Jane", "Doe", "Resume", "  Extra   Space   Co  ", "Engineer")
    assert "Extra_Space_Co" in result
    assert "__" not in result


def test_normalizes_unicode_to_ascii() -> None:
    result = build_filename("José", "Núñez", "Resume", "Acme", "Engineer")
    assert result == "Jose_Nunez_Resume_Acme_Engineer.pdf"


def test_truncates_very_long_components() -> None:
    long_title = "Senior " + "Very " * 30 + "Long Title"
    result = build_filename("Jane", "Doe", "Resume", "Acme", long_title)
    # each sanitized component is capped at 60 chars before joining
    role_component = result.removeprefix("Jane_Doe_Resume_Acme_").removesuffix(".pdf")
    assert len(role_component) <= 60
