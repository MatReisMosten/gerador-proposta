"""Páginas auxiliares: propostas geradas, templates, histórico e configurações."""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from generator import list_proposal_types
from generator import paths as P

from ui.components import _card_head, _footer_note, _page_header
from ui.formatting import _human_size, _mtime_label
from ui.icons import ICON_BRIEF, ICON_FILE, ICON_RESULT, ICON_SPARK


@st.cache_data(show_spinner=False)
def _template_summary(path_str: str, mtime: float) -> dict:
    """Seções e tokens do mestre (cacheado por mtime do arquivo)."""
    from generator.engine import scan_named_tokens
    from generator.packages import read_pptx_sections

    path = Path(path_str)
    sections = read_pptx_sections(path)
    tokens = scan_named_tokens(path)
    return {
        "sections": {name: len(slides) for name, slides in sections.items()},
        "tokens": sorted(tokens),
    }


def render_geradas() -> None:
    _page_header(
        "Propostas geradas",
        "Arquivos PPTX criados nesta instalação, do mais recente ao mais antigo.",
    )
    files = sorted(
        P.output_dir().glob("*.pptx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        with st.container(border=True, key="card_geradas_vazio"):
            st.markdown(
                '<div class="result-empty">'
                f'<div class="result-empty-icon">{ICON_FILE}</div>'
                "<h4>Nenhuma proposta ainda</h4>"
                "<p>As propostas geradas aparecem aqui com opção de download.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        _footer_note()
        return

    for idx, path in enumerate(files):
        with st.container(border=True, key=f"card_gerada_{idx}"):
            info_col, btn_col = st.columns([3, 1], gap="medium")
            with info_col:
                st.markdown(
                    f'<div class="file-row">{ICON_FILE}<div>'
                    f"<b>{path.name}</b>"
                    f"<small>{_mtime_label(path)} · "
                    f"{_human_size(path.stat().st_size)}</small>"
                    "</div></div>",
                    unsafe_allow_html=True,
                )
            with btn_col:
                st.download_button(
                    "Baixar",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime=(
                        "application/vnd.openxmlformats-officedocument"
                        ".presentationml.presentation"
                    ),
                    use_container_width=True,
                    key=f"dl_{idx}",
                )
    _footer_note()


def render_templates() -> None:
    _page_header(
        "Modelos de template",
        "Slide mestre em uso, suas seções e os tokens disponíveis.",
    )
    try:
        master = P.master_template_path()
    except FileNotFoundError as exc:
        st.error(str(exc))
        _footer_note()
        return

    with st.container(border=True, key="card_master"):
        _card_head("Slide mestre", str(master), icon_svg=ICON_FILE)
        st.markdown(
            f'<p class="meta-line">Arquivo: <b>{master.name}</b></p>'
            f'<p class="meta-line">Tamanho: <b>{_human_size(master.stat().st_size)}</b>'
            f" · Atualizado em <b>{_mtime_label(master)}</b></p>",
            unsafe_allow_html=True,
        )
        summary = _template_summary(str(master), master.stat().st_mtime)
        sections = summary["sections"]
        tokens = summary["tokens"]
        st.markdown(
            f'<p class="meta-line">Seções: <b>{len(sections)}</b>'
            f" · Tokens <code>{{NOME}}</code>: <b>{len(tokens)}</b></p>",
            unsafe_allow_html=True,
        )
        for name, count in sections.items():
            st.markdown(
                f'<p class="meta-line">• {name} — <b>{count} slide(s)</b></p>',
                unsafe_allow_html=True,
            )
        with st.expander(f"Tokens do mestre ({len(tokens)})", icon=":material/code:"):
            st.code("\n".join(tokens) or "(nenhum)", language="text")

    with st.container(border=True, key="card_tipos"):
        _card_head(
            "Tipos de proposta",
            "Registrados em data/packages.json.",
            icon_svg=ICON_BRIEF,
        )
        for item in list_proposal_types():
            mode = item.get("mode") or "llm_full"
            section = item.get("section") or "—"
            st.markdown(
                f'<p class="meta-line"><b>{item.get("label") or item["id"]}</b>'
                f" · modo <code>{mode}</code> · seção <code>{section}</code></p>",
                unsafe_allow_html=True,
            )
    _footer_note()


def render_historico() -> None:
    _page_header(
        "Histórico",
        "Metadados das gerações (cliente, código, tipo e valores usados).",
    )
    entries = sorted(
        P.output_dir().glob("*.values.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not entries:
        with st.container(border=True, key="card_hist_vazio"):
            st.markdown(
                '<div class="result-empty">'
                f'<div class="result-empty-icon">{ICON_RESULT}</div>'
                "<h4>Sem histórico</h4>"
                "<p>Cada proposta gerada registra aqui os valores aplicados "
                "no template.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        _footer_note()
        return

    for idx, path in enumerate(entries):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        with st.container(border=True, key=f"card_hist_{idx}"):
            st.markdown(
                f'<div class="file-row">{ICON_FILE}<div>'
                f'<b>{path.name.replace(".values.json", "")}</b>'
                f"<small>{_mtime_label(path)}</small>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p class="meta-line">Cliente: <b>{payload.get("client") or "—"}</b>'
                f' · Código: <b>{payload.get("code") or "—"}</b>'
                f' · Tipo: <b>{payload.get("type") or "—"}</b></p>',
                unsafe_allow_html=True,
            )
            with st.expander("Valores aplicados", icon=":material/data_object:"):
                st.json(payload.get("values") or {})
    _footer_note()


def render_config() -> None:
    from app import DEFAULT_MODELS

    _page_header(
        "Configurações",
        "Caminhos, template ativo e preferências desta instalação.",
    )
    try:
        master = str(P.master_template_path())
    except FileNotFoundError as exc:
        master = f"não encontrado ({exc})"

    with st.container(border=True, key="card_paths"):
        _card_head("Caminhos", "Resolvidos automaticamente.", icon_svg=ICON_FILE)
        rows = [
            ("Diretório de dados", str(P.UNISANTA)),
            ("Slide mestre", master),
            ("Registry de tipos", str(P.packages_registry_path())),
            ("Saída das propostas", str(P.output_dir())),
        ]
        for name, value in rows:
            st.markdown(
                f'<p class="meta-line">{name}: <b>{value}</b></p>',
                unsafe_allow_html=True,
            )

    with st.container(border=True, key="card_llm_defaults"):
        _card_head(
            "Modelos padrão",
            "Sugestões usadas no modo Livre (pode alterar na geração).",
            icon_svg=ICON_SPARK,
        )
        for prov, mod in DEFAULT_MODELS.items():
            st.markdown(
                f'<p class="meta-line">{prov}: <code>{mod}</code></p>',
                unsafe_allow_html=True,
            )
        gate = "ativo" if os.environ.get("APP_PASSWORD", "").strip() else "desativado"
        st.markdown(
            f'<p class="meta-line">Senha de acesso (APP_PASSWORD): <b>{gate}</b></p>',
            unsafe_allow_html=True,
        )
    _footer_note()
