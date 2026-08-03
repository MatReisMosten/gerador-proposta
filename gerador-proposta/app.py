"""
Gerador de Propostas Mosten — Streamlit MVP.

Uso:
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from generator import build_deck, fill_slots, load_slot_catalog  # noqa: E402
from generator import paths as P  # noqa: E402
from generator.text_extract import TextExtractError, extract_text_from_bytes  # noqa: E402

DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "openrouter": "openai/gpt-4.1-mini",
}

LIGHT_VARS = """
  --mosten-purple: #6C5CE7;
  --mosten-purple-dark: #5A4BD1;
  --mosten-purple-soft: #F0EEFF;
  --mosten-purple-mid: #DDD7FF;
  --mosten-purple-hover: #EAE6FF;
  --mosten-text: #1F2937;
  --mosten-muted: #6B7280;
  --mosten-border: #E8E5F2;
  --mosten-bg: #F8F7FC;
  --mosten-surface: #FFFFFF;
  --mosten-input: #FAFAFC;
  --mosten-header-bg: rgba(248, 247, 252, 0.92);
  --mosten-shadow: 0 4px 18px rgba(31, 41, 55, 0.04);
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
  --mosten-header-bg: rgba(18, 16, 26, 0.92);
  --mosten-shadow: 0 4px 22px rgba(0, 0, 0, 0.35);
  --mosten-uploader-btn-bg: #221E33;
