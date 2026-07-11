# resume-tailor

Resume/CV tailoring and job-application tracking tool.

Separates content selection (a deterministic, explainable keyword-matching engine, with an
opt-in Claude-powered rewrite pass) from rendering (one fixed, hand-approved HTML/CSS template
rendered to PDF via headless Chromium) — so formatting is solved once and never re-gambled on
a per-resume basis.

See `docs/DESIGN.md` for the full design and build-order roadmap.

Status: Slice 1 (bank CRUD) and Slice 2 (PDF rendering pipeline) are implemented.

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
