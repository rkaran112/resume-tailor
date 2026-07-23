# API image: FastAPI + SQLAlchemy, built with uv. Runs Alembic migrations on
# boot, then serves the app. Playwright is installed as a Python dependency
# but its Chromium browser is intentionally NOT downloaded here — PDF export
# needs it, but it's too heavy for a free-tier box, so the rest of the API
# runs and only the PDF-render endpoint degrades. Install the browser
# (`playwright install --with-deps chromium`) on a larger instance to enable it.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# uv, copied from its published image (no curl|sh bootstrap needed).
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

# Install deps + the app itself (hatchling needs the source present).
COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x /app/deploy/entrypoint.sh

EXPOSE 8000

CMD ["/app/deploy/entrypoint.sh"]