"""


def build_theme_css(theme: str) -> str:
    """CSS com variáveis light/dark."""
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

/* Navbar custom — mantém o botão de expandir/colapsar a sidebar */
header[data-testid="stHeader"] {{
  background: var(--mosten-surface) !important;
  border-bottom: 1px solid var(--mosten-border);
  height: 3.25rem;
  box-shadow: var(--mosten-shadow);
}}

[data-testid="stToolbar"] {{
  display: flex !important;
  align-items: center;
  right: 0.75rem;
}}

/* Esconde Deploy / decoração — não esconde o toggle da sidebar */
.stDeployButton,
div[data-testid="stDecoration"] {{
  display: none !important;
}}

/* Marca visual na navbar */
header[data-testid="stHeader"]::before {{
  content: "MOSTEN";
  position: absolute;
  left: 3.6rem;
  top: 50%;
  transform: translateY(-50%);
  font-family: "Plus Jakarta Sans", sans-serif;
  font-weight: 800;
  font-size: 0.82rem;
  letter-spacing: 0.12em;
  color: var(--mosten-purple);
  pointer-events: none;
}}

/* Botão quando a sidebar está colapsada (reabre) */
[data-testid="collapsedControl"] {{
  display: flex !important;
  align-items: center;
  justify-content: center;
  position: fixed !important;
  left: 0.85rem !important;
  top: 0.65rem !important;
  z-index: 999999 !important;
  width: 2.35rem !important;
  height: 2.35rem !important;
  border-radius: 10px !important;
  background: var(--mosten-purple) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 6px 16px rgba(108, 92, 231, 0.35) !important;
}}

[data-testid="collapsedControl"] svg {{
  color: #fff !important;
  fill: #fff !important;
}}

[data-testid="collapsedControl"]:hover {{
  background: var(--mosten-purple-dark) !important;
  transform: scale(1.04);
}}

/* Botão de colapsar dentro da sidebar / header */
[data-testid="stSidebarCollapseButton"] button,
button[kind="header"],
button[data-testid="baseButton-header"],
button[data-testid="baseButton-headerNoPadding"] {{
  background: var(--mosten-purple-soft) !important;
  color: var(--mosten-purple) !important;
  border: 1px solid var(--mosten-purple-mid) !important;
  border-radius: 10px !important;
  width: 2.2rem !important;
  height: 2.2rem !important;
}}

[data-testid="stSidebarCollapseButton"] button:hover,
button[kind="header"]:hover,
button[data-testid="baseButton-header"]:hover,
button[data-testid="baseButton-headerNoPadding"]:hover {{
  background: var(--mosten-purple) !important;
  color: #fff !important;
  border-color: var(--mosten-purple) !important;
}}

[data-testid="stSidebar"] {{
  background: var(--mosten-surface) !important;
  border-right: 1px solid var(--mosten-border);
}}

section[data-testid="stSidebar"] {{
  box-shadow: 4px 0 24px rgba(108, 92, 231, 0.06);
}}

[data-testid="stSidebar"] > div:first-child {{
  padding-top: 0.75rem;
}}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
  color: var(--mosten-purple) !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
}}

[data-testid="stSidebar"] h3 {{
  color: var(--mosten-text) !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{
  color: var(--mosten-text) !important;
}}

.block-container {{
  padding-top: 1.25rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1400px !important;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--mosten-surface) !important;
  border: 1px solid var(--mosten-border) !important;
  border-radius: 16px !important;
  box-shadow: var(--mosten-shadow);
  padding: 0.15rem 0.1rem;
}}

.section-head {{
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 0.85rem;
}}

.section-icon {{
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  background: var(--mosten-purple-soft);
  color: var(--mosten-purple);
  display: flex;
  align-items: center;
  justify-content: center;
}}

.section-icon svg {{
  width: 18px;
  height: 18px;
}}

.section-title {{
  margin: 0;
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--mosten-text) !important;
  letter-spacing: -0.02em;
  line-height: 1.2;
}}

.section-hint {{
  margin: 0.2rem 0 0;
  color: var(--mosten-muted) !important;
  font-size: 0.82rem;
  line-height: 1.4;
}}

.theme-label {{
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--mosten-muted) !important;
}}

/* Texto geral */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
label, .stMarkdown {{
  color: var(--mosten-text) !important;
}}

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
  min-height: 120px;
}}

.stTextArea textarea:focus {{
  border-color: var(--mosten-purple) !important;
  box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.15) !important;
}}

[data-testid="stFileUploader"] {{
  margin-top: 0.1rem;
  margin-bottom: 0.55rem;
}}

[data-testid="stFileUploader"] section {{
  background: var(--mosten-purple-soft) !important;
  border: 1.5px dashed var(--mosten-purple-mid) !important;
  border-radius: 12px !important;
  padding: 0.85rem 1rem !important;
}}

[data-testid="stFileUploader"] section:hover {{
  border-color: var(--mosten-purple) !important;
  background: var(--mosten-purple-hover) !important;
}}

[data-testid="stFileUploader"] section * {{
  color: var(--mosten-text) !important;
}}

[data-testid="stFileUploader"] button {{
  background: var(--mosten-uploader-btn-bg) !important;
  color: var(--mosten-purple) !important;
  border: 1px solid var(--mosten-purple-mid) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}}

div.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, #6C5CE7 0%, #7B6BF0 100%) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  padding: 0.7rem 1rem !important;
  box-shadow: 0 8px 20px rgba(108, 92, 231, 0.28) !important;
  color: #fff !important;
}}

div.stButton > button[kind="primary"]:hover {{
  background: linear-gradient(135deg, #5A4BD1 0%, #6C5CE7 100%) !important;
}}

.result-empty {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2.2rem 1.2rem 1.4rem;
  min-height: 280px;
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
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--mosten-text) !important;
}}

.result-empty p {{
  margin: 0;
  color: var(--mosten-muted) !important;
  font-size: 0.88rem;
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

.sidebar-caption {{
  color: var(--mosten-muted) !important;
  font-size: 0.75rem;
  margin-top: 0.35rem;
}}

.gen-wrap {{
  margin-top: 0.35rem;
}}

/* Radio tema na sidebar */
div[data-testid="stRadio"] div[role="radiogroup"] {{
  gap: 0.35rem;
}}

div[data-testid="stRadio"] label[data-baseweb="radio"] {{
  background: var(--mosten-input);
  border: 1px solid var(--mosten-border);
  border-radius: 999px;
  padding: 0.28rem 0.75rem;
  color: var(--mosten-text) !important;
}}

div[data-testid="stRadio"] label[data-baseweb="radio"] p,
div[data-testid="stRadio"] label[data-baseweb="radio"] span {{
  color: var(--mosten-text) !important;
}}

div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {{
  background: var(--mosten-purple-soft);
  border-color: var(--mosten-purple);
}}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] {{
  color: var(--mosten-text) !important;
  background: var(--mosten-surface) !important;
}}
</style>
"""

