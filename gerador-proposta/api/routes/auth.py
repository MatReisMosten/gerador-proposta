"""Login por senha única (APP_PASSWORD) — substitui o gate do Streamlit
por um cookie de sessão assinado. Sem identidade de usuário, mesma senha
compartilhada de hoje (ver docs/plano-migracao-react.md)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from .. import config, session
from ..schemas import AuthStatus, LoginRequest

router = APIRouter()


@router.get("/auth/status", response_model=AuthStatus)
def auth_status(request: Request) -> AuthStatus:
    token = request.cookies.get(config.SESSION_COOKIE_NAME)
    return AuthStatus(
        authenticated=session.verify_session_token(token),
        password_required=config.AUTH_REQUIRED,
    )


@router.post("/auth/login", response_model=AuthStatus)
def login(payload: LoginRequest, request: Request, response: Response) -> AuthStatus:
    if not session.check_password(payload.password):
        return AuthStatus(authenticated=False, password_required=config.AUTH_REQUIRED)
    token = session.create_session_token()
    response.set_cookie(
        config.SESSION_COOKIE_NAME,
        token,
        max_age=config.SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return AuthStatus(authenticated=True, password_required=config.AUTH_REQUIRED)


@router.post("/auth/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(config.SESSION_COOKIE_NAME)
    return {"ok": True}
