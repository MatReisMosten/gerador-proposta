"""Validação/formatação de campos — independente de UI (sem Streamlit).

Duplicado deliberadamente de `ui/formatting.py` em vez de importado: a API
não depende da camada Streamlit (`ui/`, `screens/`, `generation/`), que é a
parte a ser descomissionada quando a Fase 2 for para produção (ver
docs/plano-migracao-react.md). Qualquer mudança de regra de negócio aqui
precisa ser espelhada lá enquanto as duas cascas coexistirem.
"""

from __future__ import annotations

import re

PROJECT_CODE_RE = re.compile(r"^[A-Z]{3}\d{3}-\d{2}$")

TYPE_FILE_SUFFIX = {
    "suporte": "Proposta-Suporte-v1",
    "professional_service": "Professional-Service-v1",
    "passlog": "PassLog-v1",
    "discovery": "Discovery-v1",
    "clarion": "Clarion-v1",
    "escopo_fechado": "Escopo-Fechado-v1",
    "livre": "Proposta-Tecnica-v1",
}


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "proposta"


def is_valid_project_code(code: str) -> bool:
    return bool(PROJECT_CODE_RE.match((code or "").strip().upper()))


def proposal_file_stem(project_code: str, type_id: str) -> str:
    code = (project_code or "").strip().upper() or "XXX000-00"
    suffix = TYPE_FILE_SUFFIX.get(type_id) or f"{slugify(type_id) or 'Proposta'}-v1"
    return f"{code}-{suffix}"


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
