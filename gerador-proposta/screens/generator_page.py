"""Página do gerador: wizard Tipo → Informações → Gerar."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from generator import list_proposal_types
from generator import paths as P

from generation.flow import (
    _apply_upload_to_field,
    _proposal_ready_dialog,
    _run_livre_generation,
    _run_package_generation,
)
from ui.components import (
    _card_head,
    _footer_note,
    _page_header,
    _render_wizard_stepper,
    _result_empty_state,
    _result_success_html,
    _type_label,
    _wizard_nav,
)
from ui.formatting import (
    _is_valid_project_code,
    _on_money_field_change,
    _on_months_field_change,
    _on_project_code_change,
    _proposal_file_stem,
)
from ui.icons import ICON_BRIEF, ICON_INFO, ICON_RESULT


def _init_session_defaults() -> None:
    defaults = {
        "messages": [],
        "brief_text": "",
        "transcription_text": "",
        "estimate_text": "",
        "theme_mode": "Claro",
        "page": "gerador",
        "wizard_step": 1,
        "wizard_max": 1,
        "tipo_collapsed": False,
        "selected_proposal_type": "professional_service",
        "last_result": None,
        "open_result_modal": False,
        "_transcription_file_id": None,
        "_estimate_file_id": None,
        "_brief_file_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _on_tipo_selected() -> None:
    chosen = st.session_state.get("proposal_type_id")
    if chosen:
        st.session_state.selected_proposal_type = chosen


def _skips_info_step(type_id: str | None) -> bool:
    """Clarion is a static deck — no client/fields form."""
    return (type_id or "") == "clarion"


def _uses_brief_field(type_id: str | None) -> bool:
    """Tipos que mostram Brief/contexto (com anexo MD/TXT)."""
    return (type_id or "") in {"livre", "discovery", "passlog"}


def _render_brief_context_field() -> str:
    """Campo Brief/contexto com upload MD/TXT e preview editável."""
    from app import BRIEF_MAX_CHARS

    with st.container(border=True, key="sub_brief"):
        _card_head(
            "Brief / contexto",
            "Resumo da proposta, objetivos e contexto comercial.",
            icon_svg=ICON_BRIEF,
        )
        brief_file = st.file_uploader(
            "Anexar brief (MD/TXT)",
            type=["txt", "md"],
            key="brief_uploader",
            help="O texto do arquivo preenche o campo abaixo para revisão.",
        )
        _apply_upload_to_field(
            uploaded=brief_file,
            text_key="brief_text",
            fingerprint_key="_brief_file_id",
            label="Brief",
            max_chars=BRIEF_MAX_CHARS,
        )
        if brief_file is not None:
            st.caption(f"Anexo: **{brief_file.name}** — revise o texto abaixo.")
        return st.text_area(
            "Brief",
            height=185,
            max_chars=BRIEF_MAX_CHARS,
            key="brief_text",
            label_visibility="collapsed",
            placeholder=(
                "Exemplo:\n"
                "Cliente: NPH/Unisanta\n"
                "Contexto: operação cresceu; mais pessoas, sistemas "
                "e decisões no dia a dia\n"
                "Fricções: informação dispersa; decisões demoram; "
                "dependência de poucas pessoas\n"
                "Impacto: reação tardia, custo sobe, previsibilidade cai\n"
                "Transformação desejada: operação conectada, visível "
                "e pronta para crescer\n"
                "Escopo/integrações (opcional): sistemas atuais, "
                "APIs, restrições\n"
                "Prazo/preço (se houver): a definir"
            ),
        )


def render_generator() -> None:
    from app import (
        FIXED_LLM_BASE_URL,
        FIXED_LLM_MODEL,
        FIXED_LLM_PROVIDER,
        OPENAI_API_KEY,
    )

    _page_header(
        "Gerador de Propostas",
        "Monte propostas comerciais Mosten a partir do template oficial.",
    )

    if st.session_state.pop("open_result_modal", False) and st.session_state.get(
        "last_result"
    ):
        _proposal_ready_dialog()

    proposal_types = list_proposal_types()
    ordered = sorted(
        proposal_types,
        key=lambda t: (0 if t.get("mode") == "package" else 1, t.get("label") or ""),
    )
    type_ids = [t["id"] for t in ordered]
    label_by_id = {t["id"]: (t.get("label") or t["id"]) for t in ordered}
    desc_by_id = {t["id"]: (t.get("description") or "") for t in ordered}
    pkg_by_id = {t["id"]: t for t in ordered}
    master_path = P.master_template_path()

    persisted = st.session_state.get("selected_proposal_type")
    if persisted not in type_ids:
        persisted = (
            "professional_service"
            if "professional_service" in type_ids
            else type_ids[0]
        )
        st.session_state.selected_proposal_type = persisted

    step = int(st.session_state.get("wizard_step") or 1)
    step = max(1, min(3, step))
    skip_info = _skips_info_step(
        st.session_state.get("selected_proposal_type")
        or st.session_state.get("proposal_type_id")
    )
    if skip_info and step == 2:
        step = 3
    st.session_state.wizard_step = step
    max_reached = max(int(st.session_state.get("wizard_max") or 1), step)
    st.session_state.wizard_max = max_reached

    _render_wizard_stepper(step, max_reached, skip_info=skip_info)

    # CSS: esconde painéis inativos sem desmontar widgets
    hide_rules = []
    for n in (1, 2, 3):
        if n != step:
            hide_rules.append(
                f'div[class*="st-key-wizard_panel_{n}"] {{ display: none !important; }}'
            )
    if hide_rules:
        st.markdown("<style>" + "".join(hide_rules) + "</style>", unsafe_allow_html=True)

    provider = FIXED_LLM_PROVIDER
    model = FIXED_LLM_MODEL
    api_key = OPENAI_API_KEY
    base_url = FIXED_LLM_BASE_URL

    field_values: dict[str, str] = {}
    brief = transcription = estimate = ""
    client_name = st.session_state.get("info_client") or ""
    project_code = st.session_state.get("info_code") or ""
    logo_file = None

    # —— Painel 1: Tipo ——
    with st.container(border=True, key="wizard_panel_1"):
        _card_head(
            "Tipo de proposta",
            "Escolha a oferta e avance para preencher os dados.",
            step=1,
        )
        if st.session_state.get("proposal_type_id") not in type_ids:
            st.session_state.proposal_type_id = (
                st.session_state.selected_proposal_type
            )
        chosen = st.radio(
            "Tipo de proposta",
            options=type_ids,
            format_func=lambda i: _type_label(i, label_by_id[i]),
            captions=[desc_by_id[i] for i in type_ids],
            horizontal=True,
            key="proposal_type_id",
            label_visibility="collapsed",
            on_change=_on_tipo_selected,
        )
        st.session_state.selected_proposal_type = chosen
        selected_id = chosen
        pkg_preview = pkg_by_id[selected_id]
        mode_preview = pkg_preview.get("mode") or "llm_full"
        label_preview = label_by_id[selected_id]
        if mode_preview == "package":
            if selected_id == "clarion":
                banner_text = (
                    f"Gera a oferta <b>{label_preview}</b> com o deck "
                    "oficial estático. Sem formulário — avance direto "
                    "para gerar o PPTX."
                )
            else:
                banner_text = (
                    f"Gera a oferta <b>{label_preview}</b> com os slides "
                    "oficiais do template. Você preenche só os campos "
                    "comerciais; o restante do layout permanece."
                )
        else:
            banner_text = (
                "Gera a proposta completa a partir do brief. "
                "O LLM escreve os textos nos espaços do template — "
                "sem redesenhar slides."
            )
        st.markdown(
            '<div class="mode-banner">'
            '<div class="mode-banner-text">'
            f'<p class="mode-banner-title">{ICON_INFO} {label_preview}</p>'
            f"<p>{banner_text}</p>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if step == 1:
            _wizard_nav(
                step=1,
                can_advance=True,
                skip_info=_skips_info_step(selected_id),
            )

    selected_id = st.session_state.selected_proposal_type
    if selected_id not in pkg_by_id:
        selected_id = type_ids[0]
        st.session_state.selected_proposal_type = selected_id
    pkg = pkg_by_id[selected_id]
    mode = pkg.get("mode") or "llm_full"
    label = label_by_id[selected_id]

    # —— Painel 2: Informações ——
    with st.container(border=True, key="wizard_panel_2"):
        _card_head(
            "Informações da proposta",
            "Cliente, código e campos da oferta selecionada.",
            step=2,
        )
        g1, g2 = st.columns(2, gap="medium")
        with g1:
            client_name = st.text_input(
                "Cliente", placeholder="NPH / Unisanta", key="info_client"
            )
        with g2:
            project_code = st.text_input(
                "Código da proposta",
                placeholder="BUI001-26",
                key="info_code",
                max_chars=9,
                on_change=_on_project_code_change,
                help="Formato: 3 letras + 3 números + hífen + 2 números (ex.: BUI001-26).",
            )
        logo_file = st.file_uploader(
            "Logo do cliente (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
            key="info_logo",
        )
        stem_preview = _proposal_file_stem(project_code, selected_id)
        st.markdown(
            f'<p class="file-name-preview">Arquivo gerado: '
            f"<b>{stem_preview}.pptx</b></p>",
            unsafe_allow_html=True,
        )
        logo_preview_slot = st.empty()
        if logo_file is not None:
            with logo_preview_slot.container():
                st.markdown(
                    '<div class="logo-preview">'
                    '<p class="logo-preview-label">Preview do logo</p>'
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.image(logo_file, width=220)
        else:
            logo_preview_slot.caption(
                "Envie um PNG ou JPG para visualizar o logo do cliente."
            )

        if mode == "package":
            pkg_fields = pkg.get("fields") or []
            if pkg_fields:
                with st.container(border=True, key="sub_pkg"):
                    _card_head(
                        "Campos da oferta",
                        "Valores que entram na proposta. O layout do "
                        "template oficial não muda.",
                        icon_svg=ICON_BRIEF,
                    )
                    rows = [
                        pkg_fields[i : i + 2]
                        for i in range(0, len(pkg_fields), 2)
                    ]
                    for row in rows:
                        cols = st.columns(len(row) or 1, gap="medium")
                        for col, field in zip(cols, row):
                            fid = field["id"]
                            ftype = field.get("type") or "text"
                            label_f = field.get("label") or fid
                            ph = field.get("placeholder") or ""
                            key = f"pkg_{pkg['id']}_{fid}"
                            with col:
                                if ftype == "textarea":
                                    field_values[fid] = st.text_area(
                                        label_f,
                                        key=key,
                                        placeholder=ph,
                                        height=100,
                                    )
                                elif fid in {"total", "valor_suporte"}:
                                    field_values[fid] = st.text_input(
                                        label_f,
                                        key=key,
                                        placeholder=ph or "R$ 0,00",
                                        on_change=_on_money_field_change,
                                        args=(key,),
                                    )
                                elif fid in {"tempo_execucao"}:
                                    field_values[fid] = st.text_input(
                                        label_f,
                                        key=key,
                                        placeholder=ph or "3",
                                        on_change=_on_months_field_change,
                                        args=(key,),
                                    )
                                else:
                                    field_values[fid] = st.text_input(
                                        label_f, key=key, placeholder=ph
                                    )
            if _uses_brief_field(selected_id):
                brief = _render_brief_context_field()
                field_values["brief"] = (brief or "").strip()
        else:
            brief = _render_brief_context_field()

            with st.expander(
                "Anexos opcionais (transcrição e estimativa)",
                icon=":material/attach_file:",
            ):
                st.caption(
                    "Opcional. Use se tiver ata de reunião ou estimativa "
                    "técnica além do brief."
                )
                transcription_file = st.file_uploader(
                    "Anexar transcrição",
                    type=["txt", "md", "vtt", "srt", "pdf"],
                    key="transcription_uploader",
                    help="O texto extraído preenche o campo abaixo.",
                )
                _apply_upload_to_field(
                    uploaded=transcription_file,
                    text_key="transcription_text",
                    fingerprint_key="_transcription_file_id",
                    label="Transcrição",
                )
                transcription = st.text_area(
                    "Transcrição da reunião",
                    height=160,
                    key="transcription_text",
                    placeholder="Cole aqui a transcrição da reunião…",
                )
                estimate_file = st.file_uploader(
                    "Anexar estimativa (PDF)",
                    type=["pdf"],
                    key="estimate_uploader",
                    help="O texto extraído do PDF preenche o campo abaixo.",
                )
                _apply_upload_to_field(
                    uploaded=estimate_file,
                    text_key="estimate_text",
                    fingerprint_key="_estimate_file_id",
                    label="Estimativa",
                )
                estimate = st.text_area(
                    "Estimativa técnica",
                    height=160,
                    key="estimate_text",
                    placeholder=(
                        "Cole aqui a estimativa técnica ou anexe o PDF…"
                    ),
                )

        if step == 2:
            code_ok = _is_valid_project_code(project_code)
            if project_code.strip() and not code_ok:
                st.warning("Código inválido. Use o formato AAA999-99 (ex.: BUI001-26).")
            _wizard_nav(
                step=2,
                can_advance=code_ok,
                skip_info=_skips_info_step(selected_id),
            )

    # —— Painel 3: Gerar + Resultado ——
    with st.container(border=True, key="wizard_panel_3"):
        _card_head(
            "Gerar proposta",
            "Revise e gere o PPTX oficial.",
            step=3,
        )
        st.markdown(
            f'<p class="checklist"><b>Tipo:</b> {label} · '
            f"<b>Cliente:</b> {(client_name or '—').strip() or '—'} · "
            f"<b>Código:</b> {(project_code or '—').strip() or '—'}</p>",
            unsafe_allow_html=True,
        )
        if mode == "package":
            if selected_id == "clarion":
                st.markdown(
                    '<p class="checklist"><b>Clarion:</b> deck estático — '
                    "gere o PPTX sem preencher formulário.</p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p class="checklist"><b>Antes de gerar:</b> cliente, código e '
                    "campos obrigatórios da oferta preenchidos.</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p class="checklist"><b>Mínimo para Livre:</b> cliente + código + '
                "brief (ou transcrição/estimativa).</p>",
                unsafe_allow_html=True,
            )

        left, right = st.columns([1.2, 1], gap="medium")
        with left:
            generate = st.button(
                f"Gerar {label}" if mode == "package" else "Gerar proposta Livre",
                type="primary",
                use_container_width=True,
                icon=":material/rocket_launch:",
                key="generate_pptx",
            )
        with right:
            with st.container(border=True, key="card_result"):
                _card_head(
                    "Resultado",
                    "Download quando a geração terminar.",
                    icon_svg=ICON_RESULT,
                )
                result_box = st.empty()
                download_box = st.empty()
                last = st.session_state.get("last_result")
                if last:
                    result_box.markdown(
                        _result_success_html(
                            file_name=str(last.get("file_name") or ""),
                            client=str(last.get("client") or ""),
                            code=str(last.get("code") or ""),
                            type_label=str(last.get("type_label") or ""),
                            size_label=str(last.get("size_label") or ""),
                        ),
                        unsafe_allow_html=True,
                    )
                    path = Path(str(last.get("path") or ""))
                    with download_box.container():
                        if path.is_file():
                            st.download_button(
                                label="Baixar PPTX",
                                data=path.read_bytes(),
                                file_name=path.name,
                                mime=(
                                    "application/vnd.openxmlformats-officedocument"
                                    ".presentationml.presentation"
                                ),
                                use_container_width=True,
                                icon=":material/download:",
                                key="download_result_persisted",
                            )
                        if st.button(
                            "Ver detalhes da proposta",
                            use_container_width=True,
                            key="open_result_dialog_persisted",
                            icon=":material/open_in_new:",
                        ):
                            st.session_state.open_result_modal = True
                            st.rerun()
                else:
                    result_box.markdown(
                        _result_empty_state(), unsafe_allow_html=True
                    )

        if step == 3:
            _wizard_nav(
                step=3,
                can_advance=False,
                skip_info=_skips_info_step(selected_id),
            )

    _footer_note()

    if step != 3 or not generate:
        return

    if selected_id == "clarion":
        if not _is_valid_project_code(project_code):
            project_code = "CLA000-00"
    elif not _is_valid_project_code(project_code):
        result_box.error(
            "Código da proposta inválido. Use AAA999-99 (ex.: BUI001-26)."
        )
        return

    if mode == "package":
        _run_package_generation(
            pkg=pkg,
            label=label,
            field_values=field_values,
            master_path=master_path,
            client_name=client_name,
            project_code=project_code,
            logo_file=logo_file,
            result_box=result_box,
            download_box=download_box,
        )
        return

    _run_livre_generation(
        brief=brief,
        transcription=transcription,
        estimate=estimate,
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        client_name=client_name,
        project_code=project_code,
        logo_file=logo_file,
        result_box=result_box,
        download_box=download_box,
    )
