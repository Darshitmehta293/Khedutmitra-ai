"""
KhedutMitra AI — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.session import create_tables
from app.api import auth, farmer, markets, ai, buyers, admin

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KhedutMitra AI starting", version=settings.VERSION, env=settings.APP_ENV)
    await create_tables()
    logger.info("Database tables created/verified")
    yield
    logger.info("KhedutMitra AI shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─────────────────── CORS ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────── Request Logging Middleware ────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    logger.info("request", method=request.method, path=request.url.path,
                status=response.status_code, ms=elapsed)
    return response


# ─────────────────── Global Exception Handler ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ─────────────────── Routes ───────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(farmer.router, prefix="/api")
app.include_router(markets.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(buyers.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "tagline": "Know the Price. Find the Buyer. Sell Smarter.",
        "demo_mode": settings.DEMO_MODE,
    }
