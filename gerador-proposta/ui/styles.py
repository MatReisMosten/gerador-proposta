"""CSS de tema (claro/escuro) do Gerador de Propostas Mosten."""

from __future__ import annotations

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
