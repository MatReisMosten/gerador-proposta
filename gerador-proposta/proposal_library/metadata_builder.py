"""Build final metadata.json for a library slide entry."""

from __future__ import annotations

from .models import SlideEnrichment, SlideExtraction, SlideMetadata


def build_metadata(
    *,
    slide_id: str,
    enrichment: SlideEnrichment,
    extraction: SlideExtraction,
    texts: list[str],
    image_names: list[str],
) -> SlideMetadata:
    placeholders = [p.placeholder for p in enrichment.placeholders]
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_placeholders: list[str] = []
    for ph in placeholders:
        if ph not in seen:
            seen.add(ph)
            unique_placeholders.append(ph)

    return SlideMetadata(
        id=slide_id,
        type=enrichment.type,
        purpose=enrichment.purpose,
        industry=enrichment.industry,
        tags=list(enrichment.tags),
        texts=texts,
        placeholders=unique_placeholders,
        images=image_names,
        ppt="slide.pptx",
        preview="preview.png",
        structure_hash=extraction.structure_hash,
        visual_hash=extraction.visual_hash,
        source_file=extraction.source_file,
        source_slide=extraction.slide,
        original_texts=list(extraction.texts),
    )
