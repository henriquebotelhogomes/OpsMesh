"""OpsMesh FastAPI Application with Mandatory Scalar Documentation.

Implements rate limiting, BYOK authentication, REST API routes,
and Scalar API reference documentation (never Swagger UI).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from slowapi.errors import RateLimitExceeded

from opsmesh.api.dependencies import get_graph_app, limiter
from opsmesh.api.routes.chaos import router as chaos_router
from opsmesh.api.routes.incidents import router as incidents_router
from opsmesh.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager initializing graph and connections."""
    logger.info("Starting OpsMesh Incident Commander API (ENV=%s)...", settings.APP_ENV)
    # Pre-compile graph
    await get_graph_app()
    yield
    logger.info("Shutting down OpsMesh Incident Commander API...")


app = FastAPI(
    title="OpsMesh — Autonomous Incident Commander API",
    description="""**OpsMesh** é uma plataforma multi-agente autônoma para orquestração,
diagnóstico e remediação segura de incidentes em sistemas distribuídos de missão crítica.

### Governança & Padrões:
* **Protocolo de Ferramentas:** Universal Tool Gateway (Anthropic MCP + OpenAI / DeepSeek Tools).
* **Portão de Segurança HITL:** Bloqueio obrigatório antes da execução de comandos de mutação.
* **Documentação Viva:** Servida exclusivamente via **Scalar** (padrão moderno Vercel/Stripe).
* **FinOps Anti-Abuso:** Circuit Breaker diário, Rate Limiting por IP e modo Replay Zero-Token.
""",
    version="1.1.0",
    docs_url=None,  # Swagger UI desabilitado por padrão normativo
    redoc_url=None,  # ReDoc desabilitado
    lifespan=lifespan,
)

# Configure SlowAPI Rate Limiter
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return friendly JSON response when IP rate limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": "Limite de requisições excedido. FinOps Anti-DoW ativo (5 req/min por IP).",
            "detail": str(exc.detail),
        },
    )


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(incidents_router)
app.include_router(chaos_router)


# --- Scalar API Documentation Endpoints (Mandatório) ---


@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    """Live interactive API documentation powered by Scalar."""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="OpsMesh API Documentation — Scalar",
    )


@app.get("/scalar", include_in_schema=False)
async def scalar_docs_alias():
    """Alias for Scalar API documentation."""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="OpsMesh API Documentation — Scalar",
    )


@app.get("/health", tags=["Health & Status"])
async def health_check() -> dict[str, str]:
    """Health check and provider status endpoint."""
    return {
        "status": "healthy",
        "service": "opsmesh-api",
        "version": "1.1.0",
        "environment": settings.APP_ENV,
        "default_llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "docs_url": "/docs",
    }


# --- Frontend Single Page Application (SPA) Serving ---
_frontend_dist = Path(__file__).resolve().parents[3] / "frontend" / "dist"
if _frontend_dist.exists():
    _assets_dir = _frontend_dist / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # Avoid intercepting API routes or documentation
        if full_path.startswith(("api", "docs", "scalar", "health", "openapi.json")):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        target_file = _frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(_frontend_dist / "index.html")