ICON_BRIEF = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <line x1="8" y1="13" x2="16" y2="13"/>
  <line x1="8" y1="17" x2="13" y2="17"/>
</svg>
"""

ICON_MIC = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
  <line x1="12" y1="19" x2="12" y2="23"/>
  <line x1="8" y1="23" x2="16" y2="23"/>
</svg>
"""

ICON_ESTIMATE = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <path d="M9 15l2 2 4-4"/>
</svg>
"""

ICON_RESULT = """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 18h6"/>
  <path d="M10 22h4"/>
  <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>
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
    import os

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


def _section_header(title: str, hint: str, icon_svg: str) -> None:
    st.markdown(
        f'<div class="section-head">'
        f'<div class="section-icon">{icon_svg}</div>'
        f"<div><p class=\"section-title\">{title}</p>"
        f'<p class="section-hint">{hint}</p></div></div>',
        unsafe_allow_html=True,
    )


def _result_empty_state() -> str:
    return (
        '<div class="result-empty">'
        f'<div class="result-empty-icon">{ICON_RESULT}</div>'
        "<h4>Pronto para gerar</h4>"
        "<p>Preencha os campos ao lado e o resultado da proposta "
        "aparecerá aqui.</p>"
        f"{RESULT_WAVE_SVG}"
        "</div>"
    )


