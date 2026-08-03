"""Apply LLM enrichment JSON and commit slides into the library."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from . import CATEGORIES, DUPLICATE_THRESHOLD
from .duplicate_detector import find_best_duplicate
from .image_extractor import rename_images
from .library_manager import LibraryManager
from .metadata_builder import build_metadata
from .models import ApplyResult, SlideEnrichment, SlideExtraction
from .placeholder_applier import apply_placeholders, collect_texts_after_placeholders
from .utils import (
    ensure_dir,
    read_json,
    resolve_path,
    slide_stem,
    write_json,
)

logger = logging.getLogger(__name__)


def _load_enrichment(path: Path) -> SlideEnrichment:
    data = read_json(path)
    enrichment = SlideEnrichment.from_dict(data)
    if enrichment.type not in CATEGORIES:
        logger.warning(
            "Unknown type %r in %s — coercing to custom",
            enrichment.type,
            path.name,
        )
        enrichment.type = "custom"
    return enrichment


def apply_one_slide(
    staging_dir: Path,
    slide_number: int,
    library: LibraryManager,
    *,
    replace_id: str | None = None,
    skip: bool = False,
    force: bool = False,
    threshold: float = DUPLICATE_THRESHOLD,
) -> ApplyResult:
    stem = slide_stem(slide_number)
    extraction_path = staging_dir / f"{stem}.json"
    enrichment_path = staging_dir / "enrichment" / f"{stem}.json"
    pptx_path = staging_dir / f"{stem}.pptx"
    png_path = staging_dir / f"{stem}.png"
    images_dir = staging_dir / "images" / stem

    if skip:
        return ApplyResult(
            status="skipped",
            slide=slide_number,
            message="Skipped by user decision",
        )

    applied_marker = staging_dir / "enrichment" / f"{stem}.applied.json"
    if applied_marker.is_file() and replace_id is None and not force:
        prev = read_json(applied_marker)
        return ApplyResult(
            status="skipped",
            slide=slide_number,
            slide_id=prev.get("slide_id"),
            message=f"Already applied as {prev.get('slide_id')}",
        )

    if not extraction_path.is_file():
        return ApplyResult(
            status="error",
            slide=slide_number,
            message=f"Missing extraction JSON: {extraction_path.name}",
        )
    if not enrichment_path.is_file():
        return ApplyResult(
            status="error",
            slide=slide_number,
            message=f"Missing enrichment JSON: enrichment/{stem}.json",
        )
    if not pptx_path.is_file() or not png_path.is_file():
        return ApplyResult(
            status="error",
            slide=slide_number,
            message="Missing slide.pptx or preview.png in staging",
        )

    extraction = SlideExtraction.from_dict(read_json(extraction_path))
    enrichment = _load_enrichment(enrichment_path)

    # Work on copies so staging originals stay intact until success
    work_dir = staging_dir / "_work" / stem
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ensure_dir(work_dir)
    work_pptx = work_dir / "slide.pptx"
    work_png = work_dir / "preview.png"
    work_images = work_dir / "images"
    shutil.copy2(pptx_path, work_pptx)
    shutil.copy2(png_path, work_png)
    ensure_dir(work_images)
    if images_dir.is_dir():
        for img in images_dir.iterdir():
            if img.is_file():
                shutil.copy2(img, work_images / img.name)

    duplicate = None
    if not force and replace_id is None:
        duplicate = find_best_duplicate(
            extraction,
            library.slides_dir,
            preferred_type=enrichment.type,
            threshold=threshold,
        )
        if duplicate is not None:
            decision = {
                "status": "needs_decision",
                "slide": slide_number,
                "stem": stem,
                "suggested_type": enrichment.type,
                "duplicate": duplicate.to_dict(),
                "message": (
                    f"Slide semelhante a {duplicate.slide_id} "
                    f"({duplicate.similarity:.1%}). "
                    f"Reexecute com --replace {slide_number}={duplicate.slide_id} "
                    f"ou --skip {slide_number}."
                ),
            }
            write_json(staging_dir / "enrichment" / f"{stem}.decision.json", decision)
            return ApplyResult(
                status="needs_decision",
                slide=slide_number,
                slide_id=duplicate.slide_id,
                message=decision["message"],
                duplicate=duplicate,
            )

    apply_placeholders(work_pptx, enrichment.placeholders)
    image_names = rename_images(work_images, enrichment.image_labels)
    texts = collect_texts_after_placeholders(work_pptx)

    if replace_id:
        slide_id = replace_id
        status = "replaced"
        library.delete_slide(replace_id)
    else:
        slide_id = library.next_id(enrichment.type)
        status = "created"

    metadata = build_metadata(
        slide_id=slide_id,
        enrichment=enrichment,
        extraction=extraction,
        texts=texts,
        image_names=[Path(n).stem for n in image_names],
    )

    library.save_slide(
        slide_id,
        pptx_src=work_pptx,
        preview_src=work_png,
        images_src=work_images,
        metadata=metadata,
        replace=False,
    )

    # Mark enrichment as applied
    write_json(
        staging_dir / "enrichment" / f"{stem}.applied.json",
        {"status": status, "slide_id": slide_id, "slide": slide_number},
    )

    return ApplyResult(
        status=status,
        slide=slide_number,
        slide_id=slide_id,
        message=f"{status}: {slide_id}",
        duplicate=duplicate,
    )


def apply_enrichment(
    staging_dir: Path,
    library_root: Path,
    *,
    replace: dict[int, str] | None = None,
    skip_slides: set[int] | None = None,
    force: bool = False,
    keep_staging: bool = True,
) -> list[ApplyResult]:
    """
    Apply all enrichment JSON files found in staging_dir/enrichment/.

    replace: map slide_number -> existing slide_id to replace
    skip_slides: slide numbers to ignore
    """
    staging_dir = resolve_path(staging_dir)
    library_root = resolve_path(library_root)
    replace = replace or {}
    skip_slides = skip_slides or set()

    library = LibraryManager(library_root)
    manifest_path = staging_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = read_json(manifest_path)
        slide_numbers = [int(s["slide"]) for s in manifest.get("slides", [])]
    else:
        slide_numbers = []
        for path in sorted(staging_dir.glob("slide_*.json")):
            if path.name.endswith(".decision.json") or ".applied." in path.name:
                continue
            data = read_json(path)
            slide_numbers.append(int(data["slide"]))

    results: list[ApplyResult] = []
    for num in slide_numbers:
        result = apply_one_slide(
            staging_dir,
            num,
            library,
            replace_id=replace.get(num),
            skip=num in skip_slides,
            force=force,
        )
        results.append(result)
        logger.info("Slide %d -> %s", num, result.status)

    report = {
        "staging": str(staging_dir),
        "library": str(library_root),
        "results": [r.to_dict() for r in results],
        "needs_decision": [
            r.to_dict() for r in results if r.status == "needs_decision"
        ],
        "created": [r.slide_id for r in results if r.status == "created"],
        "replaced": [r.slide_id for r in results if r.status == "replaced"],
        "skipped": [r.slide for r in results if r.status == "skipped"],
        "errors": [r.to_dict() for r in results if r.status == "error"],
    }
    write_json(staging_dir / "apply_report.json", report)

    if not keep_staging:
        # Only remove work copies; keep enrichment for audit unless fully clean success
        work = staging_dir / "_work"
        if work.exists():
            shutil.rmtree(work)

    return results
