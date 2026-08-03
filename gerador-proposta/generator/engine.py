"""PPTX template engine: parameterize, fill slots, typography, logo."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

from . import paths as P

sys.path.insert(0, str(P.APP_ROOT))
from proposal_library.importer import delete_slide  # noqa: E402
from proposal_library.placeholder_applier import (  # noqa: E402
    _iter_shapes,
    _set_shape_text,
)


def shape_full_text(shape) -> str:
    return "\n".join(p.text for p in shape.text_frame.paragraphs)


def dominant_size_pt(shape) -> int | None:
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            if run.text.strip() and run.font.size:
                return int(run.font.size.pt)
    return None


def classify_role(size: int | None, text: str, slide_no: int, slot: int) -> str:
    t = text.strip()
    if t in {"1", "2", "3", "4", "“", "R$"} or t.startswith("R$"):
        return "keep"
    if size is not None and size >= 60:
        return "display"
    if size is not None and size >= 40 and slide_no in {1, 2, 19, 20}:
        return "cover_title"
    if size is not None and size >= 28:
        return "title"
    if size == 16:
        return "subtitle"
    if size in {13, 14, 18, 21} and len(t) > 40:
        return "subtitle"
    if size is not None and size <= 14 and len(t) <= 40:
        return "label"
    return "body"


def drop_bank_slides(pptx_path: Path) -> int:
    prs = Presentation(str(pptx_path))
    removed = 0
    for i in range(len(prs.slides) - 1, -1, -1):
        if (i + 1) in P.BANK_SLIDES_1BASED:
            delete_slide(prs, i)
            removed += 1
    prs.save(str(pptx_path))
    return removed


def parameterize(pptx_path: Path) -> tuple[dict[str, str], dict[str, dict]]:
    prs = Presentation(str(pptx_path))
    originals: dict[str, str] = {}
    meta: dict[str, dict] = {}

    for si, slide in enumerate(prs.slides, start=1):
        ti = 0
        for shape in _iter_shapes(slide.shapes):
            if not hasattr(shape, "text_frame") or not shape.has_text_frame:
                continue
            text = shape_full_text(shape)
            if not text.strip() or text.strip() in P.KEEP_AS_IS:
                continue
            size = dominant_size_pt(shape)
            role = classify_role(size, text, si, ti)
            key = f"{{S{si:02d}_T{ti:02d}}}"
            originals[key] = text
            meta[key] = {"role": role, "size": size, "slide": si, "slot": ti}
            _set_shape_text(shape, key)
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    run.font.name = P.FONT
                    if role == "title":
                        run.font.size = Pt(P.TITLE_PT)
                    elif role == "cover_title":
                        run.font.size = Pt(P.COVER_TITLE_PT)
                    elif role == "subtitle":
                        run.font.size = Pt(P.SUBTITLE_PT)
                    elif size:
                        run.font.size = Pt(size)
            ti += 1

    prs.save(str(pptx_path))
    return originals, meta


def apply_values_and_typography(
    pptx_path: Path,
    values: dict[str, str],
    meta: dict[str, dict],
) -> int:
    ordered = sorted(values.items(), key=lambda kv: len(kv[0]), reverse=True)
    prs = Presentation(str(pptx_path))
    modified = 0

    def style_runs(shape, role: str | None, fallback_size: int | None = None):
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.font.name = P.FONT
                if role == "title":
                    run.font.size = Pt(P.TITLE_PT)
                    run.font.bold = True
                elif role == "cover_title":
                    run.font.size = Pt(P.COVER_TITLE_PT)
                    run.font.bold = True
                elif role == "subtitle":
                    run.font.size = Pt(P.SUBTITLE_PT)
                elif role == "display":
                    if run.font.size is None:
                        run.font.size = Pt(fallback_size or 64)
                elif role == "label":
                    run.font.size = Pt(min(fallback_size or 13, 14))
                elif role == "body":
                    run.font.size = Pt(fallback_size or 12)
                elif fallback_size:
                    run.font.size = Pt(fallback_size)

    for slide in prs.slides:
        for shape in _iter_shapes(slide.shapes):
            if not hasattr(shape, "text_frame"):
                continue
            full = shape_full_text(shape)
            if not full.strip():
                continue

            roles = []
            sizes = []
            for k, info in meta.items():
                if k in full:
                    roles.append(info.get("role"))
                    if info.get("size"):
                        sizes.append(info["size"])

            pending = [(k, v) for k, v in ordered if k and k in full]
            if not pending and not roles:
                style_runs(shape, None)
                continue

            remaining = []
            for old, val in pending:
                placed = False
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if old in run.text:
                            run.text = run.text.replace(old, str(val))
                            placed = True
                if not placed:
                    remaining.append((old, val))

            if remaining:
                full2 = shape_full_text(shape)
                new = full2
                for old, val in remaining:
                    new = new.replace(old, str(val))
                if new != full2:
                    _set_shape_text(shape, new)

            role = None
            for candidate in (
                "cover_title",
                "title",
                "subtitle",
                "display",
                "label",
                "body",
            ):
                if candidate in roles:
                    role = candidate
                    break
            if roles and role is None:
                role = roles[0]

            style_runs(shape, role, max(sizes) if sizes else None)
            modified += 1

    prs.save(str(pptx_path))
    return modified


def replace_logo_cliente(pptx_path: Path, logo_path: Path) -> int:
    if not logo_path or not Path(logo_path).is_file():
        return 0
    prs = Presentation(str(pptx_path))
    replaced = 0
    for slide in prs.slides:
        targets = []
        for shape in _iter_shapes(slide.shapes):
            if not hasattr(shape, "text_frame"):
                continue
            text = shape_full_text(shape)
            if "{Logo_Cliente}" in text or "{LOGO_CLIENTE}" in text:
                targets.append(shape)
        for shape in targets:
            left, top, height = shape.left, shape.top, shape.height
            el = shape._element  # noqa: SLF001
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
            slide.shapes.add_picture(str(logo_path), left, top, height=height)
            replaced += 1
    if replaced:
        prs.save(str(pptx_path))
    return replaced


def ensure_parameterized_template(force: bool = False) -> tuple[Path, dict, dict]:
    """
    Ensure variaveis PPTX + slots JSON exist.
    Returns (template_path, originals, meta).
    """
    tpl = P.template_vars_path()
    slots_file = P.slots_path()

    if (
        not force
        and tpl.is_file()
        and slots_file.is_file()
    ):
        data = json.loads(slots_file.read_text(encoding="utf-8"))
        return tpl, data["originals"], data["meta"]

    model = P.resolve_model()
    P.UNISANTA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(model, tpl)
    drop_bank_slides(tpl)
    originals, meta = parameterize(tpl)
    slots_file.write_text(
        json.dumps({"meta": meta, "originals": originals}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return tpl, originals, meta


def build_deck(
    values: dict[str, str],
    *,
    output_path: Path,
    logo_path: Path | None = None,
    force_reparam: bool = False,
) -> Path:
    """Copy parameterized template, fill values, apply logo, save."""
    tpl, originals, meta = ensure_parameterized_template(force=force_reparam)

    # Fill missing keys with originals (keeps layout text if LLM skipped a slot)
    merged = dict(originals)
    for k, v in values.items():
        if v is not None and str(v).strip():
            merged[k] = str(v)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tpl, output_path)
    apply_values_and_typography(output_path, merged, meta)
    if logo_path:
        replace_logo_cliente(output_path, Path(logo_path))
    return output_path


def load_slot_catalog() -> dict:
    """Catalog for the LLM: key -> {role, original preview}."""
    _, originals, meta = ensure_parameterized_template()
    catalog = {}
    for key, original in originals.items():
        info = meta.get(key, {})
        catalog[key] = {
            "role": info.get("role", "body"),
            "slide": info.get("slide"),
            "original_example": original[:280],
        }
    return catalog
