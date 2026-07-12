import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes.applications import router as applications_router
from app.api.routes.bank import router as bank_router
from app.api.routes.cover_letters import router as cover_letters_router
from app.api.routes.job_descriptions import router as job_descriptions_router
from app.api.routes.tailored_resumes import router as tailored_resumes_router
from app.core.config import get_settings
from app.core.logging import configure_logging, request_id_ctx
from app.db.session import get_engine


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="resume-tailor")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        token = request_id_ctx.set(str(uuid.uuid4()))
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}

    app.include_router(bank_router, prefix="/api")
    app.include_router(job_descriptions_router, prefix="/api")
    app.include_router(tailored_resumes_router, prefix="/api")
    app.include_router(cover_letters_router, prefix="/api")
    app.include_router(applications_router, prefix="/api")

    return app