def main() -> None:
    st.set_page_config(
        page_title="Gerador de Propostas Mosten",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_session_defaults()
    st.markdown(
        build_theme_css(st.session_state.get("theme_mode", "Claro")),
        unsafe_allow_html=True,
    )

    if not gate_password():
        return

    with st.sidebar:
        st.header("Configuração")
        st.radio(
            "Tema",
            options=["Claro", "Escuro"],
            horizontal=True,
            key="theme_mode",
        )

        provider = st.selectbox(
            "Provider",
            options=["openai", "anthropic", "openrouter"],
            format_func=lambda x: {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "openrouter": "OpenRouter",
            }[x],
        )
        api_key = st.text_input(
            "API Key",
            type="password",
            help="A chave fica só nesta sessão. Não é salva em disco.",
            placeholder="sk-...",
        )
        model = st.text_input(
            "Modelo",
            value=DEFAULT_MODELS[provider],
            help="Prefira modelos baratos (mini/haiku/flash).",
        )
        base_url = None
        if provider == "openrouter":
            base_url = st.text_input(
                "Base URL",
                value="https://openrouter.ai/api/v1",
            )
        elif provider == "openai":
            custom = st.text_input("Base URL (opcional)", value="")
            base_url = custom.strip() or None

        st.divider()
        st.subheader("Dados da proposta")
        client_name = st.text_input("Cliente", placeholder="NPH / Unisanta")
        project_code = st.text_input("Código", placeholder="UNS001-26")
        output_name = st.text_input(
            "Nome do arquivo",
            value="",
            placeholder="auto",
        )
        logo_file = st.file_uploader(
            "Logo do cliente (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
        )

        st.divider()
        st.markdown(
            f'<p class="sidebar-caption">Modelo PPTX: {P.MODEL_NAME}</p>',
            unsafe_allow_html=True,
        )
        try:
            st.markdown(
                f'<p class="sidebar-caption">Fonte: {P.resolve_model()}</p>',
                unsafe_allow_html=True,
            )
        except FileNotFoundError as exc:
            st.error(str(exc))

    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        with st.container(border=True):
            _section_header(
                "Brief / contexto",
                "Resumo da proposta, objetivos e contexto comercial.",
                ICON_BRIEF,
            )
            brief = st.text_area(
                "Brief",
                height=150,
                key="brief_text",
                label_visibility="collapsed",
                placeholder=(
                    "Exemplo:\n"
                    "Cliente: NPH/Unisanta\n"
                    "Produto: Vigia — camada de alertas de risco costeiro\n"
                    "Problema: dado científico não vira decisão em campo\n"
                    "Solução: tradução, segmentação, Prismia, feedback\n"
                    "Cronograma: 5 semanas\n"
                    "Preço: a definir / captação conjunta\n"
                    "CTA: validar parceria e ACT"
                ),
            )

        with st.container(border=True):
            _section_header(
                "Transcrição da reunião",
                "Cole o texto ou anexe TXT, MD, VTT, SRT ou PDF.",
                ICON_MIC,
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

        with st.container(border=True):
            _section_header(
                "Estimativa técnica",
                "Cole o texto ou anexe o PDF da estimativa.",
                ICON_ESTIMATE,
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
                placeholder="Cole aqui a estimativa técnica ou anexe o PDF…",
            )

        follow = st.chat_input("Complemento rápido (opcional)…")
        if follow:
            st.session_state.messages.append(follow)
        if st.session_state.messages:
            with st.expander("Complementos do chat", expanded=False):
                for m in st.session_state.messages:
                    st.markdown(f"- {m}")
                if st.button("Limpar complementos"):
                    st.session_state.messages = []
                    st.rerun()

        st.markdown('<div class="gen-wrap"></div>', unsafe_allow_html=True)
        generate = st.button(
            "Gerar proposta PPTX",
            type="primary",
            use_container_width=True,
        )

    with col2:
        with st.container(border=True):
            _section_header(
                "Resultado",
                "A proposta gerada aparece aqui.",
                ICON_RESULT,
            )
            result_box = st.empty()
            download_box = st.empty()
            json_box = st.empty()
            if not generate:
                result_box.markdown(_result_empty_state(), unsafe_allow_html=True)

    if generate:
        if not api_key.strip():
            st.error("Informe a API Key na barra lateral.")
            return

        full_brief = _build_full_brief(brief, transcription, estimate)
        if not full_brief.strip():
            st.error(
                "Preencha pelo menos um dos campos: "
                "brief, transcrição ou estimativa técnica."
            )
            return

        with st.spinner("Preparando template e slots…"):
            try:
                catalog = load_slot_catalog()
            except Exception as exc:
                st.error(f"Falha ao carregar template: {exc}")
                return

        with st.spinner("LLM preenchendo os textos da proposta…"):
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
                st.error(f"Falha na chamada ao LLM: {exc}")
                return

        missing = [k for k in catalog if k not in values]
        if missing:
            result_box.warning(
                f"{len(missing)} slots sem valor do LLM — "
                "preenchidos com texto original do modelo."
            )

        logo_path = None
        if logo_file is not None:
            tmp_logo = tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(logo_file.name).suffix
            )
            tmp_logo.write(logo_file.getvalue())
            tmp_logo.close()
            logo_path = Path(tmp_logo.name)
        else:
            default_logo = P.ASSETS / "logo-nph.png"
            if default_logo.is_file() and (
                not client_name
                or "nph" in client_name.lower()
                or "unisanta" in client_name.lower()
            ):
                logo_path = default_logo

        code = project_code.strip() or "PROPOSTA"
        name = output_name.strip() or (
            f"{code} - {slugify(client_name or 'cliente')} - "
            f"{date.today().isoformat()}.pptx"
        )
        if not name.lower().endswith(".pptx"):
            name += ".pptx"
        out_path = P.output_dir() / name

        with st.spinner("Montando PPTX…"):
            try:
                build_deck(values, output_path=out_path, logo_path=logo_path)
            except Exception as exc:
                st.error(f"Falha ao montar PPTX: {exc}")
                return

        result_box.success(f"Proposta gerada: `{out_path.name}`")
        data = out_path.read_bytes()
        download_box.download_button(
            label="Baixar PPTX",
            data=data,
            file_name=out_path.name,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            use_container_width=True,
        )
        with json_box.expander("JSON dos valores (debug)"):
            st.json(values)

        values_path = out_path.with_suffix(".values.json")
        values_path.write_text(
            json.dumps(
                {
                    "client": client_name,
                    "code": project_code,
                    "provider": provider,
                    "model": model,
                    "values": values,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
