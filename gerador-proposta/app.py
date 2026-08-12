"""
Gerador de Propostas Mosten — Streamlit MVP.

Uso:
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import date, datetime
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

from generator import (  # noqa: E402
    build_livre_deck,
    build_package_deck,
    fill_slots,
    list_proposal_types,
    load_named_token_catalog,
)
from generator import paths as P  # noqa: E402
from generator.text_extract import TextExtractError, extract_text_from_bytes  # noqa: E402

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

PROJECT_CODE_RE = re.compile(r"^[A-Z]{3}\d{3}-\d{2}$")
TYPE_FILE_SUFFIX = {
    "suporte": "Proposta-Suporte-v1",
    "professional_service": "Professional-Service-v1",
    "passlog": "PassLog-v1",
    "discovery": "Discovery-v1",
    "clarion": "Clarion-v1",
    "livre": "Proposta-Tecnica-v1",
}

NAV_ITEMS = []  # navegação secundária removida do UI

BRIEF_MAX_CHARS = 4000

FOOTER_NOTE = (
    "Seus dados são utilizados apenas para gerar a proposta e não são armazenados."
)

MOSTEN_LOGO = APP_DIR / "data" / "assets" / "logo-mosten.png"

LIGHT_VARS = """
  --mosten-purple: #612CB5;
  --mosten-purple-dark: #803DE0;
  --mosten-purple-soft: #F7F4FC;
  --mosten-purple-mid: #E4D9F7;
  --mosten-purple-hover: #EFE8FA;
  --mosten-text: #23231E;
  --mosten-muted: #5C5C56;
  --mosten-border: #E8E4F0;
  --mosten-bg: #F7F4FC;
  --mosten-surface: #FFFFFF;
  --mosten-input: #FFFFFF;
  --mosten-sidebar: #FFFFFF;
  --mosten-success: #16A34A;
  --mosten-shadow: 0 1px 2px rgba(35, 35, 30, 0.04), 0 8px 24px rgba(35, 35, 30, 0.04);
  --mosten-uploader-btn-bg: #FFFFFF;
"""

DARK_VARS = """
  --mosten-purple: #A99BFF;
  --mosten-purple-dark: #CB6BF3;
  --mosten-purple-soft: #1E1A2A;
  --mosten-purple-mid: #3D3460;
  --mosten-purple-hover: #2A2438;
  --mosten-text: #F7F4FC;
  --mosten-muted: #B0AAB8;
  --mosten-border: #2E2A40;
  --mosten-bg: #14121C;
  --mosten-surface: #1C1826;
  --mosten-input: #17141F;
  --mosten-sidebar: #17141F;
  --mosten-success: #4ADE80;
  --mosten-shadow: 0 4px 22px rgba(0, 0, 0, 0.35);
  --mosten-uploader-btn-bg: #221E33;
