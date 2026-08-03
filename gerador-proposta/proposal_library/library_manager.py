"""Manage library/index.json and allocate slide IDs."""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

from . import CATEGORIES
from .models import SlideMetadata
from .utils import ensure_dir, read_json, write_json

logger = logging.getLogger(__name__)

_ID_RE = re.compile(r"^([a-z]+)_(\d{3})$")


class LibraryManager:
    def __init__(self, library_root: Path) -> None:
        self.root = library_root
        self.slides_dir = library_root / "slides"
        self.index_path = library_root / "index.json"
        ensure_dir(self.slides_dir)
        if not self.index_path.exists():
            write_json(self.index_path, [])

    def load_index(self) -> list[dict]:
        data = read_json(self.index_path)
        if not isinstance(data, list):
            raise ValueError(f"Invalid index.json: expected list at {self.index_path}")
        return data

    def save_index(self, entries: list[dict]) -> None:
        # Stable sort by id
        entries = sorted(entries, key=lambda e: e.get("id", ""))
        write_json(self.index_path, entries)

    def list_ids(self) -> list[str]:
        ids = {e.get("id") for e in self.load_index() if e.get("id")}
        for path in self.slides_dir.iterdir() if self.slides_dir.exists() else []:
            if path.is_dir() and _ID_RE.match(path.name):
                ids.add(path.name)
        return sorted(x for x in ids if x)

    def next_id(self, category: str) -> str:
        if category not in CATEGORIES:
            category = "custom"
        prefix = category
        max_n = 0
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d{{3}})$")
        for slide_id in self.list_ids():
            m = pattern.match(slide_id)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"{prefix}_{max_n + 1:03d}"

    def slide_dir(self, slide_id: str) -> Path:
        return self.slides_dir / slide_id

    def load_metadata(self, slide_id: str) -> SlideMetadata | None:
        path = self.slide_dir(slide_id) / "metadata.json"
        if not path.is_file():
            return None
        return SlideMetadata.from_dict(read_json(path))

    def upsert_index_entry(self, meta: SlideMetadata) -> None:
        entries = self.load_index()
        entry = {
            "id": meta.id,
            "category": meta.type,
            "tags": meta.tags,
        }
        if meta.purpose:
            entry["purpose"] = meta.purpose
        if meta.industry:
            entry["industry"] = meta.industry

        replaced = False
        for i, existing in enumerate(entries):
            if existing.get("id") == meta.id:
                entries[i] = entry
                replaced = True
                break
        if not replaced:
            entries.append(entry)
        self.save_index(entries)

    def remove_index_entry(self, slide_id: str) -> None:
        entries = [e for e in self.load_index() if e.get("id") != slide_id]
        self.save_index(entries)

    def save_slide(
        self,
        slide_id: str,
        *,
        pptx_src: Path,
        preview_src: Path,
        images_src: Path | None,
        metadata: SlideMetadata,
        replace: bool = False,
    ) -> Path:
        dest = self.slide_dir(slide_id)
        if dest.exists():
            if not replace:
                raise FileExistsError(f"Slide already exists: {slide_id}")
            shutil.rmtree(dest)

        ensure_dir(dest)
        shutil.copy2(pptx_src, dest / "slide.pptx")
        shutil.copy2(preview_src, dest / "preview.png")

        images_dest = dest / "images"
        ensure_dir(images_dest)
        if images_src and images_src.is_dir():
            for img in images_src.iterdir():
                if img.is_file():
                    shutil.copy2(img, images_dest / img.name)

        write_json(dest / "metadata.json", metadata.to_dict())
        self.upsert_index_entry(metadata)
        logger.info("Saved library slide %s", slide_id)
        return dest

    def delete_slide(self, slide_id: str) -> None:
        dest = self.slide_dir(slide_id)
        if dest.exists():
            shutil.rmtree(dest)
        self.remove_index_entry(slide_id)
        logger.info("Deleted library slide %s", slide_id)
