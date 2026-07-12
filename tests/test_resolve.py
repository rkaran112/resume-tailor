from datetime import date

from app.models.bullet import Bullet
from app.models.contact import ContactInfo
from app.models.education import EducationEntry
from app.models.experience import ExperienceEntry
from app.models.project import Project
from app.models.skill import Skill
from app.services.resolve import build_resolved_content, split_full_name


def test_split_full_name_basic() -> None:
    assert split_full_name("Jane Doe") == ("Jane", "Doe")


def test_split_full_name_multi_word_last() -> None:
    assert split_full_name("Jane Van Der Berg") == ("Jane", "Van Der Berg")


def test_split_full_name_single_word() -> None:
    assert split_full_name("Cher") == ("Cher", "")


def test_build_resolved_content_filters_by_selection() -> None:
    contact = ContactInfo(
        id=1,
        name="Jane Doe",
        email="jane@example.com",
        phone="555-1234",
        location="Remote",
        links=[{"label": "GitHub", "url": "https://github.com/janedoe"}],
    )
    experience_entries = [
        ExperienceEntry(
            id=1,
            company="Acme",
            title="Engineer",
            location="Remote",
            start_date=date(2022, 1, 1),
            end_date=None,
            display_order=0,
        )
    ]
    bullets = [
        Bullet(id=10, experience_entry_id=1, text="Selected bullet", tags=[]),
        Bullet(id=11, experience_entry_id=1, text="Unselected bullet", tags=[]),
        Bullet(id=12, project_id=1, text="Project bullet", tags=[]),
    ]
    projects = [
        Project(
            id=1,
            name="Resume Tailor",
            description="desc",
            tech_tags=["python"],
            display_order=0,
        ),
        Project(
            id=2, name="Unselected Project", description="desc", tech_tags=[], display_order=1
        ),
    ]
    skills = [
        Skill(id=1, name="Python", category="Languages", tags=[]),
        Skill(id=2, name="SQL", category="Languages", tags=[]),
        Skill(id=3, name="Excel", category="Tools", tags=[]),
    ]
    education_entries = [
        EducationEntry(
            id=1, institution="State U", degree="B.S.", field="CS", start_date=date(2018, 1, 1)
        )
    ]

    result = build_resolved_content(
        contact_info=contact,
        experience_entries=experience_entries,
        bullets=bullets,
        projects=projects,
        skills=skills,
        education_entries=education_entries,
        selected_experience_bullet_ids=[10],
        selected_project_ids=[1],
        selected_skill_ids=[1, 2],
        selected_education_ids=[1],
    )

    assert result["contact"]["name"] == "Jane Doe"
    assert result["experience"][0]["bullets"] == ["Selected bullet"]
    assert result["experience"][0]["start_date"] == "Jan 2022"
    assert result["experience"][0]["end_date"] is None

    assert [p["name"] for p in result["projects"]] == ["Resume Tailor"]
    assert result["projects"][0]["bullets"] == ["Project bullet"]

    assert result["skills"] == [{"category": "Languages", "names": ["Python", "SQL"]}]

    assert len(result["education"]) == 1
    assert result["education"][0]["institution"] == "State U"