"""


def build_theme_css(theme: str, active_page: str = "gerador") -> str:
    """CSS do layout central (sem sidebar) com variáveis light/dark."""
    vars_block = DARK_VARS if theme == "Escuro" else LIGHT_VARS
    _ = active_page  # reserved for future page-specific accents
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&display=swap');

:root {{
{vars_block}
}}

html, body, .stApp {{
  font-family: "Inter Tight", sans-serif !important;
  color: var(--mosten-text);
}}

.stApp {{
  background: var(--mosten-bg);
}}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

header[data-testid="stHeader"] {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: visible !important;
}}

header[data-testid="stHeader"]::before {{
  content: none !important;
}}

[data-testid="stToolbar"] {{
  display: none !important;
}}

.stDeployButton,
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"],
a[href*="share.streamlit"],
[data-testid="stHeaderActionElements"] {{
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
}}

/* Sidebar oculta — layout central do gerador (sem rail lateral) */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {{
  display: none !important;
  width: 0 !important;
  min-width: 0 !important;
  visibility: hidden !important;
}}

[data-testid="stAppViewContainer"] > .main,
.stApp [data-testid="stAppViewContainer"] {{
  margin-left: 0 !important;
}}

/* —— Área principal —— */
.stMainBlockContainer,
.block-container {{
  max-width: 1080px !important;
  padding: 1.5rem 1.75rem 2.5rem !important;
}}

.page-sub {{
  margin: 0.3rem 0 0;
  font-size: 0.88rem;
  color: var(--mosten-muted) !important;
}}

/* Cards — superfície limpa; sub-blocos sem borda (anti nested-card) */
div[class*="st-key-card_"] {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 1.25rem 1.35rem 1rem !important;
  margin-bottom: 1.1rem !important;
}}

div[class*="st-key-sub_"] {{
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0.85rem 0 0.35rem !important;
  margin-bottom: 0.35rem !important;
  border-top: 1px solid var(--mosten-border) !important;
}}

.card-head {{
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}}
.card-badge {{
  width: 26px;
  height: 26px;
  min-width: 26px;
  border-radius: 50%;
  background: var(--mosten-purple-soft);
  color: var(--mosten-purple-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
}}
.card-icon {{
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: 9px;
  background: var(--mosten-purple-soft);
  color: var(--mosten-purple);
  display: flex;
  align-items: center;
  justify-content: center;
}}
.card-icon svg {{
  width: 15px;
  height: 15px;
}}
.card-title {{
  margin: 0;
  font-size: 0.96rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.25;
  color: var(--mosten-text) !important;
}}
.card-hint {{
  margin: 0.15rem 0 0;
  font-size: 0.79rem;
  line-height: 1.4;
  color: var(--mosten-muted) !important;
}}

/* Tema (card no topo direito) */
.st-key-card_tema {{
  padding: 0.6rem 0.85rem 0.35rem !important;
  margin-bottom: 0.6rem !important;
}}
.st-key-theme_mode [data-testid="stWidgetLabel"] p {{
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: var(--mosten-muted) !important;
}}
.st-key-theme_mode [data-testid="stBaseButton-segmented_control"],
.st-key-theme_mode [data-testid="stBaseButton-segmented_controlActive"] {{
  border-radius: 9px !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  padding: 0.3rem 0.7rem !important;
  border: 1px solid var(--mosten-border) !important;
  background: var(--mosten-surface) !important;
  color: var(--mosten-muted) !important;
}}
.st-key-theme_mode [data-testid="stBaseButton-segmented_controlActive"] {{
  background: var(--mosten-purple-soft) !important;
  border-color: var(--mosten-purple) !important;
  color: var(--mosten-purple-dark) !important;
}}

/* Texto geral */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
label, .stMarkdown {{
  color: var(--mosten-text) !important;
}}

[data-testid="stWidgetLabel"] p {{
  font-size: 0.8rem !important;
  font-weight: 500 !important;
}}

[data-testid="stCaptionContainer"] p {{
  color: var(--mosten-muted) !important;
  font-size: 0.76rem !important;
}}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-baseweb="base-input"] {{
  border-radius: 10px !important;
  background-color: var(--mosten-input) !important;
  color: var(--mosten-text) !important;
  border-color: var(--mosten-border) !important;
  caret-color: var(--mosten-text) !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
  color: var(--mosten-muted) !important;
  opacity: 0.85;
}}

.stTextArea textarea {{
  background: var(--mosten-input) !important;
  border: 1px solid var(--mosten-border) !important;
  color: var(--mosten-text) !important;
}}

.stTextArea textarea:focus {{
  border-color: var(--mosten-purple) !important;
  box-shadow: 0 0 0 2px rgba(97, 44, 181, 0.15) !important;
}}

/* Upload */
[data-testid="stFileUploader"] {{
  margin-top: 0.1rem;
}}

[data-testid="stFileUploaderDropzone"] {{
  background: var(--mosten-purple-soft) !important;
  border: 1.5px dashed var(--mosten-purple-mid) !important;
  border-radius: 12px !important;
  padding: 1rem 1rem 1.35rem !important;
  flex-direction: column !important;
  text-align: center !important;
  gap: 0.45rem !important;
  align-items: center !important;
}}

[data-testid="stFileUploaderDropzone"]:hover {{
  border-color: var(--mosten-purple) !important;
  background: var(--mosten-purple-hover) !important;
}}

[data-testid="stFileUploaderDropzoneInstructions"] {{
  align-items: center !important;
  text-align: center !important;
  color: var(--mosten-text) !important;
}}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {{
  color: var(--mosten-muted) !important;
  font-size: 0.72rem !important;
}}

/* Logo — só dropzone com hover; esconde Browse files */
.st-key-info_logo [data-testid="stFileUploader"] [data-testid^="stBaseButton"] {{
  display: none !important;
}}

[data-testid="stFileUploader"] [data-testid^="stBaseButton"] {{
  background: var(--mosten-uploader-btn-bg) !important;
  color: var(--mosten-purple) !important;
  border: 1px solid var(--mosten-purple-mid) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
}}

.file-name-preview {{
  margin: 0.35rem 0 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  background: var(--mosten-purple-soft);
  border: 1px solid var(--mosten-border);
  font-size: 0.82rem;
  color: var(--mosten-text);
}}
.file-name-preview b {{
  font-weight: 600;
}}

/* Tipo de proposta — cards de seleção */
.st-key-proposal_type_id [data-testid="stRadioGroup"] {{
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem !important;
  align-items: stretch;
}}

@media (max-width: 900px) {{
  .st-key-proposal_type_id [data-testid="stRadioGroup"] {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
}}

@media (max-width: 560px) {{
  .st-key-proposal_type_id [data-testid="stRadioGroup"] {{
    grid-template-columns: 1fr;
  }}
}}

.st-key-proposal_type_id label[data-baseweb="radio"] {{
  margin: 0 !important;
  padding: 0.9rem 1rem !important;
  min-height: 7.25rem;
  height: 100%;
  box-sizing: border-box;
  display: flex !important;
  flex-direction: column;
  justify-content: flex-start;
  border: 1px solid var(--mosten-border);
  border-radius: 10px;
  background: var(--mosten-surface);
  transition: border-color 0.15s ease, background 0.15s ease;
}}

.st-key-proposal_type_id label[data-baseweb="radio"]:hover {{
  border-color: var(--mosten-purple-mid);
  background: var(--mosten-purple-soft);
}}

.st-key-proposal_type_id label[data-baseweb="radio"]:has(input:checked) {{
  border-color: var(--mosten-purple);
  background: var(--mosten-purple-soft);
  box-shadow: none;
}}

.st-key-proposal_type_id label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {{
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  margin: 0 !important;
}}

.st-key-proposal_type_id label[data-baseweb="radio"] [data-testid="stCaptionContainer"] {{
  flex: 1 1 auto;
}}

.st-key-proposal_type_id label[data-baseweb="radio"] [data-testid="stCaptionContainer"] p {{
  font-size: 0.76rem !important;
  font-weight: 400 !important;
  line-height: 1.4;
  margin-top: 0.3rem !important;
  color: var(--mosten-muted) !important;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}

/* Banner do modo + chip do template */
.mode-banner {{
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  flex-wrap: wrap;
  margin: 0.85rem 0 0.35rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--mosten-border);
  background: var(--mosten-surface);
}}
.mode-banner-text {{
  flex: 1 1 280px;
}}
.mode-banner-title {{
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.25rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--mosten-text) !important;
}}
.mode-banner-title svg {{
  width: 14px;
  height: 14px;
}}
.mode-banner-text p:last-child {{
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--mosten-muted) !important;
}}
.mode-banner-text code {{
  font-size: 0.72rem;
  background: transparent;
  color: var(--mosten-muted) !important;
}}
.tpl-chip {{
  display: none;
}}

/* Expanders */
[data-testid="stExpander"] details {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  margin-bottom: 0.6rem;
}}

[data-testid="stExpander"] summary {{
  padding: 0.7rem 0.9rem !important;
}}

[data-testid="stExpander"] summary p {{
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  color: var(--mosten-text) !important;
}}

[data-testid="stExpanderIcon"] {{
  color: var(--mosten-purple) !important;
}}

/* Botão principal — marca Mosten, texto branco */
[data-testid="stBaseButton-primary"] {{
  background: #612CB5 !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 0.8rem 1rem !important;
  box-shadow: none !important;
  color: #ffffff !important;
}}

[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primary"] span,
[data-testid="stBaseButton-primary"] label,
[data-testid="stBaseButton-primary"] div,
[data-testid="stBaseButton-primary"] svg {{
  color: #ffffff !important;
  fill: #ffffff !important;
}}

[data-testid="stBaseButton-primary"]:hover {{
  background: #803DE0 !important;
  color: #ffffff !important;
}}

.footer-note {{
  margin: 0.85rem 0 0;
  text-align: center;
  font-size: 0.76rem;
  color: var(--mosten-muted) !important;
}}

.gen-step {{
  margin: 0.35rem 0 0.65rem;
  text-align: center;
}}
.gen-step .card-title {{
  display: inline;
  font-size: 0.92rem;
}}
.gen-step .card-hint {{
  display: block;
  margin-top: 0.2rem;
}}

.checklist {{
  margin: 0 0 0.85rem;
  padding: 0.75rem 0.9rem;
  border-radius: 10px;
  background: var(--mosten-purple-soft);
  border: 1px solid var(--mosten-border);
  font-size: 0.8rem;
  color: var(--mosten-muted);
  line-height: 1.45;
}}
.checklist b {{
  color: var(--mosten-text);
  font-weight: 600;
}}

.logo-preview {{
  margin-top: 0.55rem;
  padding: 0.75rem;
  border-radius: 12px;
  border: 1px solid var(--mosten-border);
  background: var(--mosten-input);
  text-align: center;
}}
.logo-preview img {{
  max-height: 72px;
  max-width: 100%;
  object-fit: contain;
}}
.logo-preview-label {{
  margin: 0 0 0.45rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--mosten-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}

.type-summary {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.85rem 1rem;
  border-radius: 14px;
  border: 1px solid var(--mosten-border);
  background: var(--mosten-purple-soft);
  margin-bottom: 1rem;
}}
.type-summary b {{
  display: block;
  color: var(--mosten-purple-dark);
  font-size: 0.92rem;
}}
.type-summary span {{
  font-size: 0.78rem;
  color: var(--mosten-muted);
}}

.result-success {{
  padding: 0.35rem 0.15rem 0.5rem;
}}
.result-success h4 {{
  margin: 0 0 0.35rem;
  font-size: 1.02rem;
  color: var(--mosten-text) !important;
}}
.result-success p {{
  margin: 0 0 0.45rem;
  font-size: 0.84rem;
  color: var(--mosten-muted) !important;
  line-height: 1.45;
}}
.result-meta {{
  margin: 0.15rem 0;
  font-size: 0.8rem;
  color: var(--mosten-muted) !important;
}}
.result-meta b {{
  color: var(--mosten-text);
}}

.brand-logo {{
  display: block;
  height: 28px;
  width: auto;
  margin-bottom: 0.55rem;
}}
.page-title {{
  margin: 0;
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--mosten-text) !important;
}}

/* Botão Alterar tipo — compacto */
.st-key-alterar_tipo [data-testid^="stBaseButton"] {{
  border-radius: 999px !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  padding: 0.28rem 0.85rem !important;
}}


.wizard-stepper {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
  margin: 0.35rem 0 0.85rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--mosten-border);
  border-radius: 12px;
  background: var(--mosten-surface);
}}
.wizard-node {{
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-width: 0;
  flex: 0 1 auto;
}}
.wizard-dot {{
  width: 34px;
  height: 34px;
  min-width: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  border: 2px solid var(--mosten-border);
  background: var(--mosten-surface);
  color: var(--mosten-muted);
}}
.wizard-node.active .wizard-dot {{
  background: var(--mosten-purple);
  border-color: var(--mosten-purple);
  color: #fff;
  transform: scale(1.08);
}}
.wizard-node.done .wizard-dot {{
  background: var(--mosten-purple-soft);
  border-color: var(--mosten-purple);
  color: var(--mosten-purple);
}}
.wizard-meta b {{
  display: block;
  font-size: 0.86rem;
  color: var(--mosten-text);
  font-weight: 600;
}}
.wizard-meta span {{
  display: block;
  font-size: 0.72rem;
  color: var(--mosten-muted);
}}
.wizard-line {{
  flex: 1 1 24px;
  height: 2px;
  background: var(--mosten-border);
  margin: 0 0.25rem;
}}
.wizard-line.filled {{
  background: var(--mosten-purple);
}}
.wizard-panel-hidden {{
  display: none !important;
}}
div[class*="st-key-wizard_panel_"] {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 12px !important;
  padding: 1.15rem 1.25rem 0.9rem !important;
  margin-bottom: 0.85rem !important;
}}
div[class*="st-key-wizard_panel_"].wizard-panel-hidden,
div.wizard-panel-hidden[class*="st-key-wizard_panel_"] {{
  display: none !important;
}}

/* Resultado — estado vazio */
.result-empty {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2.2rem 1.2rem 1.4rem;
  min-height: 300px;
  position: relative;
  overflow: hidden;
}}

.result-empty-icon {{
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--mosten-purple-soft);
  color: var(--mosten-purple);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}}

.result-empty-icon svg {{
  width: 26px;
  height: 26px;
}}

.result-empty h4 {{
  margin: 0 0 0.4rem;
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--mosten-text) !important;
}}

.result-empty p {{
  margin: 0;
  color: var(--mosten-muted) !important;
  font-size: 0.85rem;
  line-height: 1.45;
  max-width: 16.5rem;
}}

.result-wave {{
  position: absolute;
  left: 0;
  right: 0;
  bottom: -8px;
  height: 90px;
  pointer-events: none;
  opacity: 0.7;
}}

/* Lista de arquivos (Propostas geradas / Histórico) */
.file-row {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
}}
.file-row svg {{
  width: 17px;
  height: 17px;
  color: var(--mosten-purple);
}}
.file-row b {{
  display: block;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--mosten-text);
}}
.file-row small {{
  font-size: 0.72rem;
  color: var(--mosten-muted);
}}

.meta-line {{
  margin: 0.15rem 0;
  font-size: 0.8rem;
  color: var(--mosten-muted) !important;
}}
.meta-line b {{
  color: var(--mosten-text);
  font-weight: 600;
}}

/* Overlay de carregamento */
.mosten-loading-overlay {{
  position: fixed;
  inset: 0;
  z-index: 999999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(18, 16, 26, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}}
.mosten-loading-card {{
  width: min(420px, calc(100vw - 2rem));
  background: var(--mosten-surface);
  border: 1px solid var(--mosten-border);
  border-radius: 20px;
  box-shadow: 0 24px 60px rgba(0,0,0,.25);
  padding: 1.75rem 1.6rem 1.5rem;
  text-align: center;
}}
.mosten-loading-spinner {{
  width: 52px;
  height: 52px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  border: 3px solid var(--mosten-purple-mid);
  border-top-color: var(--mosten-purple);
  animation: mosten-spin 0.85s linear infinite;
}}
@keyframes mosten-spin {{
  to {{ transform: rotate(360deg); }}
}}
.mosten-loading-pct {{
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--mosten-purple);
  line-height: 1;
  margin-bottom: 0.45rem;
}}
.mosten-loading-title {{
  font-size: 1rem;
  font-weight: 700;
  color: var(--mosten-text);
  margin: 0 0 0.25rem;
}}
.mosten-loading-msg {{
  font-size: 0.86rem;
  color: var(--mosten-muted);
  margin: 0 0 1.1rem;
  min-height: 1.3em;
}}
.mosten-loading-bar {{
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: var(--mosten-purple-soft);
  overflow: hidden;
}}
.mosten-loading-bar > i {{
  display: block;
  height: 100%;
  width: 100%;
  transform-origin: left center;
  border-radius: 999px;
  background: var(--mosten-purple);
  transition: transform 0.35s ease;
}}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] {{
  color: var(--mosten-text) !important;
  background: var(--mosten-surface) !important;
}}

@media (max-width: 900px) {{
  div[data-testid="stHorizontalBlock"] {{
    flex-wrap: wrap !important;
  }}
}}
</style>
"""

