from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

app = FastAPI(
    title="Financial Multi-Agent Dashboard API",
    version="1.0.0",
)

app.include_router(router, prefix="/api")

frontend_dir = Path(__file__).resolve().parent / "frontend"

if not frontend_dir.is_dir():
    raise RuntimeError(
        f"Frontend directory not found: {frontend_dir}"
    )

app.mount(
    "/",
    StaticFiles(directory=str(frontend_dir), html=True),
    name="frontend",
)
