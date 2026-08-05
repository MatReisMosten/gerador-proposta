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

NAV_ITEMS = [
    ("gerador", "Gerador de Propostas", ":material/description:"),
    ("geradas", "Propostas geradas", ":material/folder_open:"),
    ("templates", "Modelos de template", ":material/dashboard:"),
    ("historico", "Histórico", ":material/history:"),
    ("config", "Configurações", ":material/settings:"),
]

BRIEF_MAX_CHARS = 4000

FOOTER_NOTE = (
    "Seus dados são utilizados apenas para gerar a proposta e não são armazenados."
)

LIGHT_VARS = """
  --mosten-purple: #6C5CE7;
  --mosten-purple-dark: #5A4BD1;
  --mosten-purple-soft: #F1EFFE;
  --mosten-purple-mid: #DDD7FF;
  --mosten-purple-hover: #EAE6FF;
  --mosten-text: #1F2937;
  --mosten-muted: #6B7280;
  --mosten-border: #E9E7F3;
  --mosten-bg: #F7F6FB;
  --mosten-surface: #FFFFFF;
  --mosten-input: #FAFAFC;
  --mosten-sidebar: #FFFFFF;
  --mosten-success: #16A34A;
  --mosten-shadow: 0 2px 14px rgba(31, 41, 55, 0.04);
  --mosten-uploader-btn-bg: #FFFFFF;
"""

DARK_VARS = """
  --mosten-purple: #8B7CF0;
  --mosten-purple-dark: #A99BFF;
  --mosten-purple-soft: #2A2545;
  --mosten-purple-mid: #4A3F7A;
  --mosten-purple-hover: #342D55;
  --mosten-text: #F3F4F6;
  --mosten-muted: #9CA3AF;
  --mosten-border: #2E2A40;
  --mosten-bg: #12101A;
  --mosten-surface: #1A1726;
  --mosten-input: #15131F;
  --mosten-sidebar: #17141F;
  --mosten-success: #4ADE80;
  --mosten-shadow: 0 4px 22px rgba(0, 0, 0, 0.35);
  --mosten-uploader-btn-bg: #221E33;
"""


def build_theme_css(theme: str, active_page: str) -> str:
    """CSS do layout (sidebar + cards) com variáveis light/dark."""
    vars_block = DARK_VARS if theme == "Escuro" else LIGHT_VARS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {{
{vars_block}
}}

html, body, .stApp {{
  font-family: "Plus Jakarta Sans", sans-serif !important;
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

/* —— Sidebar —— */
[data-testid="stSidebar"] {{
  background: var(--mosten-sidebar) !important;
}}

/* Largura fixa só quando aberta: colapsada precisa zerar min/max-width */
[data-testid="stSidebar"][aria-expanded="true"] {{
  width: 268px !important;
  min-width: 268px !important;
  max-width: 268px !important;
  border-right: 1px solid var(--mosten-border) !important;
}}

[data-testid="stSidebar"][aria-expanded="false"] {{
  min-width: 0 !important;
  max-width: 0 !important;
  border-right: none !important;
}}

[data-testid="stSidebarHeader"] {{
  padding: 0.6rem 0.9rem 0 !important;
  height: auto !important;
}}

[data-testid="stSidebarUserContent"] {{
  padding: 0.2rem 0.85rem 1rem !important;
}}

[data-testid="stSidebarUserContent"] > div:first-child {{
  min-height: calc(100vh - 4.5rem);
}}

[data-testid="stSidebarNav"] {{
  display: none !important;
}}

[data-testid="stElementContainer"]:has(.sidebar-bottom) {{
  margin-top: auto;
}}

.sidebar-brand {{
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.35rem 0.4rem 0.9rem;
}}
.sidebar-brand svg {{
  width: 26px;
  height: 26px;
}}
.sidebar-brand span {{
  font-weight: 800;
  font-size: 0.98rem;
  letter-spacing: 0.06em;
  color: var(--mosten-text);
}}

.sidebar-tip {{
  border-radius: 12px;
  background: var(--mosten-purple-soft);
  border: 1px solid var(--mosten-border);
  padding: 0.7rem 0.8rem;
  margin-bottom: 0.7rem;
}}
.sidebar-tip strong {{
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: var(--mosten-purple-dark);
  margin-bottom: 0.25rem;
}}
.sidebar-tip strong svg {{
  width: 13px;
  height: 13px;
}}
.sidebar-tip p {{
  margin: 0;
  font-size: 0.72rem;
  line-height: 1.45;
  color: var(--mosten-muted) !important;
}}

.sidebar-user {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--mosten-border);
}}
.sidebar-user .avatar {{
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  background: var(--mosten-purple-soft);
  color: var(--mosten-purple-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
}}
.sidebar-user .who {{
  flex: 1;
  min-width: 0;
}}
.sidebar-user .who b {{
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--mosten-text);
  line-height: 1.2;
}}
.sidebar-user .who small {{
  font-size: 0.7rem;
  color: var(--mosten-muted);
}}
.sidebar-user svg {{
  width: 14px;
  height: 14px;
  color: var(--mosten-muted);
}}

