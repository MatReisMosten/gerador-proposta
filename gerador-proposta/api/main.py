"""Entrypoint da API — uvicorn api.main:app

Serve a API sob /api/* e, se existir um build do React em frontend_dist/
(gerado por `npm run build` no frontend/), serve o SPA no mesmo processo —
um serviço só, sem CORS, mesma URL (ver docs/plano-migracao-react.md)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .routes import auth, extract, proposal_types, proposals, templates

app = FastAPI(title="Gerador de Propostas Mosten — API", version="2.0.0")

app.include_router(auth.router, prefix="/api")
app.include_router(proposal_types.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(proposals.router, prefix="/api")
app.include_router(extract.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


if config.FRONTEND_DIST.is_dir():
    assets_dir = config.FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str) -> FileResponse:
        """Fallback do SPA: serve o arquivo estático se existir, senão index.html
        (roteamento client-side do React)."""
        candidate = config.FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(config.FRONTEND_DIST / "index.html")

else:

    @app.get("/")
    def frontend_missing() -> JSONResponse:
        return JSONResponse(
            {
                "detail": (
                    "frontend_dist/ não encontrado — rode `npm run build` em "
                    "frontend/ ou acesse a API diretamente em /api/*."
                )
            },
            status_code=404,
        )
