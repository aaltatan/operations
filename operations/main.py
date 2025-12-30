from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from operations.api import v1
from operations.core.config import get_config
from operations.core.db import init_db
from operations.core.middlewares import SqltapProfilerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    init_db()
    yield


config = get_config()

app = FastAPI(
    lifespan=lifespan,
    title=config.app_title,
    description=config.app_description,
    version=config.app_version,
)

# middlewares

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.debug:
    app.add_middleware(SqltapProfilerMiddleware)

# routers

app.include_router(v1.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
