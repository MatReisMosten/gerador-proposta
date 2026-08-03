"""Paths for the proposal generator app (portable — vault local or bundled data/)."""

from __future__ import annotations

import os
from pathlib import Path

# proposal_app/ -> proposal-library-builder/ -> .agents/skills/ -> vault
APP_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = APP_ROOT.parent

MODEL_NAME = "Modelo-Proposta Tecnica v1.0.pptx"
TEMPLATE_VARS_NAME = "Modelo-Proposta-Tecnica-v1.0-variaveis.pptx"
SLOTS_NAME = "Modelo-Proposta-Tecnica-v1.0-slots.json"
EXAMPLE_VALUES_NAME = "UNS001-26-vigia-valores.json"

# Bank slides (1-based) removed from commercial decks
BANK_SLIDES_1BASED = {21, 22, 23, 24}

FONT = "Inter Tight"
TITLE_PT = 32
SUBTITLE_PT = 16
COVER_TITLE_PT = 40
KEEP_AS_IS = {"{Logo_Cliente}", "{LOGO_CLIENTE}"}


def _vault_unisanta() -> Path:
    return SKILL_ROOT.parents[2] / "01 - Propostas" / "Unisanta"


def _resolve_data_root() -> Path:
    """
    Preferência:
    1. PROPOSAL_DATA_DIR (deploy / override)
    2. Vault local (dev) se tiver slots ou modelo
    3. proposal_app/data (pacote Railway)
    """
    if os.environ.get("PROPOSAL_DATA_DIR"):
        return Path(os.environ["PROPOSAL_DATA_DIR"]).expanduser().resolve()

    vault_u = _vault_unisanta()
    bundled = APP_ROOT / "data"

    vault_ready = vault_u.is_dir() and (
        (vault_u / SLOTS_NAME).is_file()
        or (vault_u / "assets" / MODEL_NAME).is_file()
        or (vault_u / TEMPLATE_VARS_NAME).is_file()
    )
    if vault_ready:
        return vault_u

    if bundled.is_dir() and (
        (bundled / SLOTS_NAME).is_file()
        or (bundled / TEMPLATE_VARS_NAME).is_file()
        or (bundled / "assets" / MODEL_NAME).is_file()
    ):
        return bundled

    return vault_u if vault_u.is_dir() else bundled


UNISANTA = _resolve_data_root()
ASSETS = UNISANTA / "assets" if (UNISANTA / "assets").is_dir() else UNISANTA
# Retrocompat: alguns callers ainda leem VAULT
VAULT = UNISANTA.parent.parent if UNISANTA.name == "Unisanta" else APP_ROOT


def resolve_model() -> Path:
    candidates = [
        Path(os.environ["PROPOSAL_MODEL"]).expanduser()
        if os.environ.get("PROPOSAL_MODEL")
        else None,
        ASSETS / MODEL_NAME,
        UNISANTA / MODEL_NAME,
        UNISANTA / "assets" / MODEL_NAME,
        Path.home() / "Desktop" / MODEL_NAME,
    ]
    for path in candidates:
        if path and path.is_file():
            return path
    raise FileNotFoundError(
        f"{MODEL_NAME} não encontrado. Coloque em:\n"
        f"  - {ASSETS / MODEL_NAME}\n"
        f"  - {APP_ROOT / 'data' / 'assets' / MODEL_NAME}\n"
        f"  - ou defina PROPOSAL_MODEL=/caminho/arquivo.pptx\n"
        f"Rode: ./prepare_deploy.sh"
    )


def template_vars_path() -> Path:
    return UNISANTA / TEMPLATE_VARS_NAME


def slots_path() -> Path:
    return UNISANTA / SLOTS_NAME


def example_values_path() -> Path:
    return UNISANTA / EXAMPLE_VALUES_NAME


def output_dir() -> Path:
    d = Path(os.environ["PROPOSAL_OUTPUT_DIR"]).expanduser() if os.environ.get(
        "PROPOSAL_OUTPUT_DIR"
    ) else UNISANTA / "geradas"
    d.mkdir(parents=True, exist_ok=True)
    return d
