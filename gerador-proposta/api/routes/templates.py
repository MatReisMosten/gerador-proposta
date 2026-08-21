"""GET /api/templates/summary — equivalente a screens/other_pages.py::render_templates."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from generator import paths as P
from generator.engine import scan_named_tokens
from generator.packages import read_pptx_sections

from ..formatting import human_size
from ..schemas import TemplateSummary

router = APIRouter()


@router.get("/templates/summary", response_model=TemplateSummary)
def get_template_summary() -> TemplateSummary:
    try:
        master = P.master_template_path()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    sections = read_pptx_sections(master)
    tokens = scan_named_tokens(master)
    return TemplateSummary(
        name=master.name,
        size_label=human_size(master.stat().st_size),
        updated_at=datetime.fromtimestamp(master.stat().st_mtime).strftime(
            "%d/%m/%Y %H:%M"
        ),
        sections={name: len(slides) for name, slides in sections.items()},
        tokens=sorted(tokens),
    )
