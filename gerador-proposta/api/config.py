"""Configuração da API: .env, chave de LLM fixa, senha de acesso."""

from __future__ import annotations

import os
from pathlib import Path

API_DIR = Path(__file__).resolve().parent
APP_ROOT = API_DIR.parent

try:
    from dotenv import load_dotenv

    load_dotenv(APP_ROOT / ".env")
except ImportError:
    _env_path = APP_ROOT / ".env"
    if _env_path.is_file():
        for _line in _env_path.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _, _v = _line.partition("=")
            _k, _v = _k.strip(), _v.strip().strip("'").strip('"')
            if _k and _k not in os.environ:
                os.environ[_k] = _v

DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "openrouter": "openai/gpt-4.1-mini",
}

# Provider/modelo fixos — mesma decisão do app Streamlit (ver PRODUCT.md).
OPENAI_API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
FIXED_LLM_PROVIDER = "openai"
FIXED_LLM_MODEL = DEFAULT_MODELS["openai"]
FIXED_LLM_BASE_URL: str | None = None

APP_PASSWORD = (os.environ.get("APP_PASSWORD") or "").strip()
AUTH_REQUIRED = bool(APP_PASSWORD)

BRIEF_MAX_CHARS = 4000

# Diretório do build do frontend (React), servido como estático pelo mesmo
# processo. Ausente em dev quando só a API está rodando (sem `npm run build`).
FRONTEND_DIST = APP_ROOT / "frontend_dist"

SESSION_COOKIE_NAME = "mosten_session"
SESSION_TTL_SECONDS = 12 * 60 * 60  # 12h

# TTL do download efêmero (arquivo fica em memória, nunca em disco).
DOWNLOAD_TTL_SECONDS = 10 * 60