LOGO_SVG = """
<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 26V6l12 12L28 6v20" stroke="#612CB5" stroke-width="3.4"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

ICON_BRIEF = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <line x1="8" y1="13" x2="16" y2="13"/>
  <line x1="8" y1="17" x2="13" y2="17"/>
</svg>
"""

ICON_PAGE = ICON_BRIEF

TYPE_ICONS = {
    "professional_service": ":material/work:",
    "suporte": ":material/support_agent:",
    "passlog": ":material/badge:",
    "discovery": ":material/travel_explore:",
    "clarion": ":material/analytics:",
    "livre": ":material/menu_book:",
}

ICON_RESULT = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 18h6"/>
  <path d="M10 22h4"/>
  <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>
</svg>
"""

ICON_INFO = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="9"/>
  <line x1="12" y1="11" x2="12" y2="16"/>
  <line x1="12" y1="8" x2="12" y2="8"/>
</svg>
"""

ICON_FILE = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
</svg>
"""

ICON_SPARK = """
<svg viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 2l1.6 4.4L18 8l-4.4 1.6L12 14l-1.6-4.4L6 8l4.4-1.6z"/>
  <path d="M18.5 14l.9 2.4 2.6.9-2.6.9-.9 2.4-.9-2.4-2.6-.9 2.6-.9z"/>
</svg>
"""

ICON_CHEVRON = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="6 9 12 15 18 9"/>
</svg>
"""

RESULT_WAVE_SVG = """
<svg class="result-wave" viewBox="0 0 400 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 70 C 60 40, 110 95, 170 70 C 230 45, 280 90, 340 60 C 370 48, 390 55, 400 50 L400 120 L0 120 Z" fill="#F7F4FC"/>
  <path d="M0 85 C 70 55, 120 105, 190 80 C 250 58, 300 100, 360 75 C 380 68, 395 72, 400 70 L400 120 L0 120 Z" fill="#DDD6FE"/>
  <path d="M0 98 C 80 78, 140 110, 210 95 C 270 82, 320 108, 400 90 L400 120 L0 120 Z" fill="#C4B5FD" opacity="0.85"/>
  <g fill="#CB6BF3" opacity="0.9">
    <path d="M310 42 l2.2 5.5 5.8.4-4.4 3.8 1.4 5.6-5-3.1-5 3.1 1.4-5.6-4.4-3.8 5.8-.4z"/>
    <path d="M345 28 l1.5 3.6 3.8.3-2.9 2.5.9 3.7-3.3-2-3.3 2 .9-3.7-2.9-2.5 3.8-.3z"/>
    <path d="M280 55 l1.1 2.6 2.7.2-2.1 1.8.7 2.6-2.4-1.5-2.4 1.5.7-2.6-2.1-1.8 2.7-.2z"/>
  </g>
</svg>
"""


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


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "proposta"


def load_example_values() -> dict[str, str] | None:
    path = P.example_values_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("vigia") or data.get("values")