/* Itens de navegação (botões) */
[data-testid="stSidebar"] [data-testid^="stBaseButton"] {{
  width: 100% !important;
  justify-content: flex-start !important;
  gap: 0.55rem !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 10px !important;
  color: var(--mosten-muted) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  padding: 0.5rem 0.7rem !important;
  box-shadow: none !important;
  text-align: left !important;
}}

[data-testid="stSidebar"] [data-testid^="stBaseButton"]:hover {{
  background: var(--mosten-purple-hover) !important;
  color: var(--mosten-text) !important;
}}

.st-key-nav_{active_page} [data-testid^="stBaseButton"] {{
  background: var(--mosten-purple-soft) !important;
  color: var(--mosten-purple-dark) !important;
  font-weight: 600 !important;
}}

[data-testid="stSidebar"] [data-testid="stElementContainer"] {{
  margin-bottom: 0.15rem;
}}

/* —— Área principal —— */
.stMainBlockContainer,
.block-container {{
  max-width: 1180px !important;
  padding: 1.5rem 2rem 2.4rem !important;
}}

.page-title {{
  margin: 0;
  font-size: 1.42rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--mosten-text) !important;
}}
.page-sub {{
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--mosten-muted) !important;
}}

/* Cards */
div[class*="st-key-card_"] {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 16px !important;
  box-shadow: var(--mosten-shadow) !important;
  padding: 1.15rem 1.25rem 0.85rem !important;
  margin-bottom: 1rem !important;
}}

div[class*="st-key-sub_"] {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 0.85rem 1rem 0.6rem !important;
  margin-bottom: 0.6rem !important;
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
  box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.15) !important;
}}

/* Upload */
[data-testid="stFileUploader"] {{
  margin-top: 0.1rem;
}}

