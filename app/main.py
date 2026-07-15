import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    task: asyncio.Task | None = None
    if settings.rakuten_auto_enabled:
        from app.services.rakuten_scheduler import rakuten_scheduler_loop
        task = asyncio.create_task(rakuten_scheduler_loop())
    try:
        yield
    finally:
        if task is not None:
            task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/app", include_in_schema=False)
    async def wms_app() -> FileResponse:
        return FileResponse(_STATIC_DIR / "app.html")

    @app.get("/count-import", include_in_schema=False)
    async def count_import_ui() -> FileResponse:
        return FileResponse(_STATIC_DIR / "count_import.html")

    return app


app = create_app()
