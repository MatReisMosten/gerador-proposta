"""Componentes de UI compartilhados: cabeçalhos, wizard, overlay de loading."""

from __future__ import annotations

import streamlit as st

from ui.icons import ICON_BRIEF, ICON_RESULT, TYPE_ICONS

FOOTER_NOTE = (
    "Seus dados são utilizados apenas para gerar a proposta e não são armazenados."
)


def _card_head(
    title: str,
    hint: str = "",
    *,
    step: int | None = None,
    icon_svg: str | None = None,
) -> None:
    if step is not None:
        mark = f'<div class="card-badge">{step}</div>'
    else:
        mark = f'<div class="card-icon">{icon_svg or ICON_BRIEF}</div>'
    hint_html = f'<p class="card-hint">{hint}</p>' if hint else ""
    st.markdown(
        f'<div class="card-head">{mark}<div>'
        f'<p class="card-title">{title}</p>{hint_html}'
        "</div></div>",
        unsafe_allow_html=True,
    )


def _page_header(title: str, subtitle: str, *, with_theme: bool = True) -> None:
    _ = with_theme  # tema fixo claro
    from app import MOSTEN_LOGO

    if MOSTEN_LOGO.is_file():
        st.image(str(MOSTEN_LOGO), width=132)
    st.markdown(
        f'<p class="page-title">{title}</p>'
        f'<p class="page-sub">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def _render_wizard_stepper(
    current: int, max_reached: int, *, skip_info: bool = False
) -> None:
    steps = [
        (1, "Tipo", "Escolha a oferta"),
        (2, "Informações", "Cliente e campos"),
        (3, "Gerar", "Revisar e baixar"),
    ]
    parts: list[str] = ['<div class="wizard-stepper">']
    for i, (num, title, hint) in enumerate(steps):
        if num < current:
            state = "done"
            mark = "✓"
        elif num == current:
            state = "active"
            mark = str(num)
        else:
            state = "todo"
            mark = str(num)
        # Clarion: step 2 is not part of the path
        if skip_info and num == 2:
            if current >= 3:
                state = "done"
                mark = "✓"
            else:
                state = "todo"
                mark = "—"
            hint = "Não se aplica"
        parts.append(
            f'<div class="wizard-node {state}">'
            f'<div class="wizard-dot">{mark}</div>'
            f'<div class="wizard-meta"><b>{title}</b><span>{hint}</span></div>'
            f"</div>"
        )
        if i < len(steps) - 1:
            if skip_info and num == 1:
                line = "filled" if current >= 3 else ""
            else:
                line = "filled" if num < current else ""
            parts.append(f'<div class="wizard-line {line}"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3, gap="small")
    for col, num, title in (
        (b1, 1, "1 · Tipo"),
        (b2, 2, "2 · Informações"),
        (b3, 3, "3 · Gerar"),
    ):
        with col:
            if skip_info and num == 2:
                disabled = True
            else:
                disabled = num > max_reached
            if st.button(
                title,
                key=f"wizard_jump_{num}",
                use_container_width=True,
                disabled=disabled,
                type="primary" if num == current else "secondary",
            ):
                st.session_state.wizard_step = num
                st.rerun()


def _wizard_nav(
    *, step: int, can_advance: bool = True, skip_info: bool = False
) -> None:
    back, _, nxt = st.columns([1, 2, 1], gap="medium")
    with back:
        if step > 1:
            if st.button(
                "Voltar",
                key=f"wizard_back_{step}",
                use_container_width=True,
                icon=":material/arrow_back:",
            ):
                if skip_info and step == 3:
                    st.session_state.wizard_step = 1
                else:
                    st.session_state.wizard_step = step - 1
                st.rerun()
    with nxt:
        if step < 3:
            if st.button(
                "Avançar",
                key=f"wizard_next_{step}",
                use_container_width=True,
                type="primary",
                icon=":material/arrow_forward:",
                disabled=not can_advance,
            ):
                if skip_info and step == 1:
                    next_step = 3
                else:
                    next_step = step + 1
                st.session_state.wizard_step = next_step
                st.session_state.wizard_max = max(
                    int(st.session_state.get("wizard_max") or 1), next_step
                )
                st.rerun()


def _footer_note() -> None:
    st.markdown(f'<p class="footer-note">{FOOTER_NOTE}</p>', unsafe_allow_html=True)


def _type_label(type_id: str, label: str) -> str:
    icon = TYPE_ICONS.get(type_id, ":material/description:")
    return f"{icon} {label}"


class FullscreenLoading:
    """Overlay de tela cheia com spinner + porcentagem."""

    def __init__(self, title: str = "Gerando proposta") -> None:
        self.title = title
        self._slot = st.empty()

    def update(self, percent: int, message: str) -> None:
        pct = max(0, min(100, int(percent)))
        self._slot.markdown(
            f"""
<div class="mosten-loading-overlay">
  <div class="mosten-loading-card">
    <div class="mosten-loading-spinner"></div>
    <div class="mosten-loading-pct">{pct}%</div>
    <p class="mosten-loading-title">{self.title}</p>
    <p class="mosten-loading-msg">{message}</p>
    <div class="mosten-loading-bar"><i style="transform:scaleX({pct / 100})"></i></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    def close(self) -> None:
        self._slot.empty()


def _result_empty_state() -> str:
    return (
        '<div class="result-empty">'
        f'<div class="result-empty-icon">{ICON_BRIEF}</div>'
        "<h4>Aguardando geração</h4>"
        "<p>Quando a proposta estiver pronta, "
        "o download aparece aqui.</p>"
        "</div>"
    )


def _result_success_html(
    *,
    file_name: str,
    client: str,
    code: str,
    type_label: str,
    size_label: str,
) -> str:
    client_disp = client.strip() or "—"
    code_disp = code.strip() or "—"
    return (
        '<div class="result-success">'
        f'<div class="result-empty-icon" style="margin:0 auto 0.85rem">'
        f"{ICON_RESULT}</div>"
        "<h4>Proposta gerada</h4>"
        f"<p><b>{file_name}</b></p>"
        f'<p class="result-meta">Cliente: <b>{client_disp}</b></p>'
        f'<p class="result-meta">Código: <b>{code_disp}</b></p>'
        f'<p class="result-meta">Tipo: <b>{type_label}</b></p>'
        f'<p class="result-meta">Tamanho: <b>{size_label}</b></p>'
        "</div>"
    )
