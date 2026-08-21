"""Sessão de acesso: substitui o gate de senha único do Streamlit por um
cookie assinado (HMAC), sem introduzir dependência nova (stdlib apenas).

Não há usuário/identidade — é a mesma senha única compartilhada de hoje
(`APP_PASSWORD`), só que verificada uma vez no login em vez de a cada rerun.
Ver docs/plano-migracao-react.md — SSO real é decisão futura, não desta fase.
"""

from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import HTTPException, Request

from . import config


def _sign(payload: str) -> str:
    key = config.APP_PASSWORD.encode("utf-8")
    return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token() -> str:
    expires_at = int(time.time()) + config.SESSION_TTL_SECONDS
    payload = str(expires_at)
    return f"{payload}.{_sign(payload)}"


def verify_session_token(token: str | None) -> bool:
    if not config.AUTH_REQUIRED:
        return True
    if not token or "." not in token:
        return False
    payload, _, signature = token.partition(".")
    expected = _sign(payload)
    if not hmac.compare_digest(signature, expected):
        return False
    try:
        expires_at = int(payload)
    except ValueError:
        return False
    return time.time() < expires_at


def check_password(password: str) -> bool:
    if not config.AUTH_REQUIRED:
        return True
    return hmac.compare_digest((password or "").strip(), config.APP_PASSWORD)


def require_auth(request: Request) -> None:
    """Dependency FastAPI: protege rotas quando APP_PASSWORD está definido."""
    token = request.cookies.get(config.SESSION_COOKIE_NAME)
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