def _init_session_defaults() -> None:
    defaults = {
        "messages": [],
        "brief_text": "",
        "transcription_text": "",
        "estimate_text": "",
        "premissas_restricoes": "",
        "theme_mode": "Claro",
        "page": "gerador",
        "wizard_step": 1,
        "wizard_max": 1,
        "tipo_collapsed": False,
        "selected_proposal_type": "professional_service",
        "last_result": None,
        "open_result_modal": False,
        "_transcription_file_id": None,
        "_estimate_file_id": None,
        "_brief_file_id": None,
        "_premissas_file_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _on_tipo_selected() -> None:
    chosen = st.session_state.get("proposal_type_id")
    if chosen:
        st.session_state.selected_proposal_type = chosen


def _skips_info_step(type_id: str | None) -> bool:
    """Clarion is a static deck — no client/fields form."""
    return (type_id or "") == "clarion"


def _uses_brief_field(type_id: str | None) -> bool:
    """Tipos que mostram Brief/contexto (com anexo MD/TXT)."""
    return (type_id or "") in {"livre", "discovery", "passlog"}


def _render_brief_context_field() -> str:
    """Campo Brief/contexto com upload MD/TXT e preview editável."""
    with st.container(border=True, key="sub_brief"):
        _card_head(
            "Brief / contexto",
            "Resumo da proposta, objetivos e contexto comercial.",
            icon_svg=ICON_BRIEF,
        )
        brief_file = st.file_uploader(
            "Anexar brief (MD/TXT)",
            type=["txt", "md"],
            key="brief_uploader",
            help="O texto do arquivo preenche o campo abaixo para revisão.",
        )
        _apply_upload_to_field(
            uploaded=brief_file,
            text_key="brief_text",
            fingerprint_key="_brief_file_id",
            label="Brief",
            max_chars=BRIEF_MAX_CHARS,
        )
        if brief_file is not None:
            st.caption(f"Anexo: **{brief_file.name}** — revise o texto abaixo.")
        return st.text_area(
            "Brief",
            height=185,
            max_chars=BRIEF_MAX_CHARS,
            key="brief_text",
            label_visibility="collapsed",
            placeholder=(
                "Exemplo:\n"
                "Cliente: NPH/Unisanta\n"
                "Contexto: operação cresceu; mais pessoas, sistemas "
                "e decisões no dia a dia\n"
                "Fricções: informação dispersa; decisões demoram; "
                "dependência de poucas pessoas\n"
                "Impacto: reação tardia, custo sobe, previsibilidade cai\n"
                "Transformação desejada: operação conectada, visível "
                "e pronta para crescer\n"
                "Escopo/integrações (opcional): sistemas atuais, "
                "APIs, restrições\n"
                "Prazo/preço (se houver): a definir"
            ),
        )


def _file_fingerprint(uploaded) -> str | None:
    if uploaded is None:
        return None
    return f"{uploaded.name}:{uploaded.size}"


def _apply_upload_to_field(
    *,
    uploaded,
    text_key: str,
    fingerprint_key: str,
    label: str,
    max_chars: int | None = None,
) -> None:
    """Extrai texto do upload e atualiza o session_state do textarea."""
    fp = _file_fingerprint(uploaded)
    if uploaded is None:
        st.session_state[fingerprint_key] = None
        return
    if fp == st.session_state.get(fingerprint_key):
        return
    try:
        extracted = extract_text_from_bytes(uploaded.getvalue(), uploaded.name)
    except TextExtractError as exc:
        st.warning(f"{label}: {exc}")
        return
    if max_chars is not None and len(extracted) > max_chars:
        extracted = extracted[:max_chars]
        st.warning(
            f"{label}: texto truncado para {max_chars} caracteres "
            f"(limite do campo)."
        )
    st.session_state[text_key] = extracted
    st.session_state[fingerprint_key] = fp
    st.toast(f"{label}: texto extraído de {uploaded.name}")


def _build_full_brief(
    brief: str,
    transcription: str,
    estimate: str,
    premissas: str = "",
) -> str:
    parts: list[str] = []
    if brief.strip():
        parts.append(f"BRIEF:\n{brief.strip()}")
    if transcription.strip():
        parts.append(f"TRANSCRIÇÃO DA REUNIÃO:\n{transcription.strip()}")
    if estimate.strip():
        parts.append(f"ESTIMATIVA TÉCNICA:\n{estimate.strip()}")
    if premissas.strip():
        parts.append(f"PREMISSAS E RESTRIÇÕES:\n{premissas.strip()}")
    if st.session_state.messages:
        parts.append(
            "Complementos:\n"
            + "\n".join(f"- {m}" for m in st.session_state.messages)
        )
    return "\n\n".join(parts)


def _card_head(
    title: str,
    hint: str = "",
    *,
    step: int | None = None,
    icon_svg: str | None = None,
) -> None:
    if step is not None:
        mark = f'<div class="card-badge">{step}</div>'
    else:
        mark = f'<div class="card-icon">{icon_svg or ICON_BRIEF}</div>'
    hint_html = f'<p class="card-hint">{hint}</p>' if hint else ""
    st.markdown(
        f'<div class="card-head">{mark}<div>'
        f'<p class="card-title">{title}</p>{hint_html}'
        "</div></div>",
        unsafe_allow_html=True,
    )


def _page_header(title: str, subtitle: str, *, with_theme: bool = True) -> None:
    _ = with_theme  # tema fixo claro
    if MOSTEN_LOGO.is_file():
        st.image(str(MOSTEN_LOGO), width=132)
    st.markdown(
        f'<p class="page-title">{title}</p>'
        f'<p class="page-sub">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def _render_wizard_stepper(
    current: int, max_reached: int, *, skip_info: bool = False
) -> None:
    steps = [
        (1, "Tipo", "Escolha a oferta"),
        (2, "Informações", "Cliente e campos"),
        (3, "Gerar", "Revisar e baixar"),
    ]
    parts: list[str] = ['<div class="wizard-stepper">']
    for i, (num, title, hint) in enumerate(steps):
        if num < current:
            state = "done"
            mark = "✓"
        elif num == current:
            state = "active"
            mark = str(num)
        else:
            state = "todo"
            mark = str(num)
        # Clarion: step 2 is not part of the path
        if skip_info and num == 2:
            if current >= 3:
                state = "done"
                mark = "✓"
            else:
                state = "todo"
                mark = "—"
            hint = "Não se aplica"
        parts.append(
            f'<div class="wizard-node {state}">'
            f'<div class="wizard-dot">{mark}</div>'
            f'<div class="wizard-meta"><b>{title}</b><span>{hint}</span></div>'
            f"</div>"
        )
        if i < len(steps) - 1:
            if skip_info and num == 1:
                line = "filled" if current >= 3 else ""
            else:
                line = "filled" if num < current else ""
            parts.append(f'<div class="wizard-line {line}"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3, gap="small")
    for col, num, title in (
        (b1, 1, "1 · Tipo"),
        (b2, 2, "2 · Informações"),
        (b3, 3, "3 · Gerar"),
    ):
        with col:
            if skip_info and num == 2:
                disabled = True
            else:
                disabled = num > max_reached
            if st.button(
                title,
                key=f"wizard_jump_{num}",
                use_container_width=True,
                disabled=disabled,
                type="primary" if num == current else "secondary",
            ):
                st.session_state.wizard_step = num
                st.rerun()


def _wizard_nav(
    *, step: int, can_advance: bool = True, skip_info: bool = False
) -> None:
    back, _, nxt = st.columns([1, 2, 1], gap="medium")
    with back:
        if step > 1:
            if st.button(
                "Voltar",
                key=f"wizard_back_{step}",
                use_container_width=True,
                icon=":material/arrow_back:",
            ):
                if skip_info and step == 3:
                    st.session_state.wizard_step = 1
                else:
                    st.session_state.wizard_step = step - 1
                st.rerun()
    with nxt:
        if step < 3:
            if st.button(
                "Avançar",
                key=f"wizard_next_{step}",
                use_container_width=True,
                type="primary",
                icon=":material/arrow_forward:",
                disabled=not can_advance,
            ):
                if skip_info and step == 1:
                    next_step = 3
                else:
                    next_step = step + 1
                st.session_state.wizard_step = next_step
                st.session_state.wizard_max = max(
                    int(st.session_state.get("wizard_max") or 1), next_step
                )
                st.rerun()


def _footer_note() -> None:
    st.markdown(f'<p class="footer-note">{FOOTER_NOTE}</p>', unsafe_allow_html=True)


def _type_label(type_id: str, label: str) -> str:
    icon = TYPE_ICONS.get(type_id, ":material/description:")
    return f"{icon} {label}"

class FullscreenLoading:
    """Overlay de tela cheia com spinner + porcentagem."""

    def __init__(self, title: str = "Gerando proposta") -> None:
        self.title = title
        self._slot = st.empty()

    def update(self, percent: int, message: str) -> None:
        pct = max(0, min(100, int(percent)))
        self._slot.markdown(
            f"""
<div class="mosten-loading-overlay">
  <div class="mosten-loading-card">
    <div class="mosten-loading-spinner"></div>
    <div class="mosten-loading-pct">{pct}%</div>
    <p class="mosten-loading-title">{self.title}</p>
    <p class="mosten-loading-msg">{message}</p>
    <div class="mosten-loading-bar"><i style="transform:scaleX({pct / 100})"></i></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    def close(self) -> None:
        self._slot.empty()


def _result_empty_state() -> str:
    return (
        '<div class="result-empty">'
        f'<div class="result-empty-icon">{ICON_BRIEF}</div>'
        "<h4>Aguardando geração</h4>"
        "<p>Quando a proposta estiver pronta, "
        "o download aparece aqui.</p>"
        "</div>"
    )


def _resolve_logo_path(logo_file, client_name: str) -> Path | None:
    if logo_file is not None:
        tmp_logo = tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(logo_file.name).suffix
        )
        tmp_logo.write(logo_file.getvalue())
        tmp_logo.close()
        return Path(tmp_logo.name)
    default_logo = P.ASSETS / "logo-nph.png"
    if default_logo.is_file() and (
        not client_name
        or "nph" in client_name.lower()
        or "unisanta" in client_name.lower()
    ):
        return default_logo
    return None


def _format_project_code(raw: str) -> str:
    """Normaliza para AAA999-99 (3 letras + 3 dígitos + hífen + 2 dígitos)."""
    chars = re.sub(r"[^A-Za-z0-9]", "", raw or "").upper()
    letters = "".join(c for c in chars if c.isalpha())[:3]
    digits = "".join(c for c in chars if c.isdigit())
    d1 = digits[:3]
    d2 = digits[3:5]
    out = letters + d1
    if d2 or len(digits) > 3:
        out += "-" + d2
    return out


def _on_project_code_change() -> None:
    raw = st.session_state.get("info_code") or ""
    st.session_state.info_code = _format_project_code(raw)


def _format_money_br(raw: str) -> str:
    """Máscara monetária BR a partir só de dígitos (centavos)."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    digits = digits[:12]
    value = int(digits)
    reais = value // 100
    cents = value % 100
    reais_fmt = f"{reais:,}".replace(",", ".")
    return f"R$ {reais_fmt},{cents:02d}"


def _format_weeks_only(raw: str) -> str:
    """Só dígitos — tempo em semanas."""
    digits = re.sub(r"\D", "", raw or "")[:3]
    if not digits:
        return ""
    return str(int(digits))


def _on_money_field_change(key: str) -> None:
    st.session_state[key] = _format_money_br(st.session_state.get(key) or "")


def _on_weeks_field_change(key: str) -> None:
    st.session_state[key] = _format_weeks_only(st.session_state.get(key) or "")


def _is_valid_project_code(code: str) -> bool:
    return bool(PROJECT_CODE_RE.match((code or "").strip().upper()))


def _proposal_file_stem(project_code: str, type_id: str) -> str:
    code = (project_code or "").strip().upper() or "XXX000-00"
    suffix = TYPE_FILE_SUFFIX.get(type_id) or f"{slugify(type_id) or 'Proposta'}-v1"
    return f"{code}-{suffix}"


def _build_output_path(
    *,
    project_code: str,
    type_id: str = "",
    output_name: str = "",
    client_name: str = "",
    type_slug: str = "",
) -> Path:
    if output_name.strip():
        name = output_name.strip()
    else:
        tid = type_id or type_slug or "proposta"
        name = _proposal_file_stem(project_code, tid)
    if not name.lower().endswith(".pptx"):
        name += ".pptx"
    return P.output_dir() / name


def _result_success_html(
    *,
    file_name: str,
    client: str,
    code: str,
    type_label: str,
    size_label: str,
) -> str:
    client_disp = client.strip() or "—"
    code_disp = code.strip() or "—"
    return (
        '<div class="result-success">'
        f'<div class="result-empty-icon" style="margin:0 auto 0.85rem">'
        f"{ICON_RESULT}</div>"
        "<h4>Proposta gerada</h4>"
        f"<p><b>{file_name}</b></p>"
        f'<p class="result-meta">Cliente: <b>{client_disp}</b></p>'
        f'<p class="result-meta">Código: <b>{code_disp}</b></p>'
        f'<p class="result-meta">Tipo: <b>{type_label}</b></p>'
        f'<p class="result-meta">Tamanho: <b>{size_label}</b></p>'
        "</div>"
    )


def _persist_values_json(out_path: Path, values: dict, meta: dict | None) -> None:
    payload = {
        "client": (meta or {}).get("client"),
        "code": (meta or {}).get("code"),
        "type": (meta or {}).get("type"),
        "template": (meta or {}).get("template"),
        "provider": (meta or {}).get("provider"),
        "model": (meta or {}).get("model"),
        "values": values,
    }
    values_path = out_path.with_suffix(".values.json")
    values_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _show_download(
    *,
    result_box,
    download_box,
    out_path: Path,
    values: dict,
    meta: dict | None = None,
) -> None:
    meta = meta or {}
    type_label = meta.get("type_label") or meta.get("type") or "—"
    size_label = _human_size(out_path.stat().st_size)
    payload_bytes = out_path.read_bytes()

    st.session_state.last_result = {
        "file_name": out_path.name,
        "path": str(out_path),
        "client": meta.get("client") or "",
        "code": meta.get("code") or "",
        "type": meta.get("type"),
        "type_label": type_label,
        "template": meta.get("template"),
        "size_label": size_label,
        "values": values,
    }

    result_box.markdown(
        _result_success_html(
            file_name=out_path.name,
            client=str(meta.get("client") or ""),
            code=str(meta.get("code") or ""),
            type_label=str(type_label),
            size_label=size_label,
        ),
        unsafe_allow_html=True,
    )
    with download_box.container():
        st.download_button(
            label="Baixar PPTX",
            data=payload_bytes,
            file_name=out_path.name,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            use_container_width=True,
            icon=":material/download:",
            key="download_result_card",
        )

    _persist_values_json(out_path, values, meta)
    _proposal_ready_dialog()


@st.dialog("Proposta gerada", width="large")
def _proposal_ready_dialog() -> None:
    data = st.session_state.get("last_result") or {}
    out_name = data.get("file_name") or "proposta.pptx"
    st.markdown(
        f"**Arquivo:** `{out_name}`  \n"
        f"**Cliente:** {data.get('client') or '—'}  \n"
        f"**Código:** {data.get('code') or '—'}  \n"
        f"**Tipo:** {data.get('type_label') or '—'}  \n"
        f"**Tamanho:** {data.get('size_label') or '—'}"
    )
    path_str = data.get("path") or ""
    path = Path(path_str) if path_str else None
    if path and path.is_file():
        st.download_button(
            label="Baixar PPTX",
            data=path.read_bytes(),
            file_name=out_name,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            use_container_width=True,
            type="primary",
            icon=":material/download:",
            key="download_modal_pptx",
        )
    if data.get("template"):
        st.caption(f"Template: `{Path(str(data['template'])).name}`")


def _parse_premissas_restricoes(text: str) -> dict[str, str]:
    """
    Converte texto livre em tokens {PREMISSA_n_ITEM}, {RESTRICAO_n_ITEM},
    {RESTR_n_DESC}. Aceita blocos 'Premissas:' / 'Restrições:' ou lista única.
    """
    raw = (text or "").strip()
    if not raw:
        return {}

    lower = raw.lower()
    prem_idx = -1
    rest_idx = -1
    for marker in ("premissas:", "premissa:", "premissas\n", "premissa\n"):
        i = lower.find(marker)
        if i >= 0:
            prem_idx = i
            break
    for marker in (
        "restrições:",
        "restricoes:",
        "restrição:",
        "restricao:",
        "restrições\n",
        "restricoes\n",
    ):
        i = lower.find(marker)
        if i >= 0:
            rest_idx = i
            break

    def _items(block: str) -> list[str]:
        lines: list[str] = []
        headers = {
            "premissas",
            "premissa",
            "restrições",
            "restricoes",
            "restrição",
            "restricao",
        }
        for line in block.splitlines():
            cleaned = re.sub(r"^[\s\-•*–—\d.)]+", "", line).strip()
            if not cleaned:
                continue
            if cleaned.lower().rstrip(":").strip() in headers:
                continue
            lines.append(cleaned)
        if not lines and block.strip():
            parts = re.split(r"[;\n]+", block)
            lines = [
                p.strip()
                for p in parts
                if p.strip() and p.strip().lower().rstrip(":").strip() not in headers
            ]
        return lines

    if prem_idx >= 0 or rest_idx >= 0:
        if prem_idx >= 0 and rest_idx >= 0:
            if prem_idx < rest_idx:
                prem_block = raw[prem_idx:rest_idx]
                rest_block = raw[rest_idx:]
            else:
                rest_block = raw[rest_idx:prem_idx]
                prem_block = raw[prem_idx:]
        elif prem_idx >= 0:
            prem_block = raw[prem_idx:]
            rest_block = ""
        else:
            prem_block = ""
            rest_block = raw[rest_idx:]
        premissas = _items(prem_block)
        restricoes = _items(rest_block)
    else:
        premissas = _items(raw)
        restricoes = []

    out: dict[str, str] = {}
    for i, item in enumerate(premissas[:7], start=1):
        out[f"{{PREMISSA_{i}_ITEM}}"] = item
    for i, item in enumerate(restricoes[:5], start=1):
        out[f"{{RESTRICAO_{i}_ITEM}}"] = item
        out[f"{{RESTR_{i}_DESC}}"] = item
    return out


def _apply_premissas_to_values(
    values: dict[str, str], premissas_text: str
) -> dict[str, str]:
    parsed = _parse_premissas_restricoes(premissas_text)
    if not parsed:
        return values
    merged = dict(values)
    merged.update(parsed)
    return merged


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _mtime_label(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")


@st.cache_data(show_spinner=False)
def _template_summary(path_str: str, mtime: float) -> dict:
    """Seções e tokens do mestre (cacheado por mtime do arquivo)."""
    from generator.engine import scan_named_tokens
    from generator.packages import read_pptx_sections

    path = Path(path_str)
    sections = read_pptx_sections(path)
    tokens = scan_named_tokens(path)
    return {
        "sections": {name: len(slides) for name, slides in sections.items()},
        "tokens": sorted(tokens),
    }


def render_generator() -> None:
    _page_header(
        "Gerador de Propostas",
        "Monte propostas comerciais Mosten a partir do template oficial.",
    )

    if st.session_state.pop("open_result_modal", False) and st.session_state.get(
        "last_result"
    ):
        _proposal_ready_dialog()

    proposal_types = list_proposal_types()
    ordered = sorted(
        proposal_types,
        key=lambda t: (0 if t.get("mode") == "package" else 1, t.get("label") or ""),
    )
    type_ids = [t["id"] for t in ordered]
    label_by_id = {t["id"]: (t.get("label") or t["id"]) for t in ordered}
    desc_by_id = {t["id"]: (t.get("description") or "") for t in ordered}
    pkg_by_id = {t["id"]: t for t in ordered}
    master_path = P.master_template_path()

    persisted = st.session_state.get("selected_proposal_type")
    if persisted not in type_ids:
        persisted = (
            "professional_service"
            if "professional_service" in type_ids
            else type_ids[0]
        )
        st.session_state.selected_proposal_type = persisted

    step = int(st.session_state.get("wizard_step") or 1)
    step = max(1, min(3, step))
    skip_info = _skips_info_step(
        st.session_state.get("selected_proposal_type")
        or st.session_state.get("proposal_type_id")
    )
    if skip_info and step == 2:
        step = 3
    st.session_state.wizard_step = step
    max_reached = max(int(st.session_state.get("wizard_max") or 1), step)
    st.session_state.wizard_max = max_reached

    _render_wizard_stepper(step, max_reached, skip_info=skip_info)

    # CSS: esconde painéis inativos sem desmontar widgets
    hide_rules = []
    for n in (1, 2, 3):
        if n != step:
            hide_rules.append(
                f'div[class*="st-key-wizard_panel_{n}"] {{ display: none !important; }}'
            )
    if hide_rules:
        st.markdown("<style>" + "".join(hide_rules) + "</style>", unsafe_allow_html=True)

    provider = FIXED_LLM_PROVIDER
    model = FIXED_LLM_MODEL
    api_key = OPENAI_API_KEY
    base_url = FIXED_LLM_BASE_URL

    field_values: dict[str, str] = {}
    brief = transcription = estimate = ""
    client_name = st.session_state.get("info_client") or ""
    project_code = st.session_state.get("info_code") or ""
    logo_file = None
    premissas_text = st.session_state.get("premissas_restricoes") or ""

    # —— Painel 1: Tipo ——
    with st.container(border=True, key="wizard_panel_1"):
        _card_head(
            "Tipo de proposta",
            "Escolha a oferta e avance para preencher os dados.",
            step=1,
        )
        if st.session_state.get("proposal_type_id") not in type_ids:
            st.session_state.proposal_type_id = (
                st.session_state.selected_proposal_type
            )
        chosen = st.radio(
            "Tipo de proposta",
            options=type_ids,
            format_func=lambda i: _type_label(i, label_by_id[i]),
            captions=[desc_by_id[i] for i in type_ids],
            horizontal=True,
            key="proposal_type_id",
            label_visibility="collapsed",
            on_change=_on_tipo_selected,
        )
        st.session_state.selected_proposal_type = chosen
        selected_id = chosen
        pkg_preview = pkg_by_id[selected_id]
        mode_preview = pkg_preview.get("mode") or "llm_full"
        label_preview = label_by_id[selected_id]
        if mode_preview == "package":
            if selected_id == "clarion":
                banner_text = (
                    f"Gera a oferta <b>{label_preview}</b> com o deck "
                    "oficial estático. Sem formulário — avance direto "
                    "para gerar o PPTX."
                )
            else:
                banner_text = (
                    f"Gera a oferta <b>{label_preview}</b> com os slides "
                    "oficiais do template. Você preenche só os campos "
                    "comerciais; o restante do layout permanece."
                )
        else:
            banner_text = (
                "Gera a proposta completa a partir do brief. "
                "O LLM escreve os textos nos espaços do template — "
                "sem redesenhar slides."
            )
        st.markdown(
            '<div class="mode-banner">'
            '<div class="mode-banner-text">'
            f'<p class="mode-banner-title">{ICON_INFO} {label_preview}</p>'
            f"<p>{banner_text}</p>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if step == 1:
            _wizard_nav(
                step=1,
                can_advance=True,
                skip_info=_skips_info_step(selected_id),
            )

    selected_id = st.session_state.selected_proposal_type
    if selected_id not in pkg_by_id:
        selected_id = type_ids[0]
        st.session_state.selected_proposal_type = selected_id
    pkg = pkg_by_id[selected_id]
    mode = pkg.get("mode") or "llm_full"
    label = label_by_id[selected_id]

    # —— Painel 2: Informações ——
    with st.container(border=True, key="wizard_panel_2"):
        _card_head(
            "Informações da proposta",
            "Cliente, código e campos da oferta selecionada.",
            step=2,
        )
        g1, g2 = st.columns(2, gap="medium")
        with g1:
            client_name = st.text_input(
                "Cliente", placeholder="NPH / Unisanta", key="info_client"
            )
        with g2:
            project_code = st.text_input(
                "Código da proposta",
                placeholder="BUI001-26",
                key="info_code",
                max_chars=9,
                on_change=_on_project_code_change,
                help="Formato: 3 letras + 3 números + hífen + 2 números (ex.: BUI001-26).",
            )
        logo_file = st.file_uploader(
            "Logo do cliente (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            key="info_logo",
        )
        stem_preview = _proposal_file_stem(project_code, selected_id)
        st.markdown(
            f'<p class="file-name-preview">Arquivo gerado: '
            f"<b>{stem_preview}.pptx</b></p>",
            unsafe_allow_html=True,
        )
        logo_preview_slot = st.empty()
        if logo_file is not None:
            with logo_preview_slot.container():
                st.markdown(
                    '<div class="logo-preview">'
                    '<p class="logo-preview-label">Preview do logo</p>'
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.image(logo_file, width=220)
        else:
            logo_preview_slot.caption(
                "Envie um PNG ou JPG para visualizar o logo do cliente."
            )

        premissas_file = st.file_uploader(
            "Anexar premissas e restrições (MD/TXT)",
            type=["txt", "md"],
            key="premissas_uploader",
            help="O texto do arquivo preenche o campo abaixo para revisão.",
        )
        _apply_upload_to_field(
            uploaded=premissas_file,
            text_key="premissas_restricoes",
            fingerprint_key="_premissas_file_id",
            label="Premissas e restrições",
        )
        if premissas_file is not None:
            st.caption(f"Anexo: **{premissas_file.name}** — revise o texto abaixo.")
        premissas_text = st.text_area(
            "Premissas e restrições",
            height=120,
            key="premissas_restricoes",
            placeholder=(
                "Premissas:\n"
                "- Acesso aos sistemas legado disponível\n"
                "- Stakeholders alinhados no kick-off\n"
                "Restrições:\n"
                "- Sem integração em tempo real\n"
                "- Infraestrutura cloud sob responsabilidade do cliente"
            ),
            help=(
                "Itens explícitos do projeto. Use blocos Premissas: e "
                "Restrições: (um item por linha). Ou anexe um .md/.txt."
            ),
        )

        if mode == "package":
            pkg_fields = pkg.get("fields") or []
            if pkg_fields:
                with st.container(border=True, key="sub_pkg"):
                    _card_head(
                        "Campos da oferta",
                        "Valores que entram na proposta. O layout do "
                        "template oficial não muda.",
                        icon_svg=ICON_BRIEF,
                    )
                    rows = [
                        pkg_fields[i : i + 2]
                        for i in range(0, len(pkg_fields), 2)
                    ]
                    for row in rows:
                        cols = st.columns(len(row) or 1, gap="medium")
                        for col, field in zip(cols, row):
                            fid = field["id"]
                            ftype = field.get("type") or "text"
                            label_f = field.get("label") or fid
                            ph = field.get("placeholder") or ""
                            key = f"pkg_{pkg['id']}_{fid}"
                            with col:
                                if ftype == "textarea":
                                    field_values[fid] = st.text_area(
                                        label_f,
                                        key=key,
                                        placeholder=ph,
                                        height=100,
                                    )
                                elif fid in {"total", "valor_suporte"}:
                                    field_values[fid] = st.text_input(
                                        label_f,
                                        key=key,
                                        placeholder=ph or "R$ 0,00",
                                        on_change=_on_money_field_change,
                                        args=(key,),
                                    )
                                elif fid in {"tempo_execucao"}:
                                    field_values[fid] = st.text_input(
                                        label_f,
                                        key=key,
                                        placeholder=ph or "8",
                                        on_change=_on_weeks_field_change,
                                        args=(key,),
                                    )
                                else:
                                    field_values[fid] = st.text_input(
                                        label_f, key=key, placeholder=ph
                                    )
            if _uses_brief_field(selected_id):
                brief = _render_brief_context_field()
                field_values["brief"] = (brief or "").strip()
        else:
            brief = _render_brief_context_field()

            with st.expander(
                "Anexos opcionais (transcrição e estimativa)",
                icon=":material/attach_file:",
            ):
                st.caption(
                    "Opcional. Use se tiver ata de reunião ou estimativa "
                    "técnica além do brief."
                )
                transcription_file = st.file_uploader(
                    "Anexar transcrição",
                    type=["txt", "md", "vtt", "srt", "pdf"],
                    key="transcription_uploader",
                    help="O texto extraído preenche o campo abaixo.",
                )
                _apply_upload_to_field(
                    uploaded=transcription_file,
                    text_key="transcription_text",
                    fingerprint_key="_transcription_file_id",
                    label="Transcrição",
                )
                transcription = st.text_area(
                    "Transcrição da reunião",
                    height=160,
                    key="transcription_text",
                    placeholder="Cole aqui a transcrição da reunião…",
                )
                estimate_file = st.file_uploader(
                    "Anexar estimativa (PDF)",
                    type=["pdf"],
                    key="estimate_uploader",
                    help="O texto extraído do PDF preenche o campo abaixo.",
                )
                _apply_upload_to_field(
                    uploaded=estimate_file,
                    text_key="estimate_text",
                    fingerprint_key="_estimate_file_id",
                    label="Estimativa",
                )
                estimate = st.text_area(
                    "Estimativa técnica",
                    height=160,
                    key="estimate_text",
                    placeholder=(
                        "Cole aqui a estimativa técnica ou anexe o PDF…"
                    ),
                )

        if step == 2:
            code_ok = _is_valid_project_code(project_code)
            if project_code.strip() and not code_ok:
                st.warning("Código inválido. Use o formato AAA999-99 (ex.: BUI001-26).")
            _wizard_nav(
                step=2,
                can_advance=code_ok,
                skip_info=_skips_info_step(selected_id),
            )

    # —— Painel 3: Gerar + Resultado ——
    with st.container(border=True, key="wizard_panel_3"):
        _card_head(
            "Gerar proposta",
            "Revise e gere o PPTX oficial.",
            step=3,
        )
        st.markdown(
            f'<p class="checklist"><b>Tipo:</b> {label} · '
            f"<b>Cliente:</b> {(client_name or '—').strip() or '—'} · "
            f"<b>Código:</b> {(project_code or '—').strip() or '—'}</p>",
            unsafe_allow_html=True,
        )
        if mode == "package":
            if selected_id == "clarion":
                st.markdown(
                    '<p class="checklist"><b>Clarion:</b> deck estático — '
                    "gere o PPTX sem preencher formulário.</p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p class="checklist"><b>Antes de gerar:</b> cliente, código e '
                    "campos obrigatórios da oferta preenchidos.</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p class="checklist"><b>Mínimo para Livre:</b> cliente + código + '
                "brief (ou transcrição/estimativa).</p>",
                unsafe_allow_html=True,
            )

        left, right = st.columns([1.2, 1], gap="medium")
        with left:
            generate = st.button(
                f"Gerar {label}" if mode == "package" else "Gerar proposta Livre",
                type="primary",
                use_container_width=True,
                icon=":material/rocket_launch:",
                key="generate_pptx",
            )
        with right:
            with st.container(border=True, key="card_result"):
                _card_head(
                    "Resultado",
                    "Download quando a geração terminar.",
                    icon_svg=ICON_RESULT,
                )
                result_box = st.empty()
                download_box = st.empty()
                last = st.session_state.get("last_result")
                if last:
                    result_box.markdown(
                        _result_success_html(
                            file_name=str(last.get("file_name") or ""),
                            client=str(last.get("client") or ""),
                            code=str(last.get("code") or ""),
                            type_label=str(last.get("type_label") or ""),
                            size_label=str(last.get("size_label") or ""),
                        ),
                        unsafe_allow_html=True,
                    )
                    path = Path(str(last.get("path") or ""))
                    with download_box.container():
                        if path.is_file():
                            st.download_button(
                                label="Baixar PPTX",
                                data=path.read_bytes(),
                                file_name=path.name,
                                mime=(
                                    "application/vnd.openxmlformats-officedocument"
                                    ".presentationml.presentation"
                                ),
                                use_container_width=True,
                                icon=":material/download:",
                                key="download_result_persisted",
                            )
                        if st.button(
                            "Ver detalhes da proposta",
                            use_container_width=True,
                            key="open_result_dialog_persisted",
                            icon=":material/open_in_new:",
                        ):
                            st.session_state.open_result_modal = True
                            st.rerun()
                else:
                    result_box.markdown(
                        _result_empty_state(), unsafe_allow_html=True
                    )

        if step == 3:
            _wizard_nav(
                step=3,
                can_advance=False,
                skip_info=_skips_info_step(selected_id),
            )

    _footer_note()

    if step != 3 or not generate:
        return

    if selected_id == "clarion":
        if not _is_valid_project_code(project_code):
            project_code = "CLA000-00"
    elif not _is_valid_project_code(project_code):
        result_box.error(
            "Código da proposta inválido. Use AAA999-99 (ex.: BUI001-26)."
        )
        return

    if mode == "package":
        _run_package_generation(
            pkg=pkg,
            label=label,
            field_values=field_values,
            master_path=master_path,
            client_name=client_name,
            project_code=project_code,
            logo_file=logo_file,
            result_box=result_box,
            download_box=download_box,
        )
        return

    _run_livre_generation(
        brief=brief,
        transcription=transcription,
        estimate=estimate,
        premissas_text=premissas_text,
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        client_name=client_name,
        project_code=project_code,
        logo_file=logo_file,
        result_box=result_box,
        download_box=download_box,
    )


def _run_package_generation(
    *,
    pkg: dict,
    label: str,
    field_values: dict[str, str],
    master_path: Path,
    client_name: str,
    project_code: str,
    logo_file,
    result_box,
    download_box,
) -> None:
    missing_req = [
        f.get("label") or f["id"]
        for f in (pkg.get("fields") or [])
        if f.get("required") and not (field_values.get(f["id"]) or "").strip()
    ]
    if missing_req:
        result_box.error(
            "Preencha os campos obrigatórios: " + ", ".join(missing_req)
        )
        return

    logo_path = _resolve_logo_path(logo_file, client_name)
    out_path = _build_output_path(
        project_code=project_code,
        type_id=str(pkg.get("id") or "pacote"),
    )
    loading = FullscreenLoading(title=f"Gerando {label}")
    loading.update(5, "Iniciando geração…")
    try:
        out_path, values = build_package_deck(
            pkg,
            field_values=field_values,
            output_path=out_path,
            client_name=client_name.strip(),
            project_code=project_code.strip(),
            logo_path=logo_path,
            on_progress=loading.update,
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao montar PPTX: {exc}")
        return

    loading.update(100, "Proposta pronta!")
    loading.close()
    _show_download(
        result_box=result_box,
        download_box=download_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": pkg.get("id"),
            "type_label": label,
            "template": str(master_path),
            "section_slides": values.get("_section_slides", ""),
        },
    )


def _run_livre_generation(
    *,
    brief: str,
    transcription: str,
    estimate: str,
    premissas_text: str,
    provider: str,
    api_key: str,
    model: str,
    base_url: str | None,
    client_name: str,
    project_code: str,
    logo_file,
    result_box,
    download_box,
) -> None:
    if not api_key.strip():
        result_box.error(
            "API Key OpenAI não configurada. Defina OPENAI_API_KEY no arquivo .env."
        )
        return

    full_brief = _build_full_brief(
        brief, transcription, estimate, premissas=premissas_text
    )
    if not full_brief.strip():
        result_box.error(
            "Preencha pelo menos um dos campos: "
            "brief, transcrição ou estimativa técnica."
        )
        return

    loading = FullscreenLoading(title="Gerando proposta Livre")
    loading.update(8, "Escaneando tokens {NOME} do slide mestre…")
    try:
        master = P.master_template_path()
        catalog = load_named_token_catalog(master)
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao carregar slide mestre: {exc}")
        return

    if not catalog:
        loading.close()
        result_box.error(
            "Nenhum token {NOME} encontrado no slide mestre. "
            "Adicione placeholders no PPTX e tente de novo."
        )
        return

    loading.update(28, f"Enviando brief ao LLM ({len(catalog)} tokens)…")
    try:
        values = fill_slots(
            provider=provider,
            api_key=api_key.strip(),
            brief=full_brief,
            catalog=catalog,
            model=model.strip(),
            example_values=load_example_values(),
            project_code=project_code.strip(),
            client_name=client_name.strip(),
            base_url=base_url,
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha na chamada ao LLM: {exc}")
        return

    loading.update(72, "Textos recebidos. Montando PPTX…")
    values = _apply_premissas_to_values(values, premissas_text)

    empty = [k for k, v in values.items() if not str(v).strip()]
    if empty:
        result_box.info(
            f"{len(empty)} token(s) sem conteúdo (ficarão vazios no slide) — "
            "normal quando o brief não traz cronograma/premissas."
        )

    logo_path = _resolve_logo_path(logo_file, client_name)
    out_path = _build_output_path(
        project_code=project_code,
        type_id="livre",
    )

    loading.update(88, "Substituindo apenas {TOKENS} no mestre…")
    try:
        build_livre_deck(
            values,
            output_path=out_path,
            logo_path=logo_path,
            client_name=client_name.strip(),
            project_code=project_code.strip(),
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao montar PPTX: {exc}")
        return

    loading.update(100, "Proposta pronta!")
    loading.close()
    _show_download(
        result_box=result_box,
        download_box=download_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": "livre",
            "type_label": "Livre",
            "template": str(master),
            "provider": provider,
            "model": model,
            "tokens": len(catalog),
        },
    )


def render_geradas() -> None:
    _page_header(
        "Propostas geradas",
        "Arquivos PPTX criados nesta instalação, do mais recente ao mais antigo.",
    )
    files = sorted(
        P.output_dir().glob("*.pptx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        with st.container(border=True, key="card_geradas_vazio"):
            st.markdown(
                '<div class="result-empty">'
                f'<div class="result-empty-icon">{ICON_FILE}</div>'
                "<h4>Nenhuma proposta ainda</h4>"
                "<p>As propostas geradas aparecem aqui com opção de download.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        _footer_note()
        return

    for idx, path in enumerate(files):
        with st.container(border=True, key=f"card_gerada_{idx}"):
            info_col, btn_col = st.columns([3, 1], gap="medium")
            with info_col:
                st.markdown(
                    f'<div class="file-row">{ICON_FILE}<div>'
                    f"<b>{path.name}</b>"
                    f"<small>{_mtime_label(path)} · "
                    f"{_human_size(path.stat().st_size)}</small>"
                    "</div></div>",
                    unsafe_allow_html=True,
                )
            with btn_col:
                st.download_button(
                    "Baixar",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime=(
                        "application/vnd.openxmlformats-officedocument"
                        ".presentationml.presentation"
                    ),
                    use_container_width=True,
                    key=f"dl_{idx}",
                )
    _footer_note()


def render_templates() -> None:
    _page_header(
        "Modelos de template",
        "Slide mestre em uso, suas seções e os tokens disponíveis.",
    )
    try:
        master = P.master_template_path()
    except FileNotFoundError as exc:
        st.error(str(exc))
        _footer_note()
        return

    with st.container(border=True, key="card_master"):
        _card_head("Slide mestre", str(master), icon_svg=ICON_FILE)
        st.markdown(
            f'<p class="meta-line">Arquivo: <b>{master.name}</b></p>'
            f'<p class="meta-line">Tamanho: <b>{_human_size(master.stat().st_size)}</b>'
            f" · Atualizado em <b>{_mtime_label(master)}</b></p>",
            unsafe_allow_html=True,
        )
        summary = _template_summary(str(master), master.stat().st_mtime)
        sections = summary["sections"]
        tokens = summary["tokens"]
        st.markdown(
            f'<p class="meta-line">Seções: <b>{len(sections)}</b>'
            f" · Tokens <code>{{NOME}}</code>: <b>{len(tokens)}</b></p>",
            unsafe_allow_html=True,
        )
        for name, count in sections.items():
            st.markdown(
                f'<p class="meta-line">• {name} — <b>{count} slide(s)</b></p>',
                unsafe_allow_html=True,
            )
        with st.expander(f"Tokens do mestre ({len(tokens)})", icon=":material/code:"):
            st.code("\n".join(tokens) or "(nenhum)", language="text")

    with st.container(border=True, key="card_tipos"):
        _card_head(
            "Tipos de proposta",
            "Registrados em data/packages.json.",
            icon_svg=ICON_BRIEF,
        )
        for item in list_proposal_types():
            mode = item.get("mode") or "llm_full"
            section = item.get("section") or "—"
            st.markdown(
                f'<p class="meta-line"><b>{item.get("label") or item["id"]}</b>'
                f" · modo <code>{mode}</code> · seção <code>{section}</code></p>",
                unsafe_allow_html=True,
            )
    _footer_note()


def render_historico() -> None:
    _page_header(
        "Histórico",
        "Metadados das gerações (cliente, código, tipo e valores usados).",
    )
    entries = sorted(
        P.output_dir().glob("*.values.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not entries:
        with st.container(border=True, key="card_hist_vazio"):
            st.markdown(
                '<div class="result-empty">'
                f'<div class="result-empty-icon">{ICON_RESULT}</div>'
                "<h4>Sem histórico</h4>"
                "<p>Cada proposta gerada registra aqui os valores aplicados "
                "no template.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        _footer_note()
        return

    for idx, path in enumerate(entries):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        with st.container(border=True, key=f"card_hist_{idx}"):
            st.markdown(
                f'<div class="file-row">{ICON_FILE}<div>'
                f'<b>{path.name.replace(".values.json", "")}</b>'
                f"<small>{_mtime_label(path)}</small>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p class="meta-line">Cliente: <b>{payload.get("client") or "—"}</b>'
                f' · Código: <b>{payload.get("code") or "—"}</b>'
                f' · Tipo: <b>{payload.get("type") or "—"}</b></p>',
                unsafe_allow_html=True,
            )
            with st.expander("Valores aplicados", icon=":material/data_object:"):
                st.json(payload.get("values") or {})
    _footer_note()


def render_config() -> None:
    _page_header(
        "Configurações",
        "Caminhos, template ativo e preferências desta instalação.",
    )
    try:
        master = str(P.master_template_path())
    except FileNotFoundError as exc:
        master = f"não encontrado ({exc})"

    with st.container(border=True, key="card_paths"):
        _card_head("Caminhos", "Resolvidos automaticamente.", icon_svg=ICON_FILE)
        rows = [
            ("Diretório de dados", str(P.UNISANTA)),
            ("Slide mestre", master),
            ("Registry de tipos", str(P.packages_registry_path())),
            ("Saída das propostas", str(P.output_dir())),
        ]
        for name, value in rows:
            st.markdown(
                f'<p class="meta-line">{name}: <b>{value}</b></p>',
                unsafe_allow_html=True,
            )

    with st.container(border=True, key="card_llm_defaults"):
        _card_head(
            "Modelos padrão",
            "Sugestões usadas no modo Livre (pode alterar na geração).",
            icon_svg=ICON_SPARK,
        )
        for prov, mod in DEFAULT_MODELS.items():
            st.markdown(
                f'<p class="meta-line">{prov}: <code>{mod}</code></p>',
                unsafe_allow_html=True,
            )
        gate = "ativo" if os.environ.get("APP_PASSWORD", "").strip() else "desativado"
        st.markdown(
            f'<p class="meta-line">Senha de acesso (APP_PASSWORD): <b>{gate}</b></p>',
            unsafe_allow_html=True,
        )
    _footer_note()


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
