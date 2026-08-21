"""GET /api/proposal-types — contrato declarativo do formulário por tipo.

O front não precisa saber "discovery e passlog também mostram brief" — a API
já resolve isso (`show_brief`, `show_attachments`, `requires_form`) a partir
de `data/packages.json` + das mesmas regras que o wizard Streamlit aplicava
em `screens/generator_page.py` (`_skips_info_step`, `_uses_brief_field`).
"""

from __future__ import annotations

from fastapi import APIRouter

from generator import list_proposal_types

from ..schemas import ProposalType

router = APIRouter()

_ALSO_SHOWS_BRIEF = {"discovery", "passlog"}


def _to_schema(pkg: dict) -> ProposalType:
    type_id = pkg["id"]
    mode = pkg.get("mode") or "llm_full"
    return ProposalType(
        id=type_id,
        label=pkg.get("label") or type_id,
        mode=mode,
        description=pkg.get("description") or "",
        fields=pkg.get("fields") or [],
        requires_form=type_id != "clarion",
        show_brief=mode != "package" or type_id in _ALSO_SHOWS_BRIEF,
        show_attachments=mode != "package",
        hide_client=bool(pkg.get("hide_client")),
        hide_logo=bool(pkg.get("hide_logo")),
    )


@router.get("/proposal-types", response_model=list[ProposalType])
def get_proposal_types() -> list[ProposalType]:
    ordered = sorted(
        list_proposal_types(),
        key=lambda t: (0 if t.get("mode") == "package" else 1, t.get("label") or ""),
    )
    return [_to_schema(t) for t in ordered]
