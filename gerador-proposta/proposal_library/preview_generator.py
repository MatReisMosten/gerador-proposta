"""Generate PNG previews from PPTX via LibreOffice (soffice)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from .utils import ensure_dir, sha256_text

logger = logging.getLogger(__name__)


class PreviewError(RuntimeError):
    """Raised when preview generation fails."""


def find_soffice() -> Path | None:
    env = os.environ.get("SOFFICE_PATH") or os.environ.get("LIBREOFFICE_PATH")
    if env:
        path = Path(env).expanduser()
        if path.is_file():
            return path

    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found)

    mac_path = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if mac_path.is_file():
        return mac_path

    return None


def average_hash(image_path: Path, hash_size: int = 8) -> str:
    """Compute a simple average perceptual hash as hex string."""
    with Image.open(image_path) as img:
        gray = img.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if px >= avg else "0" for px in pixels)
    return f"{int(bits, 2):0{hash_size * hash_size // 4}x}"


def hamming_similarity(hash_a: str, hash_b: str) -> float:
    if not hash_a or not hash_b:
        return 0.0
    # Compare as binary bitstrings of equal padded length
    max_len = max(len(hash_a), len(hash_b))
    a = int(hash_a, 16)
    b = int(hash_b, 16)
    bits = max_len * 4
    xor = a ^ b
    distance = bin(xor).count("1")
    return 1.0 - (distance / bits)


def generate_preview(pptx_path: Path, png_path: Path) -> str:
    """
    Convert PPTX to PNG using LibreOffice headless mode.

    Returns visual_hash of the generated PNG.
    Raises PreviewError if LibreOffice is missing or conversion fails.
    """
    soffice = find_soffice()
    if soffice is None:
        raise PreviewError(
            "LibreOffice (soffice) não encontrado. Instale o LibreOffice ou defina "
            "SOFFICE_PATH apontando para o binário soffice. Preview PNG é obrigatório."
        )

    ensure_dir(png_path.parent)
    pptx_path = pptx_path.resolve()

    with tempfile.TemporaryDirectory(prefix="plb_preview_") as tmp:
        tmp_dir = Path(tmp)
        cmd = [
            str(soffice),
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--norestore",
            "--convert-to",
            "png",
            "--outdir",
            str(tmp_dir),
            str(pptx_path),
        ]
        logger.info("Generating preview: %s", pptx_path.name)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PreviewError(f"Timeout ao gerar preview de {pptx_path.name}") from exc

        if result.returncode != 0:
            stderr = (result.stderr or result.stdout or "").strip()
            raise PreviewError(
                f"Falha ao converter {pptx_path.name} para PNG "
                f"(exit {result.returncode}): {stderr[:500]}"
            )

        produced = sorted(tmp_dir.glob("*.png"))
        if not produced:
            raise PreviewError(
                f"LibreOffice não gerou PNG para {pptx_path.name}. "
                f"stdout={result.stdout[:200]!r}"
            )

        # Single-slide decks produce one PNG; multi-page unlikely but take first.
        shutil.copy2(produced[0], png_path)

    visual = average_hash(png_path)
    logger.debug("Preview ready %s hash=%s", png_path.name, visual)
    return visual


def visual_hash_from_file(png_path: Path) -> str:
    if not png_path.is_file():
        return ""
    try:
        return average_hash(png_path)
    except Exception as exc:
        logger.warning("Could not hash preview %s: %s", png_path, exc)
        return sha256_text(str(png_path))
