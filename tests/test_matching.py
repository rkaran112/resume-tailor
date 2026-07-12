from datetime import date

from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.project import Project
from app.models.skill import Skill
from app.services.matching import (
    extract_keywords,
    match_bank_to_job_description,
    score_bullet,
    score_project,
    score_skill,
)


def test_extract_keywords_lowercases_strips_stopwords_and_dedupes() -> None:
    keywords = extract_keywords("The Python developer will use Python and SQL.")
    assert "python" in keywords
    assert "sql" in keywords
    assert "the" not in keywords
    assert "and" not in keywords
    assert keywords.count("python") == 1


def test_extract_keywords_produces_bigrams() -> None:
    keywords = extract_keywords("Experience with machine learning required.")
    assert "machine learning" in keywords


def test_extract_keywords_applies_alias_map() -> None:
    keywords = extract_keywords("Strong JS and TS skills required.")
    assert "javascript" in keywords
    assert "typescript" in keywords
    assert "js" not in keywords


def test_score_bullet_weights_tag_match_above_text_match() -> None:
    tag_matching_bullet = Bullet(id=1, experience_entry_id=1, text="Did some work", tags=["python"])
    text_matching_bullet = Bullet(id=2, experience_entry_id=1, text="Wrote python scripts", tags=[])

    tag_score = score_bullet(tag_matching_bullet, ["python"])
    text_score = score_bullet(text_matching_bullet, ["python"])

    assert tag_score > text_score


def test_score_skill_and_score_project_use_name_and_tags() -> None:
    skill = Skill(id=1, name="Python", category="language", tags=["backend"])
    project = Project(
        id=1, name="API Service", description="A Python backend", tech_tags=["python"]
    )

    assert score_skill(skill, ["python"]) > 0
    assert score_project(project, ["python"]) > 0
    assert score_skill(skill, ["golang"]) == 0
    assert score_project(project, ["golang"]) == 0


def test_match_bank_to_job_description_selects_exact_ids() -> None:
    bullets = [
        Bullet(id=1, experience_entry_id=10, text="Built Python APIs", tags=["python"]),
        Bullet(id=2, experience_entry_id=10, text="Wrote documentation", tags=[]),
        Bullet(id=3, experience_entry_id=10, text="Used Python for scripting", tags=["python"]),
        Bullet(id=4, experience_entry_id=10, text="Organized team lunches", tags=[]),
    ]
    skills = [
        Skill(id=100, name="Python", category="language", tags=["backend"]),
        Skill(id=101, name="Excel", category="tool", tags=[]),
    ]
    projects = [
        Project(id=200, name="Resume Tailor", description="Python tool", tech_tags=["python"]),
        Project(id=201, name="Recipe Blog", description="A cooking blog", tech_tags=["wordpress"]),
    ]
    education = [
        EducationEntry(
            id=300, institution="State U", degree="B.S.", field="CS", start_date=date(2018, 1, 1)
        )
    ]

    result = match_bank_to_job_description(
        jd_keywords=["python"],
        bullets=bullets,
        skills=skills,
        projects=projects,
        education_entries=education,
        bullets_per_experience_entry=2,
        max_skills=1,
        max_projects=1,
    )

    assert result.selected_experience_bullet_ids == [1, 3]
    assert result.selected_skill_ids == [100]
    assert result.selected_project_ids == [200]
    assert result.selected_education_ids == [300]
    assert result.scoring_metadata["bullets"][1] == ["python"]
    assert result.scoring_metadata["skills"][100] == ["python"]
    assert result.scoring_metadata["projects"][200] == ["python"]
