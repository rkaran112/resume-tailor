# resume-tailor

Resume/CV tailoring and job-application tracking tool.

Separates content selection (a deterministic, explainable keyword-matching engine, with an
opt-in Claude-powered rewrite pass) from rendering (one fixed, hand-approved HTML/CSS template
rendered to PDF via headless Chromium) — so formatting is solved once and never re-gambled on
a per-resume basis.

See `docs/DESIGN.md` for the full design and build-order roadmap.

Status: all 7 slices are implemented (bank CRUD, PDF rendering, matching engine, tailoring +
finalize/export, application tracker, opt-in LLM bullet enhancement, opt-in cover letter
generation). See `docs/DESIGN.md` for the full build history.

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
