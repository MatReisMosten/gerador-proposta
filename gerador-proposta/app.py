"""
Gerador de Propostas Mosten — Streamlit MVP.

Uso:
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

try:
    from dotenv import load_dotenv

    load_dotenv(APP_DIR / ".env")
except ImportError:
    _env_path = APP_DIR / ".env"
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

# API OpenAI via .env (OPENAI_API_KEY) — sem chave no código
OPENAI_API_KEY = (os.environ.get("OPENAI_API_KEY") or "").strip()
FIXED_LLM_PROVIDER = "openai"
FIXED_LLM_MODEL = DEFAULT_MODELS["openai"]
FIXED_LLM_BASE_URL = None

BRIEF_MAX_CHARS = 4000

MOSTEN_LOGO = APP_DIR / "data" / "assets" / "logo-mosten.png"

from ui.styles import build_theme_css  # noqa: E402
from screens.generator_page import _init_session_defaults, render_generator  # noqa: E402
from screens.other_pages import (  # noqa: E402
    render_config,
    render_geradas,
    render_historico,
    render_templates,
)


def gate_password() -> bool:
    """Optional APP_PASSWORD env — simple gate for public Railway URL."""
    expected = os.environ.get("APP_PASSWORD", "").strip()
    if not expected:
        return True
    if st.session_state.get("_authed"):
        return True
    st.title("Gerador de Propostas Mosten")
    st.caption("Informe a senha de acesso para continuar.")
    pwd = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar", type="primary") and pwd == expected:
        st.session_state._authed = True
        st.rerun()
    if pwd:
        st.error("Senha incorreta.")
    return False


PAGES = {
    "gerador": render_generator,
    "geradas": render_geradas,
    "templates": render_templates,
    "historico": render_historico,
    "config": render_config,
}


def main() -> None:
    st.set_page_config(
        page_title="Gerador de Propostas Mosten",
        page_icon=str(MOSTEN_LOGO) if MOSTEN_LOGO.is_file() else "📄",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _init_session_defaults()
    st.session_state.theme_mode = "Claro"
    st.markdown(build_theme_css("Claro"), unsafe_allow_html=True)

    if not gate_password():
        return

    render_generator()


if __name__ == "__main__":
    main()
