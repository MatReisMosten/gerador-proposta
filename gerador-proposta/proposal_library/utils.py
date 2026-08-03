"""Shared helpers: logging, paths, hashing, JSON I/O."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("proposal_library")


def resolve_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any, *, indent: int = 2) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=indent)
        fh.write("\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\x0b", "\n")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def slide_stem(slide_number: int) -> str:
    return f"slide_{slide_number:03d}"


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def safe_rmtree(path: Path) -> None:
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def find_vault_root(start: Path | None = None) -> Path:
    """Walk up from start (or this file) looking for Obsidian vault markers."""
    cur = (start or Path(__file__).resolve()).parent
    for candidate in [cur, *cur.parents]:
        if (candidate / ".obsidian").is_dir() or (candidate / ".agents").is_dir():
            return candidate
    return Path.cwd()
