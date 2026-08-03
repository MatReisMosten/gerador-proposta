"""Typed dataclasses for extraction, enrichment, and library metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ShapeInfo:
    name: str
    type: str
    x: float
    y: float
    w: float
    h: float
    text: str = ""
    font_size: float | None = None
    font_name: str | None = None
    color: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SlideExtraction:
    slide: int
    title: str
    texts: list[str]
    font_sizes: list[float]
    fonts: list[str]
    colors: list[str]
    shapes: list[dict[str, Any]]
    images: list[str]
    notes: str
    layout: str
    element_count: int
    structure_hash: str
    visual_hash: str = ""
    source_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SlideExtraction:
        return cls(
            slide=int(data["slide"]),
            title=data.get("title", ""),
            texts=list(data.get("texts", [])),
            font_sizes=[float(x) for x in data.get("font_sizes", [])],
            fonts=list(data.get("fonts", [])),
            colors=list(data.get("colors", [])),
            shapes=list(data.get("shapes", [])),
            images=list(data.get("images", [])),
            notes=data.get("notes", ""),
            layout=data.get("layout", "16:9"),
            element_count=int(data.get("element_count", 0)),
            structure_hash=data.get("structure_hash", ""),
            visual_hash=data.get("visual_hash", ""),
            source_file=data.get("source_file", ""),
        )


@dataclass
class PlaceholderMapping:
    original: str
    placeholder: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class SlideEnrichment:
    type: str
    purpose: str = ""
    industry: str = ""
    tags: list[str] = field(default_factory=list)
    image_labels: dict[str, str] = field(default_factory=dict)
    placeholders: list[PlaceholderMapping] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "purpose": self.purpose,
            "industry": self.industry,
            "tags": self.tags,
            "image_labels": self.image_labels,
            "placeholders": [p.to_dict() for p in self.placeholders],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SlideEnrichment:
        placeholders = [
            PlaceholderMapping(
                original=p["original"],
                placeholder=p["placeholder"],
            )
            for p in data.get("placeholders", [])
        ]
        return cls(
            type=data["type"],
            purpose=data.get("purpose", ""),
            industry=data.get("industry", ""),
            tags=list(data.get("tags", [])),
            image_labels=dict(data.get("image_labels", {})),
            placeholders=placeholders,
        )


@dataclass
class SlideMetadata:
    id: str
    type: str
    purpose: str
    industry: str
    tags: list[str]
    texts: list[str]
    placeholders: list[str]
    images: list[str]
    ppt: str = "slide.pptx"
    preview: str = "preview.png"
    structure_hash: str = ""
    visual_hash: str = ""
    source_file: str = ""
    source_slide: int = 0
    original_texts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SlideMetadata:
        return cls(
            id=data["id"],
            type=data["type"],
            purpose=data.get("purpose", ""),
            industry=data.get("industry", ""),
            tags=list(data.get("tags", [])),
            texts=list(data.get("texts", [])),
            placeholders=list(data.get("placeholders", [])),
            images=list(data.get("images", [])),
            ppt=data.get("ppt", "slide.pptx"),
            preview=data.get("preview", "preview.png"),
            structure_hash=data.get("structure_hash", ""),
            visual_hash=data.get("visual_hash", ""),
            source_file=data.get("source_file", ""),
            source_slide=int(data.get("source_slide", 0)),
            original_texts=list(data.get("original_texts", [])),
        )


@dataclass
class DuplicateMatch:
    slide_id: str
    similarity: float
    structure_score: float
    text_score: float
    visual_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApplyResult:
    status: str  # created | replaced | skipped | needs_decision | error
    slide: int
    slide_id: str | None = None
    message: str = ""
    duplicate: DuplicateMatch | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "slide": self.slide,
            "slide_id": self.slide_id,
            "message": self.message,
        }
        if self.duplicate is not None:
            payload["duplicate"] = self.duplicate.to_dict()
        return payload
