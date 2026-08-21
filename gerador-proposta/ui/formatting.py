"""Slugs, máscaras de campo e helpers de formatação/validação."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import streamlit as st

from generator import paths as P

PROJECT_CODE_RE = re.compile(r"^[A-Z]{3}\d{3}-\d{2}$")
TYPE_FILE_SUFFIX = {
    "suporte": "Proposta-Suporte-v1",
    "professional_service": "Professional-Service-v1",
    "passlog": "PassLog-v1",
    "discovery": "Discovery-v1",
    "clarion": "Clarion-v1",
    "livre": "Proposta-Tecnica-v1",
}


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "proposta"


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


def _format_months_only(raw: str) -> str:
    """Só dígitos — tempo em meses."""
    digits = re.sub(r"\D", "", raw or "")[:3]
    if not digits:
        return ""
    return str(int(digits))


def _on_money_field_change(key: str) -> None:
    st.session_state[key] = _format_money_br(st.session_state.get(key) or "")


def _on_months_field_change(key: str) -> None:
    st.session_state[key] = _format_months_only(st.session_state.get(key) or "")


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


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _mtime_label(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