[data-testid="stFileUploaderDropzone"] {{
  background: var(--mosten-purple-soft) !important;
  border: 1.5px dashed var(--mosten-purple-mid) !important;
  border-radius: 12px !important;
  padding: 0.75rem 0.9rem !important;
  flex-direction: column !important;
  text-align: center !important;
  gap: 0.35rem !important;
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

[data-testid="stFileUploader"] [data-testid^="stBaseButton"] {{
  background: var(--mosten-uploader-btn-bg) !important;
  color: var(--mosten-purple) !important;
  border: 1px solid var(--mosten-purple-mid) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
}}

/* Tipo de proposta — cards de seleção */
.st-key-proposal_type_id [data-testid="stRadioGroup"] {{
  display: flex !important;
  flex-wrap: wrap;
  gap: 0.75rem !important;
}}

.st-key-proposal_type_id label[data-baseweb="radio"] {{
  flex: 1 1 220px;
  margin: 0 !important;
  padding: 0.9rem 1rem !important;
  border: 1.5px solid var(--mosten-border);
  border-radius: 14px;
  background: var(--mosten-surface);
  transition: border-color 0.15s ease, background 0.15s ease;
}}

.st-key-proposal_type_id label[data-baseweb="radio"]:hover {{
  border-color: var(--mosten-purple-mid);
}}

.st-key-proposal_type_id label[data-baseweb="radio"]:has(input:checked) {{
  border-color: var(--mosten-purple);
  background: var(--mosten-purple-soft);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.09);
}}

.st-key-proposal_type_id label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {{
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  margin: 0 !important;
}}

.st-key-proposal_type_id label[data-baseweb="radio"] [data-testid="stCaptionContainer"] p {{
  font-size: 0.76rem !important;
  font-weight: 400 !important;
  line-height: 1.4;
  margin-top: 0.3rem !important;
  color: var(--mosten-muted) !important;
}}

/* Banner do modo + chip do template */
.mode-banner {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 0.85rem 0 0.35rem;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  border: 1px solid var(--mosten-border);
  background: var(--mosten-purple-soft);
}}
.mode-banner-text {{
  flex: 1 1 320px;
}}
.mode-banner-title {{
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.25rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--mosten-purple-dark) !important;
}}
.mode-banner-title svg {{
  width: 14px;
  height: 14px;
}}
.mode-banner-text p:last-child {{
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--mosten-muted) !important;
}}
.mode-banner-text code {{
  font-size: 0.72rem;
  background: transparent;
  color: var(--mosten-muted) !important;
}}
.tpl-chip {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--mosten-border);
  background: var(--mosten-surface);
}}
.tpl-chip svg {{
  width: 16px;
  height: 16px;
  color: var(--mosten-purple);
}}
.tpl-chip b {{
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--mosten-text);
}}
.tpl-chip small {{
  font-size: 0.7rem;
  color: var(--mosten-success);
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

/* Botão principal */
[data-testid="stBaseButton-primary"] {{
  background: linear-gradient(135deg, #6C5CE7 0%, #7B6BF0 100%) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  padding: 0.75rem 1rem !important;
  box-shadow: 0 8px 20px rgba(108, 92, 231, 0.28) !important;
  color: #fff !important;
}}

[data-testid="stBaseButton-primary"]:hover {{
  background: linear-gradient(135deg, #5A4BD1 0%, #6C5CE7 100%) !important;
}}

.footer-note {{
  margin: 0.85rem 0 0;
  text-align: center;
  font-size: 0.76rem;
  color: var(--mosten-muted) !important;
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
  border-radius: 999px;
  background: linear-gradient(90deg, var(--mosten-purple), var(--mosten-purple-dark));
  transition: width 0.35s ease;
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
  <path d="M4 26V6l12 12L28 6v20" stroke="#6C5CE7" stroke-width="3.4"
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
  <path d="M0 70 C 60 40, 110 95, 170 70 C 230 45, 280 90, 340 60 C 370 48, 390 55, 400 50 L400 120 L0 120 Z" fill="#EDE9FE"/>
  <path d="M0 85 C 70 55, 120 105, 190 80 C 250 58, 300 100, 360 75 C 380 68, 395 72, 400 70 L400 120 L0 120 Z" fill="#DDD6FE"/>
  <path d="M0 98 C 80 78, 140 110, 210 95 C 270 82, 320 108, 400 90 L400 120 L0 120 Z" fill="#C4B5FD" opacity="0.85"/>
  <g fill="#A78BFA" opacity="0.9">
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
        "theme_mode": "Claro",
        "page": "gerador",
        "_transcription_file_id": None,
        "_estimate_file_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
    st.session_state[text_key] = extracted
    st.session_state[fingerprint_key] = fp
    st.toast(f"{label}: texto extraído de {uploaded.name}")


def _build_full_brief(brief: str, transcription: str, estimate: str) -> str:
    parts: list[str] = []
    if brief.strip():
        parts.append(f"BRIEF:\n{brief.strip()}")
    if transcription.strip():
        parts.append(f"TRANSCRIÇÃO DA REUNIÃO:\n{transcription.strip()}")
    if estimate.strip():
        parts.append(f"ESTIMATIVA TÉCNICA:\n{estimate.strip()}")
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
    title_col, theme_col = st.columns([3, 1], gap="medium")
    with title_col:
        st.markdown(
            f'<p class="page-title">{title}</p>'
            f'<p class="page-sub">{subtitle}</p>',
            unsafe_allow_html=True,
        )
    if not with_theme:
        return
    with theme_col:
        with st.container(border=True, key="card_tema"):
            st.segmented_control(
                "Tema",
                options=["Claro", "Escuro"],
                key="theme_mode",
                format_func=lambda v: (
                    f":material/light_mode: {v}"
                    if v == "Claro"
                    else f":material/dark_mode: {v}"
                ),
            )


def _footer_note() -> None:
    st.markdown(f'<p class="footer-note">{FOOTER_NOTE}</p>', unsafe_allow_html=True)


def _sidebar() -> str:
    """Marca, navegação, dica e usuário. Retorna a página ativa."""
    user_name = os.environ.get("APP_USER_NAME", "Matheus Reis").strip() or "Usuário"
    user_org = os.environ.get("APP_USER_ORG", "HNS - MOSTEN").strip()
    initials = "".join(p[0] for p in user_name.split()[:2]).upper() or "M"

    with st.sidebar:
        st.markdown(
            f'<div class="sidebar-brand">{LOGO_SVG}<span>MOSTEN</span></div>',
            unsafe_allow_html=True,
        )
        for page_id, page_label, page_icon in NAV_ITEMS:
            if st.button(
                page_label,
                key=f"nav_{page_id}",
                icon=page_icon,
                type="tertiary",
                use_container_width=True,
            ):
                st.session_state.page = page_id
                st.rerun()

        st.markdown(
            '<div class="sidebar-bottom">'
            '<div class="sidebar-tip">'
            f"<strong>{ICON_SPARK} Dica rápida</strong>"
            "<p>Use o modo Livre para personalizar cada seção. "
            "Seu template mestre garante consistência.</p>"
            "</div>"
            '<div class="sidebar-user">'
            f'<div class="avatar">{initials}</div>'
            f'<div class="who"><b>{user_name}</b><small>{user_org}</small></div>'
            f"{ICON_CHEVRON}"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    return st.session_state.get("page", "gerador")


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
    <div class="mosten-loading-bar"><i style="width:{pct}%"></i></div>
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
        f'<div class="result-empty-icon">{ICON_RESULT}</div>'
        "<h4>Pronto para gerar</h4>"
        "<p>Preencha os campos ao lado e clique em gerar "
        "para criar a proposta.</p>"
        f"{RESULT_WAVE_SVG}"
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


def _build_output_path(
    *,
    output_name: str,
    project_code: str,
    client_name: str,
    type_slug: str = "",
) -> Path:
    code = project_code.strip() or "PROPOSTA"
    suffix = f" - {type_slug}" if type_slug else ""
    name = output_name.strip() or (
        f"{code}{suffix} - {slugify(client_name or 'cliente')} - "
        f"{date.today().isoformat()}.pptx"
    )
    if not name.lower().endswith(".pptx"):
        name += ".pptx"
    return P.output_dir() / name


def _show_download(
    *,
    result_box,
    download_box,
    json_box,
    out_path: Path,
    values: dict,
    meta: dict | None = None,
) -> None:
    src = (meta or {}).get("template")
    extra = f"\n\nTemplate: `{src}`" if src else ""
    result_box.success(f"Proposta gerada: `{out_path.name}`{extra}")
    download_box.download_button(
        label="Baixar PPTX",
        data=out_path.read_bytes(),
        file_name=out_path.name,
        mime=(
            "application/vnd.openxmlformats-officedocument"
            ".presentationml.presentation"
        ),
        use_container_width=True,
    )
    with json_box.expander("JSON dos valores (debug)"):
        st.json(values)

    payload = {
        "client": meta.get("client") if meta else None,
        "code": meta.get("code") if meta else None,
        "type": meta.get("type") if meta else None,
        "template": meta.get("template") if meta else None,
        "provider": meta.get("provider") if meta else None,
        "model": meta.get("model") if meta else None,
        "values": values,
    }
    values_path = out_path.with_suffix(".values.json")
    values_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


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
        "Crie propostas profissionais com agilidade e consistência.",
    )

    # —— 1. Dados da proposta ——
    with st.container(border=True, key="card_dados"):
        _card_head(
            "Dados da proposta",
            "Informações básicas usadas em todos os tipos de proposta.",
            step=1,
        )
        g1, g2, g3, g4 = st.columns(4, gap="medium")
        with g1:
            client_name = st.text_input("Cliente", placeholder="NPH / Unisanta")
        with g2:
            project_code = st.text_input(
                "Código da proposta", placeholder="UNS001-26"
            )
        with g3:
            output_name = st.text_input(
                "Nome do arquivo", value="", placeholder="auto"
            )
        with g4:
            logo_file = st.file_uploader(
                "Logo do cliente (PNG/JPG)",
                type=["png", "jpg", "jpeg"],
            )

    # —— Configuração LLM ——
    provider = "openai"
    model = DEFAULT_MODELS["openai"]
    api_key = ""
    base_url = None
    with st.expander("Configuração LLM (modo Livre)", icon=":material/tune:"):
        st.caption(
            "Usado apenas no modo Livre. Pacotes como Professional Service "
            "não precisam de LLM."
        )
        l1, l2, l3, l4 = st.columns(4, gap="medium")
        with l1:
            provider = st.selectbox(
                "Provider",
                options=["openai", "anthropic", "openrouter"],
                format_func=lambda x: {
                    "openai": "OpenAI",
                    "anthropic": "Anthropic",
                    "openrouter": "OpenRouter",
                }[x],
            )
        with l2:
            api_key = st.text_input(
                "API Key",
                type="password",
                help="A chave fica só nesta sessão. Não é salva em disco.",
                placeholder="sk-...",
            )
        with l3:
            model = st.text_input(
                "Modelo",
                value=DEFAULT_MODELS[provider],
                help="Prefira modelos baratos (mini/haiku/flash).",
            )
        with l4:
            if provider == "openrouter":
                base_url = st.text_input(
                    "Base URL", value="https://openrouter.ai/api/v1"
                )
            elif provider == "openai":
                custom = st.text_input("Base URL (opcional)", value="")
                base_url = custom.strip() or None
            else:
                st.caption("Base URL não necessária para Anthropic.")

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

    # —— 2. Tipo de proposta ——
    with st.container(border=True, key="card_tipo"):
        _card_head(
            "Tipo de proposta",
            "Escolha o tipo de proposta que deseja gerar.",
            step=2,
        )
        selected_id = st.radio(
            "Tipo de proposta",
            options=type_ids,
            index=type_ids.index("livre") if "livre" in type_ids else 0,
            format_func=lambda i: label_by_id[i],
            captions=[desc_by_id[i] for i in type_ids],
            horizontal=True,
            key="proposal_type_id",
            label_visibility="collapsed",
        )
        pkg = pkg_by_id[selected_id]
        mode = pkg.get("mode") or "llm_full"
        label = label_by_id[selected_id]

        if mode == "package":
            banner_text = (
                "Mantém só os slides da seção no mestre; textos fixos não mudam "
                "e apenas <code>{TOKENS}</code> e a tabela de investimento são "
                "preenchidos."
            )
        else:
            banner_text = (
                f"Utiliza o slide mestre (<code>{master_path.name}</code>): "
                "somente os tokens <code>{NOME}</code> são preenchidos; "
                "texto cru do template permanece."
            )
        st.markdown(
            '<div class="mode-banner">'
            '<div class="mode-banner-text">'
            f'<p class="mode-banner-title">{ICON_INFO} Sobre o modo {label}</p>'
            f"<p>{banner_text}</p>"
            "</div>"
            '<div class="tpl-chip">'
            f"{ICON_FILE}"
            f"<div><b>{master_path.name}</b><small>Template ativo</small></div>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    # —— 3. Informações da proposta + Resultado ——
    field_values: dict[str, str] = {}
    brief = transcription = estimate = ""

    left, right = st.columns([1.45, 1], gap="medium")

    with left:
        with st.container(border=True, key="card_info"):
            _card_head(
                "Informações da proposta",
                "Preencha os campos para gerar a proposta.",
                step=3,
            )

            if mode == "package":
                with st.container(border=True, key="sub_pkg"):
                    _card_head(
                        "Insumos do pacote",
                        "Campos variáveis da seção. Textos fixos do mestre "
                        "não mudam.",
                        icon_svg=ICON_BRIEF,
                    )
                    pkg_fields = pkg.get("fields") or []
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
                                else:
                                    field_values[fid] = st.text_input(
                                        label_f, key=key, placeholder=ph
                                    )
            else:
                with st.container(border=True, key="sub_brief"):
                    _card_head(
                        "Brief / contexto",
                        "Resumo da proposta, objetivos e contexto comercial.",
                        icon_svg=ICON_BRIEF,
                    )
                    brief = st.text_area(
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

                with st.expander(
                    "Transcrição da reunião", icon=":material/mic:"
                ):
                    st.caption(
                        "Cole a transcrição completa da reunião ou anexe "
                        "TXT, MD, VTT, SRT ou PDF."
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
                        "Transcrição",
                        height=200,
                        key="transcription_text",
                        label_visibility="collapsed",
                        placeholder="Cole aqui a transcrição da reunião…",
                    )

                with st.expander(
                    "Estimativa técnica", icon=":material/diamond:"
                ):
                    st.caption(
                        "Informe estimativas, prazos e recursos envolvidos "
                        "ou anexe o PDF."
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
                        height=200,
                        key="estimate_text",
                        label_visibility="collapsed",
                        placeholder=(
                            "Cole aqui a estimativa técnica ou anexe o PDF…"
                        ),
                    )

                with st.expander(
                    "Complemento rápido (opcional)", icon=":material/bolt:"
                ):
                    st.caption("Qualquer observação adicional relevante.")
                    follow = st.chat_input(
                        "Escreva algo ou pressione Enter para adicionar"
                    )
                    if follow:
                        st.session_state.messages.append(follow)
                        st.rerun()
                    for m in st.session_state.messages:
                        st.markdown(f"- {m}")
                    if st.session_state.messages and st.button(
                        "Limpar complementos", key="clear_messages"
                    ):
                        st.session_state.messages = []
                        st.rerun()

    with right:
        with st.container(border=True, key="card_result"):
            _card_head(
                "Resultado",
                "Acompanhe o status da geração.",
                icon_svg=ICON_RESULT,
            )
            result_box = st.empty()
            download_box = st.empty()
            json_box = st.empty()
            result_box.markdown(_result_empty_state(), unsafe_allow_html=True)

    generate = st.button(
        f"Gerar {label} PPTX" if mode == "package" else "Gerar proposta PPTX",
        type="primary",
        use_container_width=True,
        icon=":material/description:",
        key=f"generate_{selected_id}",
    )
    _footer_note()

    if not generate:
        return

    if mode == "package":
        _run_package_generation(
            pkg=pkg,
            label=label,
            field_values=field_values,
            master_path=master_path,
            client_name=client_name,
            project_code=project_code,
            output_name=output_name,
            logo_file=logo_file,
            result_box=result_box,
            download_box=download_box,
            json_box=json_box,
        )
        return

    _run_livre_generation(
        brief=brief,
        transcription=transcription,
        estimate=estimate,
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        client_name=client_name,
        project_code=project_code,
        output_name=output_name,
        logo_file=logo_file,
        result_box=result_box,
        download_box=download_box,
        json_box=json_box,
    )


def _run_package_generation(
    *,
    pkg: dict,
    label: str,
    field_values: dict[str, str],
    master_path: Path,
    client_name: str,
    project_code: str,
    output_name: str,
    logo_file,
    result_box,
    download_box,
    json_box,
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
        output_name=output_name,
        project_code=project_code,
        client_name=client_name,
        type_slug=slugify(pkg.get("id") or "pacote"),
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
        json_box=json_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": pkg.get("id"),
            "template": str(master_path),
            "section_slides": values.get("_section_slides", ""),
        },
    )


def _run_livre_generation(
    *,
    brief: str,
    transcription: str,
    estimate: str,
    provider: str,
    api_key: str,
    model: str,
    base_url: str | None,
    client_name: str,
    project_code: str,
    output_name: str,
    logo_file,
    result_box,
    download_box,
    json_box,
) -> None:
    if not api_key.strip():
        result_box.error("Informe a API Key em Configuração LLM.")
        return

    full_brief = _build_full_brief(brief, transcription, estimate)
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
    empty = [k for k, v in values.items() if not str(v).strip()]
    if empty:
        result_box.info(
            f"{len(empty)} token(s) sem conteúdo (ficarão vazios no slide) — "
            "normal quando o brief não traz cronograma/premissas."
        )

    logo_path = _resolve_logo_path(logo_file, client_name)
    out_path = _build_output_path(
        output_name=output_name,
        project_code=project_code,
        client_name=client_name,
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
        json_box=json_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": "livre",
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
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_session_defaults()
    st.markdown(
        build_theme_css(
            st.session_state.get("theme_mode") or "Claro",
            st.session_state.get("page", "gerador"),
        ),
        unsafe_allow_html=True,
    )

    if not gate_password():
        return

    active_page = _sidebar()
    PAGES.get(active_page, render_generator)()


if __name__ == "__main__":
    main()
