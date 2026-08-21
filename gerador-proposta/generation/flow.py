"""Orquestração da geração de PPTX: uploads, brief, execução e download."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from generator import (
    build_livre_deck,
    build_package_deck,
    fill_slots,
    load_named_token_catalog,
)
from generator import paths as P
from generator.text_extract import TextExtractError, extract_text_from_bytes

from ui.components import FullscreenLoading, _result_success_html
from ui.formatting import _build_output_path, _human_size


def load_example_values() -> dict[str, str] | None:
    path = P.example_values_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("vigia") or data.get("values")


def _file_fingerprint(uploaded) -> str | None:
    if uploaded is None:
        return None
    return f"{uploaded.name}:{uploaded.size}"


def _apply_upload_to_field(
    *,
    uploaded,
    text_key: str,
    fingerprint_key: str,
    label: str,
    max_chars: int | None = None,
) -> None:
    """Extrai texto do upload e atualiza o session_state do textarea."""
    fp = _file_fingerprint(uploaded)
    if uploaded is None:
        st.session_state[fingerprint_key] = None
        return
    if fp == st.session_state.get(fingerprint_key):
        return
    try:
        extracted = extract_text_from_bytes(uploaded.getvalue(), uploaded.name)
    except TextExtractError as exc:
        st.warning(f"{label}: {exc}")
        return
    if max_chars is not None and len(extracted) > max_chars:
        extracted = extracted[:max_chars]
        st.warning(
            f"{label}: texto truncado para {max_chars} caracteres "
            f"(limite do campo)."
        )
    st.session_state[text_key] = extracted
    st.session_state[fingerprint_key] = fp
    st.toast(f"{label}: texto extraído de {uploaded.name}")


def _build_full_brief(
    brief: str,
    transcription: str,
    estimate: str,
) -> str:
    parts: list[str] = []
    if brief.strip():
        parts.append(f"BRIEF:\n{brief.strip()}")
    if transcription.strip():
        parts.append(f"TRANSCRIÇÃO DA REUNIÃO:\n{transcription.strip()}")
    if estimate.strip():
        parts.append(f"ESTIMATIVA TÉCNICA:\n{estimate.strip()}")
    if st.session_state.messages:
        parts.append(
            "Complementos:\n"
            + "\n".join(f"- {m}" for m in st.session_state.messages)
        )
    return "\n\n".join(parts)


def _resolve_logo_path(logo_file, client_name: str) -> Path | None:
    if logo_file is not None:
        tmp_logo = tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(logo_file.name).suffix
        )
        tmp_logo.write(logo_file.getvalue())
        tmp_logo.close()
        return Path(tmp_logo.name)
    default_logo = P.ASSETS / "logo-nph.png"
    if default_logo.is_file() and (
        not client_name
        or "nph" in client_name.lower()
        or "unisanta" in client_name.lower()
    ):
        return default_logo
    return None


def _persist_values_json(out_path: Path, values: dict, meta: dict | None) -> None:
    payload = {
        "client": (meta or {}).get("client"),
        "code": (meta or {}).get("code"),
        "type": (meta or {}).get("type"),
        "template": (meta or {}).get("template"),
        "provider": (meta or {}).get("provider"),
        "model": (meta or {}).get("model"),
        "values": values,
    }
    values_path = out_path.with_suffix(".values.json")
    values_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _show_download(
    *,
    result_box,
    download_box,
    out_path: Path,
    values: dict,
    meta: dict | None = None,
) -> None:
    meta = meta or {}
    type_label = meta.get("type_label") or meta.get("type") or "—"
    size_label = _human_size(out_path.stat().st_size)
    payload_bytes = out_path.read_bytes()

    st.session_state.last_result = {
        "file_name": out_path.name,
        "path": str(out_path),
        "client": meta.get("client") or "",
        "code": meta.get("code") or "",
        "type": meta.get("type"),
        "type_label": type_label,
        "template": meta.get("template"),
        "size_label": size_label,
        "values": values,
    }

    result_box.markdown(
        _result_success_html(
            file_name=out_path.name,
            client=str(meta.get("client") or ""),
            code=str(meta.get("code") or ""),
            type_label=str(type_label),
            size_label=size_label,
        ),
        unsafe_allow_html=True,
    )
    with download_box.container():
        st.download_button(
            label="Baixar PPTX",
            data=payload_bytes,
            file_name=out_path.name,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            use_container_width=True,
            icon=":material/download:",
            key="download_result_card",
        )

    _persist_values_json(out_path, values, meta)
    _proposal_ready_dialog()


@st.dialog("Proposta gerada", width="large")
def _proposal_ready_dialog() -> None:
    data = st.session_state.get("last_result") or {}
    out_name = data.get("file_name") or "proposta.pptx"
    st.markdown(
        f"**Arquivo:** `{out_name}`  \n"
        f"**Cliente:** {data.get('client') or '—'}  \n"
        f"**Código:** {data.get('code') or '—'}  \n"
        f"**Tipo:** {data.get('type_label') or '—'}  \n"
        f"**Tamanho:** {data.get('size_label') or '—'}"
    )
    path_str = data.get("path") or ""
    path = Path(path_str) if path_str else None
    if path and path.is_file():
        st.download_button(
            label="Baixar PPTX",
            data=path.read_bytes(),
            file_name=out_name,
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            use_container_width=True,
            type="primary",
            icon=":material/download:",
            key="download_modal_pptx",
        )
    if data.get("template"):
        st.caption(f"Template: `{Path(str(data['template'])).name}`")


def _run_package_generation(
    *,
    pkg: dict,
    label: str,
    field_values: dict[str, str],
    master_path: Path,
    client_name: str,
    project_code: str,
    logo_file,
    result_box,
    download_box,
) -> None:
    missing_req = [
        f.get("label") or f["id"]
        for f in (pkg.get("fields") or [])
        if f.get("required") and not (field_values.get(f["id"]) or "").strip()
    ]
    if missing_req:
        result_box.error(
            "Preencha os campos obrigatórios: " + ", ".join(missing_req)
        )
        return

    logo_path = _resolve_logo_path(logo_file, client_name)
    out_path = _build_output_path(
        project_code=project_code,
        type_id=str(pkg.get("id") or "pacote"),
    )
    loading = FullscreenLoading(title=f"Gerando {label}")
    loading.update(5, "Iniciando geração…")
    try:
        out_path, values = build_package_deck(
            pkg,
            field_values=field_values,
            output_path=out_path,
            client_name=client_name.strip(),
            project_code=project_code.strip(),
            logo_path=logo_path,
            on_progress=loading.update,
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao montar PPTX: {exc}")
        return

    loading.update(100, "Proposta pronta!")
    loading.close()
    _show_download(
        result_box=result_box,
        download_box=download_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": pkg.get("id"),
            "type_label": label,
            "template": str(master_path),
            "section_slides": values.get("_section_slides", ""),
        },
    )


def _run_livre_generation(
    *,
    brief: str,
    transcription: str,
    estimate: str,
    provider: str,
    api_key: str,
    model: str,
    base_url: str | None,
    client_name: str,
    project_code: str,
    logo_file,
    result_box,
    download_box,
) -> None:
    if not api_key.strip():
        result_box.error(
            "API Key OpenAI não configurada. Defina OPENAI_API_KEY no arquivo .env."
        )
        return

    full_brief = _build_full_brief(brief, transcription, estimate)
    if not full_brief.strip():
        result_box.error(
            "Preencha pelo menos um dos campos: "
            "brief, transcrição ou estimativa técnica."
        )
        return

    loading = FullscreenLoading(title="Gerando proposta Livre")
    loading.update(8, "Escaneando tokens {NOME} do slide mestre…")
    try:
        master = P.master_template_path()
        catalog = load_named_token_catalog(master)
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao carregar slide mestre: {exc}")
        return

    if not catalog:
        loading.close()
        result_box.error(
            "Nenhum token {NOME} encontrado no slide mestre. "
            "Adicione placeholders no PPTX e tente de novo."
        )
        return

    loading.update(28, f"Enviando brief ao LLM ({len(catalog)} tokens)…")
    try:
        values = fill_slots(
            provider=provider,
            api_key=api_key.strip(),
            brief=full_brief,
            catalog=catalog,
            model=model.strip(),
            example_values=load_example_values(),
            project_code=project_code.strip(),
            client_name=client_name.strip(),
            base_url=base_url,
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha na chamada ao LLM: {exc}")
        return

    loading.update(72, "Textos recebidos. Montando PPTX…")

    empty = [k for k, v in values.items() if not str(v).strip()]
    if empty:
        result_box.info(
            f"{len(empty)} token(s) sem conteúdo (ficarão vazios no slide) — "
            "normal quando o brief não traz cronograma/premissas."
        )

    logo_path = _resolve_logo_path(logo_file, client_name)
    out_path = _build_output_path(
        project_code=project_code,
        type_id="livre",
    )

    loading.update(88, "Substituindo apenas {TOKENS} no mestre…")
    try:
        build_livre_deck(
            values,
            output_path=out_path,
            logo_path=logo_path,
            client_name=client_name.strip(),
            project_code=project_code.strip(),
        )
    except Exception as exc:
        loading.close()
        result_box.error(f"Falha ao montar PPTX: {exc}")
        return

    loading.update(100, "Proposta pronta!")
    loading.close()
    _show_download(
        result_box=result_box,
        download_box=download_box,
        out_path=out_path,
        values=values,
        meta={
            "client": client_name,
            "code": project_code,
            "type": "livre",
            "type_label": "Livre",
            "template": str(master),
            "provider": provider,
            "model": model,
            "tokens": len(catalog),
        },
    )
