"""Extrai texto de anexos (txt/md/vtt/srt/pdf) para os blocos do formulário."""

from __future__ import annotations

from io import BytesIO


class TextExtractError(Exception):
    """Falha ao ler ou extrair texto de um anexo."""


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Retorna o texto extraído do arquivo. Levanta TextExtractError em falha."""
    name = (filename or "").lower()
    suffix = name.rsplit(".", 1)[-1] if "." in name else ""

    if suffix in {"txt", "md", "vtt", "srt"}:
        return _decode_plain(data)

    if suffix == "pdf":
        return _extract_pdf(data)

    raise TextExtractError(
        f"Tipo de arquivo não suportado: .{suffix or '?'}. "
        "Use txt, md, vtt, srt ou pdf."
    )


def _decode_plain(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = data.decode(encoding)
            if text.strip():
                return text
            raise TextExtractError("Arquivo de texto está vazio.")
        except UnicodeDecodeError:
            continue
    raise TextExtractError("Não foi possível decodificar o arquivo de texto.")


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise TextExtractError(
            "Pacote pypdf não instalado. Rode: pip install pypdf"
        ) from exc

    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise TextExtractError(f"PDF inválido ou corrompido: {exc}") from exc

    parts: list[str] = []
    for page in reader.pages:
        try:
            chunk = page.extract_text() or ""
        except Exception:
            chunk = ""
        if chunk.strip():
            parts.append(chunk.strip())

    text = "\n\n".join(parts).strip()
    if not text:
        raise TextExtractError(
            "Não foi possível extrair texto deste PDF "
            "(pode ser imagem/escaneado sem OCR)."
        )
    return text
