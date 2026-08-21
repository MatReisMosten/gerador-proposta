"""Orquestração de geração de PPTX — versão framework-agnóstica de
`generation/flow.py` (aquele depende de Streamlit; este não depende de nada
além de `generator/`).

Dispatcher por `mode` do tipo de proposta:
- "package"     → campos estruturados, sem LLM (Professional Service, Suporte,
                  PassLog, Discovery, Clarion).
- "llm_package" → seção isolada do mestre + LLM só nos tokens dela
                  (Escopo Fechado / DP World).
- "llm_full"    → brief livre + LLM em todo o catálogo do mestre (Livre).

Nota sobre "llm_package": no app Streamlit (Fase 1), esse modo não tem
tratamento dedicado e cai no fluxo "llm_full", cujo `build_livre_deck` exclui
justamente a seção "Escopo Fechado (DP World)" da lista de seções livres —
ou seja, selecionar Escopo Fechado no app antigo gera um deck SEM a própria
seção. Aqui isolamos a seção do pacote antes de rodar o LLM, como o
PRODUCT.md descreve. Ver conversa/README para o achado — não corrigido no
app Streamlit para não mudar comportamento ali sem pedido explícito.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from generator import (
    build_livre_deck,
    build_package_deck,
    fill_slots,
    get_proposal_type,
    load_named_token_catalog,
)
from generator import paths as P
from generator.engine import apply_named_placeholders, keep_only_slides, replace_logo_cliente
from generator.packages import (
    build_field_values,
    resolve_package_slides,
    resolve_package_template,
)

from . import config
from .errors import GenerationError
from .formatting import human_size, is_valid_project_code, proposal_file_stem


def build_full_brief(brief: str, transcription: str, estimate: str) -> str:
    parts: list[str] = []
    if (brief or "").strip():
        parts.append(f"BRIEF:\n{brief.strip()}")
    if (transcription or "").strip():
        parts.append(f"TRANSCRIÇÃO DA REUNIÃO:\n{transcription.strip()}")
    if (estimate or "").strip():
        parts.append(f"ESTIMATIVA TÉCNICA:\n{estimate.strip()}")
    return "\n\n".join(parts)


def _load_example_values() -> dict[str, str] | None:
    path = P.example_values_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("vigia") or data.get("values")


def _resolve_logo_path(
    work_dir: Path,
    logo_bytes: bytes | None,
    logo_filename: str | None,
    client_name: str,
) -> Path | None:
    if logo_bytes:
        suffix = Path(logo_filename or "logo.png").suffix or ".png"
        path = work_dir / f"logo{suffix}"
        path.write_bytes(logo_bytes)
        return path
    default_logo = P.ASSETS / "logo-nph.png"
    if default_logo.is_file() and (
        not client_name
        or "nph" in client_name.lower()
        or "unisanta" in client_name.lower()
    ):
        return default_logo
    return None


def _generate_package(
    *,
    pkg: dict,
    field_values: dict[str, str],
    client_name: str,
    project_code: str,
    logo_path: Path | None,
    work_dir: Path,
) -> tuple[Path, dict[str, str]]:
    missing_req = [
        f.get("label") or f["id"]
        for f in (pkg.get("fields") or [])
        if f.get("required") and not (field_values.get(f["id"]) or "").strip()
    ]
    if missing_req:
        raise GenerationError(
            "Preencha os campos obrigatórios: " + ", ".join(missing_req)
        )

    stem = proposal_file_stem(project_code, pkg["id"])
    out_path = work_dir / f"{stem}.pptx"
    out_path, values = build_package_deck(
        pkg,
        field_values=field_values,
        output_path=out_path,
        client_name=client_name,
        project_code=project_code,
        logo_path=logo_path,
    )
    return out_path, values


def _generate_llm_package(
    *,
    pkg: dict,
    client_name: str,
    project_code: str,
    brief: str,
    transcription: str,
    estimate: str,
    logo_path: Path | None,
    work_dir: Path,
) -> tuple[Path, dict[str, str]]:
    if not config.OPENAI_API_KEY:
        raise GenerationError(
            "API Key OpenAI não configurada. Defina OPENAI_API_KEY no .env do servidor."
        )
    full_brief = build_full_brief(brief, transcription, estimate)
    if not full_brief.strip():
        raise GenerationError(
            "Preencha pelo menos um dos campos: brief, transcrição ou estimativa técnica."
        )

    src = resolve_package_template(pkg)
    stem = proposal_file_stem(project_code, pkg["id"])
    out_path = work_dir / f"{stem}.pptx"
    shutil.copy2(src, out_path)

    slides = resolve_package_slides(pkg, src)
    keep_only_slides(out_path, slides)

    catalog = load_named_token_catalog(out_path)
    if not catalog:
        raise GenerationError(
            "Nenhum token {NOME} encontrado na seção isolada do template."
        )

    values = fill_slots(
        provider=config.FIXED_LLM_PROVIDER,
        api_key=config.OPENAI_API_KEY,
        brief=full_brief,
        catalog=catalog,
        model=config.FIXED_LLM_MODEL,
        example_values=None,
        project_code=project_code,
        client_name=client_name,
        base_url=config.FIXED_LLM_BASE_URL,
    )

    # Código/data nunca vêm do LLM — sempre do formulário (nunca inventar).
    meta_values = build_field_values(
        pkg, field_values={}, client_name=client_name, project_code=project_code
    )
    values.update(meta_values)

    apply_named_placeholders(out_path, values)
    if logo_path:
        replace_logo_cliente(out_path, Path(logo_path))
    return out_path, values


def _generate_livre(
    *,
    client_name: str,
    project_code: str,
    brief: str,
    transcription: str,
    estimate: str,
    logo_path: Path | None,
    work_dir: Path,
) -> tuple[Path, dict[str, str]]:
    if not config.OPENAI_API_KEY:
        raise GenerationError(
            "API Key OpenAI não configurada. Defina OPENAI_API_KEY no .env do servidor."
        )
    full_brief = build_full_brief(brief, transcription, estimate)
    if not full_brief.strip():
        raise GenerationError(
            "Preencha pelo menos um dos campos: brief, transcrição ou estimativa técnica."
        )

    master = P.master_template_path()
    catalog = load_named_token_catalog(master)
    if not catalog:
        raise GenerationError("Nenhum token {NOME} encontrado no slide mestre.")

    values = fill_slots(
        provider=config.FIXED_LLM_PROVIDER,
        api_key=config.OPENAI_API_KEY,
        brief=full_brief,
        catalog=catalog,
        model=config.FIXED_LLM_MODEL,
        example_values=_load_example_values(),
        project_code=project_code,
        client_name=client_name,
        base_url=config.FIXED_LLM_BASE_URL,
    )

    stem = proposal_file_stem(project_code, "livre")
    out_path = work_dir / f"{stem}.pptx"
    build_livre_deck(
        values,
        output_path=out_path,
        logo_path=logo_path,
        client_name=client_name,
        project_code=project_code,
    )
    return out_path, values


def generate_proposal(
    *,
    type_id: str,
    client_name: str,
    project_code: str,
    field_values: dict[str, str],
    brief: str,
    transcription: str,
    estimate: str,
    logo_bytes: bytes | None,
    logo_filename: str | None,
    work_dir: Path,
) -> tuple[bytes, dict]:
    """Gera a proposta e devolve (bytes do pptx, metadados). Não persiste nada."""
    pkg = get_proposal_type(type_id)  # KeyError -> tratado no router como 404
    mode = pkg.get("mode") or "llm_full"
    label = pkg.get("label") or type_id
    hide_client = bool(pkg.get("hide_client"))
    hide_logo = bool(pkg.get("hide_logo"))

    project_code = (project_code or "").strip().upper()
    if type_id == "clarion":
        if not is_valid_project_code(project_code):
            project_code = "CLA000-00"
    elif not is_valid_project_code(project_code):
        raise GenerationError(
            "Código da proposta inválido. Use AAA999-99 (ex.: BUI001-26)."
        )

    client_name = "" if hide_client else (client_name or "").strip()
    logo_path = None
    if not hide_logo:
        logo_path = _resolve_logo_path(work_dir, logo_bytes, logo_filename, client_name)

    if mode == "package":
        out_path, values = _generate_package(
            pkg=pkg,
            field_values=field_values,
            client_name=client_name,
            project_code=project_code,
            logo_path=logo_path,
            work_dir=work_dir,
        )
    elif mode == "llm_package":
        out_path, values = _generate_llm_package(
            pkg=pkg,
            client_name=client_name,
            project_code=project_code,
            brief=brief,
            transcription=transcription,
            estimate=estimate,
            logo_path=logo_path,
            work_dir=work_dir,
        )
    else:
        out_path, values = _generate_livre(
            client_name=client_name,
            project_code=project_code,
            brief=brief,
            transcription=transcription,
            estimate=estimate,
            logo_path=logo_path,
            work_dir=work_dir,
        )

    if not logo_path:
        # Sem logo resolvido (não enviado / hide_logo / cliente sem logo
        # padrão): limpa o marcador em vez de deixar "{LOGO_CLIENTE}"
        # literal no slide exportado. `apply_named_placeholders` já suporta
        # isso via force=True — só não era chamado como fallback em nenhum
        # caminho do app Streamlit (Fase 1 tem o mesmo vazamento).
        apply_named_placeholders(
            out_path, {"{LOGO_CLIENTE}": "", "{Logo_Cliente}": ""}, force=True
        )

    content = out_path.read_bytes()
    empty_tokens = sum(
        1 for v in values.values() if isinstance(v, str) and not v.strip()
    )
    meta = {
        "client": client_name,
        "code": project_code,
        "type": type_id,
        "type_label": label,
        "size_label": human_size(len(content)),
        "filename": out_path.name,
        "empty_tokens": empty_tokens,
    }
    return content, meta
