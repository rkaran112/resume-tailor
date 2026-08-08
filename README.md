# resume-tailor

Resume/CV tailoring and job-application tracking tool.

Separates content selection (a deterministic, explainable keyword-matching engine, with an
opt-in Claude-powered rewrite pass) from rendering (one fixed, hand-approved HTML/CSS template
rendered to PDF via headless Chromium) — so formatting is solved once and never re-gambled on
a per-resume basis.

See `docs/DESIGN.md` for the full engineering design and build-order roadmap, and `DESIGN.md`
for the visual design system (typography, color, layout, motion).

Status: all 8 slices are implemented (bank CRUD, PDF rendering, matching engine, tailoring +
finalize/export, application tracker, opt-in LLM bullet enhancement, opt-in cover letter
generation, opt-in resume import), plus a post-V1 extension adding LaTeX resume import and
duplicate detection, and a motion/animation pass on the frontend. See `docs/DESIGN.md` for the
full build history.

## Setup

```
docker compose up -d db
uv sync
uv run playwright install chromium
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

```
cd frontend
npm install
npm run dev
```

## Commands

- `uv run ruff check .` / `uv run mypy app` / `uv run pytest` — lint / type-check / test
- `uv run python scripts/render_sample_resume.py` — render a hardcoded sample resume to
  `scratch/sample_resume.html` and `scratch/sample_resume.pdf`, for visually reviewing
  `app/templates/resume_template.html`
- `cd frontend && npm run lint && npm run build` — lint / type-check / build the frontend

## LLM bullet enhancement (opt-in)

Set `ENABLE_LLM_ENHANCE=true` and an `ANTHROPIC_API_KEY` (or run `ant auth login`) to turn on
`POST /tailored-resumes/{id}/enhance`. Off by default — the app works fully with no API key.

## Cover letter generation (opt-in)

Set `ENABLE_COVER_LETTER=true` and an `ANTHROPIC_API_KEY` (or run `ant auth login`) to turn on
`POST /cover-letters`. Off by default — the app works fully with no API key. Generation is
grounded strictly in the tailored resume's already-selected content (never the full bank) and
the job description.

## Resume import (opt-in)

Set `ENABLE_RESUME_IMPORT=true` and an `ANTHROPIC_API_KEY` (or run `ant auth login`) to turn on
`POST /bank/import`. Off by default — the app works fully with no API key, and bank data can
always be entered manually via the Bank tab. Drop a PDF **or LaTeX (`.tex`)** resume onto the
"Import from resume" panel to extract contact info, experience, skills, projects, and education
into a reviewable preview — nothing is written to the bank until you uncheck anything you don't
want and click "Add to bank". Extraction is grounded strictly in the document (no invented
employers/dates/skills). Items that already look like they're in your bank (matched by name/
company/text) are flagged and unchecked by default; importing the same resume twice still
creates duplicate rows for anything you leave checked (no merge-on-commit) — delete extras via
the Bank tab if that happens.

## Deploying

`render.yaml` + `Dockerfile` are set up for a one-click [Render](https://render.com) Blueprint
deploy: free Postgres + the FastAPI backend (Docker, migrations run on boot) + the React
frontend as a static site. In the Render dashboard: **New → Blueprint**, pick this repo. The
free-tier deploy ships with LLM features (enhance / cover letter / import) off — no Anthropic
key is wired in by default — and PDF export's headless-Chromium dependency is left out to fit
the free web-instance size; both are easy to add back on a paid plan. See the comments in
`render.yaml` for specifics, including the free Postgres plan's 90-day/30-day-idle limits.
