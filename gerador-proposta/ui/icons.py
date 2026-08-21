"""SVGs e mapas de ícones usados na UI do Gerador de Propostas Mosten."""

from __future__ import annotations

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
