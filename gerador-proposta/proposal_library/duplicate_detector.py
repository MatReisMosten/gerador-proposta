"""Detect near-duplicate slides in the library."""

from __future__ import annotations

import logging
from pathlib import Path

from . import DUPLICATE_THRESHOLD
from .models import DuplicateMatch, SlideExtraction, SlideMetadata
from .preview_generator import hamming_similarity
from .utils import normalize_text, read_json

logger = logging.getLogger(__name__)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _text_set(texts: list[str]) -> set[str]:
    return {normalize_text(t) for t in texts if normalize_text(t)}


def structure_similarity(hash_a: str, hash_b: str) -> float:
    if not hash_a or not hash_b:
        return 0.0
    return 1.0 if hash_a == hash_b else 0.0


def compare_extractions(
    candidate: SlideExtraction,
    existing: SlideMetadata,
) -> DuplicateMatch:
    struct = structure_similarity(candidate.structure_hash, existing.structure_hash)
    existing_texts = existing.original_texts or existing.texts
    text = _jaccard(_text_set(candidate.texts), _text_set(existing_texts))
    visual = hamming_similarity(candidate.visual_hash, existing.visual_hash)

    # Weighted composite: structure exact match is strong signal.
    similarity = (0.35 * struct) + (0.40 * text) + (0.25 * visual)
    # Exact structure + high text should push over threshold even with weak visual
    if struct == 1.0 and text >= 0.85:
        similarity = max(similarity, 0.92)
    if struct == 1.0 and text >= 0.99:
        similarity = max(similarity, 0.95)
    if text >= 0.95 and visual >= 0.90:
        similarity = max(similarity, 0.93)

    return DuplicateMatch(
        slide_id=existing.id,
        similarity=round(similarity, 4),
        structure_score=round(struct, 4),
        text_score=round(text, 4),
        visual_score=round(visual, 4),
    )


def find_best_duplicate(
    candidate: SlideExtraction,
    library_slides_dir: Path,
    *,
    preferred_type: str | None = None,
    threshold: float = DUPLICATE_THRESHOLD,
) -> DuplicateMatch | None:
    """
    Scan library metadata and return the best match above threshold, or None.
    Prefers same category first, then falls back to all slides.
    """
    if not library_slides_dir.is_dir():
        return None

    metas: list[SlideMetadata] = []
    for meta_path in sorted(library_slides_dir.glob("*/metadata.json")):
        try:
            data = read_json(meta_path)
            metas.append(SlideMetadata.from_dict(data))
        except Exception as exc:
            logger.warning("Skipping bad metadata %s: %s", meta_path, exc)

    if not metas:
        return None

    same_type = [m for m in metas if preferred_type and m.type == preferred_type]
    search_order = (same_type or []) + [m for m in metas if m not in (same_type or [])]

    best: DuplicateMatch | None = None
    for meta in search_order:
        # Enrich existing texts from metadata if available
        match = compare_extractions(candidate, meta)
        if best is None or match.similarity > best.similarity:
            best = match

    if best is None or best.similarity < threshold:
        return None
    return best
