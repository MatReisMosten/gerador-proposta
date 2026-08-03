"""
Gerador de Propostas Mosten — Streamlit MVP.

Uso:
  cd .agents/skills/proposal-library-builder/proposal_app
  pip install -r requirements.txt
  streamlit run app.py
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from generator import build_deck, fill_slots, load_slot_catalog  # noqa: E402
from generator import paths as P  # noqa: E402

DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "openrouter": "openai/gpt-4.1-mini",
}


def gate_password() -> bool:
    """Optional APP_PASSWORD env — simple gate for public Railway URL."""
    import os

    expected = os.environ.get("APP_PASSWORD", "").strip()
    if not expected:
        return True
    if st.session_state.get("_authed"):
        return True
    st.title("Gerador de Propostas Mosten")
    pwd = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar") and pwd == expected:
        st.session_state._authed = True
        st.rerun()
    if pwd:
        st.error("Senha incorreta.")
    return False


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "proposta"


def load_example_values() -> dict[str, str] | None:
    path = P.example_values_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("vigia") or data.get("values")


def main() -> None:
    st.set_page_config(
        page_title="Gerador de Propostas Mosten",
        page_icon="📄",
        layout="wide",
    )
    if not gate_password():
        return
    st.title("Gerador de Propostas Mosten")
    st.caption(
        "Cole sua API key, descreva a proposta e baixe o PPTX. "
        "O visual vem do Modelo-Proposta Técnica — o LLM só preenche o texto."
    )

    with st.sidebar:
        st.header("Configuração")
        provider = st.selectbox(
            "Provider",
            options=["openai", "anthropic", "openrouter"],
            format_func=lambda x: {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "openrouter": "OpenRouter",
            }[x],
        )
        api_key = st.text_input(
            "API Key",
            type="password",
            help="A chave fica só nesta sessão do navegador/servidor local. Não é salva em disco.",
            placeholder="sk-...",
        )
        model = st.text_input(
            "Modelo",
            value=DEFAULT_MODELS[provider],
            help="Prefira modelos baratos (mini/haiku/flash) — o trabalho é só texto→JSON.",
        )
        base_url = None
        if provider == "openrouter":
            base_url = st.text_input(
                "Base URL",
                value="https://openrouter.ai/api/v1",
            )
        elif provider == "openai":
            custom = st.text_input("Base URL (opcional)", value="")
            base_url = custom.strip() or None

        st.divider()
        st.subheader("Proposta")
        client_name = st.text_input("Cliente", placeholder="NPH / Unisanta")
        project_code = st.text_input("Código", placeholder="UNS001-26")
        output_name = st.text_input(
            "Nome do arquivo",
            value="",
            placeholder="auto",
        )
        logo_file = st.file_uploader("Logo do cliente (PNG/JPG)", type=["png", "jpg", "jpeg"])

        st.divider()
        st.caption(f"Modelo: `{P.MODEL_NAME}`")
        try:
            st.caption(f"Fonte: `{P.resolve_model()}`")
        except FileNotFoundError as exc:
            st.error(str(exc))

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("Brief / conteúdo")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        brief = st.text_area(
            "Descreva a proposta (pode colar um markdown completo)",
            height=320,
            placeholder=(
                "Exemplo:\n"
                "Cliente: NPH/Unisanta\n"
                "Produto: Vigia — camada de alertas de risco costeiro\n"
                "Problema: dado científico não vira decisão em campo\n"
                "Solução: tradução, segmentação, Prismia, feedback\n"
                "Cronograma: 5 semanas\n"
                "Preço: a definir / captação conjunta\n"
                "CTA: validar parceria e ACT"
            ),
        )

        # Optional chat-style follow-ups stored in session
        follow = st.chat_input("Complemento rápido (opcional)…")
        if follow:
            st.session_state.messages.append(follow)
        if st.session_state.messages:
            with st.expander("Complementos do chat", expanded=False):
                for m in st.session_state.messages:
                    st.markdown(f"- {m}")
                if st.button("Limpar complementos"):
                    st.session_state.messages = []
                    st.rerun()

        generate = st.button("Gerar proposta PPTX", type="primary", use_container_width=True)

    with col2:
        st.subheader("Resultado")
        result_box = st.empty()
        download_box = st.empty()
        json_box = st.empty()

    if generate:
        if not api_key.strip():
            st.error("Informe a API Key na barra lateral.")
            return
        if not brief.strip() and not st.session_state.messages:
            st.error("Escreva um brief ou pelo menos um complemento.")
            return

        full_brief = brief.strip()
        if st.session_state.messages:
            full_brief += "\n\nComplementos:\n" + "\n".join(
                f"- {m}" for m in st.session_state.messages
            )

        with st.spinner("Preparando template e slots…"):
            try:
                catalog = load_slot_catalog()
            except Exception as exc:
                st.error(f"Falha ao carregar template: {exc}")
                return

        with st.spinner("LLM preenchendo os textos da proposta…"):
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
                st.error(f"Falha na chamada ao LLM: {exc}")
                return

        # Ensure required keys exist
        missing = [k for k in catalog if k not in values]
        if missing:
            result_box.warning(
                f"{len(missing)} slots sem valor do LLM — preenchidos com texto original do modelo."
            )

        logo_path = None
        tmp_logo = None
        if logo_file is not None:
            tmp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=Path(logo_file.name).suffix)
            tmp_logo.write(logo_file.getvalue())
            tmp_logo.close()
            logo_path = Path(tmp_logo.name)
        else:
            default_logo = P.ASSETS / "logo-nph.png"
            if default_logo.is_file() and (
                not client_name or "nph" in client_name.lower() or "unisanta" in client_name.lower()
            ):
                logo_path = default_logo

        code = project_code.strip() or "PROPOSTA"
        name = output_name.strip() or (
            f"{code} - {slugify(client_name or 'cliente')} - "
            f"{date.today().isoformat()}.pptx"
        )
        if not name.lower().endswith(".pptx"):
            name += ".pptx"
        out_path = P.output_dir() / name

        with st.spinner("Montando PPTX…"):
            try:
                build_deck(values, output_path=out_path, logo_path=logo_path)
            except Exception as exc:
                st.error(f"Falha ao montar PPTX: {exc}")
                return

        result_box.success(f"Proposta gerada: `{out_path.name}`")
        data = out_path.read_bytes()
        download_box.download_button(
            label="Baixar PPTX",
            data=data,
            file_name=out_path.name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
        with json_box.expander("JSON dos valores (debug)"):
            st.json(values)

        # also save values alongside
        values_path = out_path.with_suffix(".values.json")
        values_path.write_text(
            json.dumps(
                {
                    "client": client_name,
                    "code": project_code,
                    "provider": provider,
                    "model": model,
                    "values": values,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
