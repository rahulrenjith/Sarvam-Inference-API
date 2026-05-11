from fastapi import FastAPI
from contextlib import asynccontextmanager
import time
import logging

from app.routers import chat, diagnostics, translate
from app.services.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    app.state.start_time = time.time()
    yield
    await redis_client.disconnect()


app = FastAPI(
    title="Sarvam Inference API",
    description="Production-grade FastAPI service wrapping LLM APIs with Redis caching and diagnostics.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration}ms"
    )

    return response


app.include_router(diagnostics.router, prefix="/health", tags=["Diagnostics"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(translate.router, prefix="/api/v1/translate", tags=["Translate"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Sarvam Inference API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
