"""POST /api/proposals/generate + GET /api/proposals/download/{token}.

Gera em um diretório temporário por requisição (isolamento entre gerações
concorrentes — o app Streamlit escrevia direto em data/geradas/ com nome
fixo por código de projeto, então duas pessoas gerando o mesmo código ao
mesmo tempo colidiam), devolve o binário via download efêmero em memória
(api/store.py) e descarta o diretório temporário ao final da requisição.
"""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from ..errors import GenerationError
from ..schemas import GenerateProposalResponse, ProposalMeta
from ..service import generate_proposal
from ..session import require_auth
from ..store import store

router = APIRouter()

PPTX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)


@router.post(
    "/proposals/generate",
    response_model=GenerateProposalResponse,
    dependencies=[Depends(require_auth)],
)
async def generate(
    type_id: str = Form(...),
    client_name: str = Form(""),
    project_code: str = Form(""),
    fields_json: str = Form("{}"),
    brief: str = Form(""),
    transcription: str = Form(""),
    estimate: str = Form(""),
    logo: UploadFile | None = File(None),
) -> GenerateProposalResponse:
    try:
        field_values = json.loads(fields_json) if fields_json else {}
        if not isinstance(field_values, dict):
            raise ValueError("fields_json deve ser um objeto JSON.")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="fields_json inválido.") from exc

    logo_bytes = await logo.read() if logo is not None else None
    logo_filename = logo.filename if logo is not None else None

    with tempfile.TemporaryDirectory(prefix="mosten-proposal-") as tmp:
        work_dir = Path(tmp)
        try:
            content, meta = generate_proposal(
                type_id=type_id,
                client_name=client_name,
                project_code=project_code,
                field_values=field_values,
                brief=brief,
                transcription=transcription,
                estimate=estimate,
                logo_bytes=logo_bytes,
                logo_filename=logo_filename,
                work_dir=work_dir,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail=f"Tipo de proposta desconhecido: {type_id}"
            ) from exc
        except GenerationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 — vira 500 com contexto para o front
            raise HTTPException(
                status_code=500, detail=f"Falha ao montar PPTX: {exc}"
            ) from exc

    token = store.put(filename=meta["filename"], content=content, meta=meta)
    return GenerateProposalResponse(token=token, meta=ProposalMeta(**meta))


@router.get("/proposals/download/{token}", dependencies=[Depends(require_auth)])
def download(token: str) -> StreamingResponse:
    item = store.get(token)
    if item is None:
        raise HTTPException(
            status_code=404, detail="Link de download expirado ou inválido."
        )
    return StreamingResponse(
        io.BytesIO(item.content),
        media_type=PPTX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{item.filename}"'},
    )
