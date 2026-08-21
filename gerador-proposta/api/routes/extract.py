"""POST /api/extract-text — extrai texto de anexo (brief/transcrição/estimativa).

Equivalente a `_apply_upload_to_field` do Streamlit: o front chama isso ao
soltar um arquivo no dropzone e usa o texto retornado para pré-popular o
textarea (o usuário ainda revisa/edita antes de gerar)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from generator.text_extract import TextExtractError, extract_text_from_bytes

from .. import config
from ..schemas import ExtractTextResponse
from ..session import require_auth

router = APIRouter()


@router.post(
    "/extract-text",
    response_model=ExtractTextResponse,
    dependencies=[Depends(require_auth)],
)
async def extract_text(file: UploadFile = File(...)) -> ExtractTextResponse:
    data = await file.read()
    try:
        text = extract_text_from_bytes(data, file.filename or "")
    except TextExtractError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    truncated = False
    if len(text) > config.BRIEF_MAX_CHARS:
        text = text[: config.BRIEF_MAX_CHARS]
        truncated = True
    return ExtractTextResponse(text=text, truncated=truncated)
