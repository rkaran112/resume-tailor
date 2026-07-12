import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from app.models.bullet import Bullet
from app.models.education import EducationEntry
from app.models.project import Project
from app.models.skill import Skill

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")

_STOPWORDS = frozenset(
    """
    a an the and or but in on at to for of with by from as is are was were
    be been being this that these those it its we you your our will shall
    can could should would may might must have has had do does did not no
    if then than so such into about over under per
    """.split()
)

_ALIAS_MAP = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "db": "database",
}

_TAG_WEIGHT = 2.0
_TEXT_WEIGHT = 1.0


def extract_keywords(jd_text: str) -> list[str]:
    lowered = jd_text.lower()
    raw_tokens = (match.rstrip(".") for match in _WORD_RE.findall(lowered))
    tokens = [
        _ALIAS_MAP.get(token, token) for token in raw_tokens if token and token not in _STOPWORDS
    ]
    bigrams = [f"{a} {b}" for a, b in zip(tokens, tokens[1:], strict=False)]

    seen: set[str] = set()
    keywords: list[str] = []
    for keyword in [*tokens, *bigrams]:
        if keyword not in seen:
            seen.add(keyword)
            keywords.append(keyword)
    return keywords


def _score_with_matches(
    text: str, tags: Sequence[str], jd_keywords: Sequence[str]
) -> tuple[float, list[str]]:
    text_lower = text.lower()
    tags_lower = {tag.lower() for tag in tags}
    score = 0.0
    matched: list[str] = []
    for keyword in jd_keywords:
        hit = False
        if keyword in tags_lower:
            score += _TAG_WEIGHT
            hit = True
        if keyword in text_lower:
            score += _TEXT_WEIGHT
            hit = True
        if hit:
            matched.append(keyword)
    return score, matched


def score_bullet(bullet: Bullet, jd_keywords: Sequence[str]) -> float:
    score, _ = _score_with_matches(bullet.text, bullet.tags, jd_keywords)
    return score


def score_skill(skill: Skill, jd_keywords: Sequence[str]) -> float:
    score, _ = _score_with_matches(skill.name, skill.tags, jd_keywords)
    return score


def score_project(project: Project, jd_keywords: Sequence[str]) -> float:
    text = f"{project.name} {project.description}"
    score, _ = _score_with_matches(text, project.tech_tags, jd_keywords)
    return score


@dataclass
class MatchResult:
    selected_experience_bullet_ids: list[int]
    selected_project_ids: list[int]
    selected_skill_ids: list[int]
    selected_education_ids: list[int]
    scoring_metadata: dict[str, dict[int, list[str]]] = field(default_factory=dict)


def match_bank_to_job_description(
    jd_keywords: Sequence[str],
    bullets: Sequence[Bullet],
    skills: Sequence[Skill],
    projects: Sequence[Project],
    education_entries: Sequence[EducationEntry],
    bullets_per_experience_entry: int = 3,
    max_skills: int = 6,
    max_projects: int = 2,
) -> MatchResult:
    """Selects bank content for a JD. Experience entries and education entries are always
    included wholesale (there's nothing to filter them by); only their attached bullets
    (for experience entries) and skills/projects are ranked and capped by keyword overlap.
    A project's own bullets ride along automatically once the project is selected.
    """
    scoring_metadata: dict[str, dict[int, list[str]]] = {
        "bullets": {},
        "skills": {},
        "projects": {},
    }

    bullets_by_experience_entry: dict[int, list[Bullet]] = {}
    for bullet in bullets:
        if bullet.experience_entry_id is not None:
            bullets_by_experience_entry.setdefault(bullet.experience_entry_id, []).append(bullet)

    selected_experience_bullet_ids: list[int] = []
    for entry_bullets in bullets_by_experience_entry.values():
        scored_bullets = [
            (*_score_with_matches(bullet.text, bullet.tags, jd_keywords), bullet)
            for bullet in entry_bullets
        ]
        scored_bullets.sort(key=lambda item: item[0], reverse=True)
        for _score, matched, bullet in scored_bullets[:bullets_per_experience_entry]:
            selected_experience_bullet_ids.append(bullet.id)
            scoring_metadata["bullets"][bullet.id] = matched

    scored_skills = [
        (*_score_with_matches(skill.name, skill.tags, jd_keywords), skill) for skill in skills
    ]
    scored_skills.sort(key=lambda item: item[0], reverse=True)
    selected_skill_ids: list[int] = []
    for _score, matched, skill in scored_skills[:max_skills]:
        selected_skill_ids.append(skill.id)
        scoring_metadata["skills"][skill.id] = matched

    scored_projects = [
        (
            *_score_with_matches(
                f"{project.name} {project.description}", project.tech_tags, jd_keywords
            ),
            project,
        )
        for project in projects
    ]
    scored_projects.sort(key=lambda item: item[0], reverse=True)
    selected_project_ids: list[int] = []
    for _score, matched, project in scored_projects[:max_projects]:
        selected_project_ids.append(project.id)
        scoring_metadata["projects"][project.id] = matched

    selected_education_ids = [entry.id for entry in education_entries]

    return MatchResult(
        selected_experience_bullet_ids=selected_experience_bullet_ids,
        selected_project_ids=selected_project_ids,
        selected_skill_ids=selected_skill_ids,
        selected_education_ids=selected_education_ids,
        scoring_metadata=scoring_metadata,
    )
