"""LLM: brief/chat → JSON de valores para tokens nomeados {TOKEN} do slide-mestre."""

from __future__ import annotations

import json
import re
from typing import Any

SYSTEM_PROMPT = """
Você é um Especialista em Pré-Vendas Enterprise, Consultoria de Negócios e Storytelling Comercial da Mosten.

Sua responsabilidade é transformar qualquer documento de entendimento de projeto em uma apresentação comercial altamente executiva, seguindo a Narrative Storytelling Engine da Mosten.

Você NÃO cria apenas slides.
Você cria uma jornada narrativa. Os slides são apenas a forma de dar vida a essa jornada.

A narrativa vem antes dos slides.
A solução nunca é a protagonista.
A protagonista é a transformação do negócio do cliente.
O produto emerge como consequência natural da narrativa, nunca como ponto de partida.

Jamais escrever como documentação técnica.
Sempre escrever como proposta comercial consultiva.

Regra fundamental da Mosten

Entendemos o contexto.
Entendemos os pontos de fricção.
Entendemos o impacto no negócio.
Há uma forma melhor de operar.
Apresentamos uma visão de transformação.
Damos vida a essa visão por meio de um ecossistema de soluções.
Executamos a transformação de forma segura e incremental.
Entregamos uma operação mais inteligente, previsível e pronta para crescer.

Entrada esperada

O usuário enviará um documento contendo (quando disponível): contexto da operação, fricções, impacto no negócio, objetivos de transformação, processos atuais, integrações, escopo, restrições, estimativas e expectativas.

A partir disso, construa a apresentação automaticamente.
Nunca copiar o documento recebido — sempre reescrever em linguagem executiva.

Regras gerais de escrita

- Sempre vender transformação, nunca features isoladas.
- Linguagem executiva, clara e humana.
- Focar em resultado de negócio.
- Evitar jargão técnico quando não agregar valor.
- Cada slide conta um beat da história; nenhum slide repete o anterior.
- Até apresentar a Solução: ZERO menção a módulos, telas, OCR, IA como produto, nomes de software ou features.
- Capa: vende transformação, não produto; cada placeholder preenchido individualmente; zero features/arquitetura.
- Dor/Desafio: sequência contexto → ruptura → consequências → sintomas (cards) → fechamento sem solução; nunca culpe o cliente.
- Solução/Oportunidade: vende nova forma de operar (não software); capacidades, não features.
- Resultados / Visão Futura: Future Pacing no presente; aspiração, não urgência.
- Densidade de texto é obrigatória e permanente (todas as propostas futuras):
  use o campo "role"/"writing" de cada token no catálogo.
- role=narrative: 2–3 parágrafos curtos separados por \\n\\n (45–90 palavras).
  Nunca devolver só uma frase nesses campos.
- role=card_desc: 1–2 frases (10–22 palavras) explicando consequência/contexto
  sob o título do card — nunca um rótulo seco.
- role=title|subtitle|label|step|bullet|meta|cover: manter conciso; sem parágrafos.
- Cronograma: NUNCA inventar semanas, horas, fases, entregáveis; se não houver dado no brief → "".
- Premissas e Restrições: NUNCA inventar; só extrair do brief; lacuna → "".
- Nunca inventar preços ou SLAs. Se não houver dado comercial: "A definir" / "".
- Preencha APENAS as chaves do catálogo de tokens nomeados ({TITULO_DOR}, {BREVE_DESCRICAO}, …).
- Nunca invente tokens que não estejam no catálogo.
- Texto cru do template (rótulos como "O DESAFIO", "NOSSA SOLUÇÃO", footers) NÃO é sua responsabilidade — só os {TOKENS}.

Processo mental (não exibir)

Context → Challenge → Impact → Opportunity → Vision → Results → Delivery → Premises → Outcome.

Só depois preencher os tokens do PPTX.

Famílias de tokens (quando existirem no catálogo)

CAPA — {TITULO_CAPA}, {BREVE_DESCRICAO}, metadados ({COD_PROJ}, {DATA} podem vir do contexto).
DOR / DESAFIO — {TITULO_DOR}, {TITULO_DESAFIO}, {ITEM_*_DESAFIO}, {DESC_*}, sintomas e impactos de negócio.
OPORTUNIDADE — {TITULO_OPORTUNIDADE}, {DESC_OPORTUNIDADE}, {ITEM_*_OPORTUNIDADE}, {TITULO_*_OPORT*}.
SOLUÇÃO — {TITULO_SOLUCAO}, {DESC_SOLUCAO}, {TITULO_*_ITEM}, pilares/capacidades.
RESULTADOS / CRONOGRAMA / PREMISSAS — preencha só se o token existir no catálogo e houver dado no brief; senão "".

Todas as variantes de layout que compartilham o mesmo token recebem o mesmo valor (preencha uma vez).

Guia narrativo por seção (aplicar aos tokens daquela seção)

CAPA — título 4–10 palavras (transformação, não produto); breve descrição 1–3 linhas; placeholders independentes.
DOR — nunca culpe o cliente; contexto → ruptura → consequências de negócio; campos narrativos em 2–3 parágrafos; cards = sintomas operacionais, nunca features técnicas.
OPORTUNIDADE / SOLUÇÃO — nova forma de operar; campos narrativos em 2–3 parágrafos; capacidades percebidas; sem módulos/APIs/OCR/IA.
RESULTADOS — Future Pacing no presente ("a operação possui…"); campos narrativos em 2–3 parágrafos; aspiração.
CRONOGRAMA / PREMISSAS — só fatos do brief; sem inventar; lacuna = "".

Formato de saída

Retorne APENAS um JSON objeto.
Chaves = exatamente as mesmas do catálogo ({TITULO_CAPA}, {BREVE_DESCRICAO}, …).
Valores = strings prontas para os textos dos slides.
Não gere markdown de slides, HTML, PowerPoint nem elementos gráficos.
Não explique o raciocínio — só o JSON.
"""
def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    # fallback: first {...} block
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("A resposta do modelo não contém JSON válido.")
    data = json.loads(m.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON raiz deve ser um objeto.")
    return data


def build_user_prompt(
    *,
    brief: str,
    catalog: dict[str, dict],
    example_values: dict[str, str] | None = None,
    project_code: str = "",
    client_name: str = "",
) -> str:
    # Group tokens by section for clearer prompting
    by_section: dict[str, list[str]] = {}
    compact: dict[str, dict] = {}
    for key, info in catalog.items():
        section = (info.get("section") or "OUTROS").strip() or "OUTROS"
        by_section.setdefault(section, []).append(key)
        compact[key] = {
            "role": info.get("role"),
            "writing": info.get("writing"),
            "section": section,
            "slides": info.get("slides") or ([info.get("slide")] if info.get("slide") else []),
            "count": info.get("count", 1),
        }

    section_lines = []
    for section, keys in by_section.items():
        section_lines.append(f"- {section}: {', '.join(keys)}")

    by_role: dict[str, list[str]] = {}
    for key, info in catalog.items():
        by_role.setdefault(info.get("role") or "narrative", []).append(key)
    role_lines = []
    for role in (
        "narrative",
        "card_desc",
        "title",
        "subtitle",
        "label",
        "bullet",
        "step",
        "meta",
        "cover",
    ):
        keys = by_role.get(role) or []
        if keys:
            role_lines.append(f"- {role}: {', '.join(keys)}")

    parts = [
        f"Cliente: {client_name or '(não informado)'}",
        f"Código da proposta: {project_code or '(gerar se fizer sentido, ex: XXX001-26)'}",
        "",
        "BRIEF DO USUÁRIO:",
        brief.strip(),
        "",
        "REGRA DE PREENCHIMENTO:",
        "- Preencha APENAS os tokens {NOME} listados no catálogo.",
        "- Texto cru do PPTX (rótulos, footers, frases fixas) NÃO deve ser reescrito — não há chave para isso.",
        "- Se não houver informação no brief para um token (ex.: cronograma/premissa), use string vazia \"\".",
        "- Tokens iguais em várias variantes de slide recebem o mesmo valor.",
        "- OBRIGATÓRIO: respeite role/writing de cada token (densidade permanente para todas as gerações).",
        "- narrative → 2–3 parágrafos separados por \\n\\n (45–90 palavras); nunca uma frase isolada.",
        "- card_desc → 1–2 frases (10–22 palavras) sob o título; explique consequência/contexto.",
        "- title/subtitle/label/step/bullet/meta/cover → curtos; sem parágrafos.",
        "",
        "TOKENS POR DENSIDADE DE ESCRITA:",
        *role_lines,
        "",
        "TOKENS POR SEÇÃO DO TEMPLATE:",
        *section_lines,
        "",
        "CATÁLOGO DE TOKENS (preencha TODAS as chaves):",
        json.dumps(compact, ensure_ascii=False),
    ]

    if example_values:
        # Few-shot: only named-token style keys if present
        named = {
            k: v[:200]
            for k, v in example_values.items()
            if k.startswith("{") and "S0" not in k[:6]
        }
        sample_src = named or example_values
        sample_keys = list(sample_src.keys())[:20]
        sample = {k: sample_src[k][:200] for k in sample_keys}
        parts.extend(
            [
                "",
                "EXEMPLO DE ESTILO (tom apenas — NÃO copie conteúdo nem chaves antigas {S##_T##}; "
                "respeite a densidade role/writing do catálogo, não encurte campos narrative/card_desc):",
                json.dumps(sample, ensure_ascii=False),
            ]
        )

    parts.append(
        "\nRetorne um JSON com exatamente as mesmas chaves do catálogo (tokens {NOME})."
    )
    return "\n".join(parts)


def _normalize_llm_values(data: dict[str, Any], catalog: dict[str, dict]) -> dict[str, str]:
    """Map LLM keys onto catalog tokens; ensure every catalog key exists."""
    out: dict[str, str] = {}
    # index without braces
    by_inner = {k.strip("{}").upper(): k for k in catalog}

    for k, v in data.items():
        raw = str(k).strip()
        if not raw or raw.startswith("_"):
            continue
        key = raw if raw.startswith("{") else "{" + raw.strip("{}") + "}"
        if key in catalog:
            out[key] = "" if v is None else str(v)
            continue
        canon = by_inner.get(key.strip("{}").upper())
        if canon:
            out[canon] = "" if v is None else str(v)

    for key in catalog:
        out.setdefault(key, "")
    return out


def fill_slots_openai(
    *,
    api_key: str,
    brief: str,
    catalog: dict[str, dict],
    model: str = "gpt-4.1-mini",
    base_url: str | None = None,
    example_values: dict[str, str] | None = None,
    project_code: str = "",
    client_name: str = "",
) -> dict[str, str]:
    import os

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        base_url=base_url or None,
    )
    user = build_user_prompt(
        brief=brief,
        catalog=catalog,
        example_values=example_values,
        project_code=project_code,
        client_name=client_name,
    )
    resp = client.chat.completions.create(
        model=model,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
    )
    content = resp.choices[0].message.content or "{}"
    data = _extract_json(content)
    return _normalize_llm_values(data, catalog)


def fill_slots_anthropic(
    *,
    api_key: str,
    brief: str,
    catalog: dict[str, dict],
    model: str = "claude-haiku-4-5-20251001",
    example_values: dict[str, str] | None = None,
    project_code: str = "",
    client_name: str = "",
) -> dict[str, str]:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    user = build_user_prompt(
        brief=brief,
        catalog=catalog,
        example_values=example_values,
        project_code=project_code,
        client_name=client_name,
    )
    resp = client.messages.create(
        model=model,
        max_tokens=16000,
        temperature=0.3,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
    )
    content = "".join(
        block.text for block in resp.content if getattr(block, "type", "") == "text"
    )
    data = _extract_json(content)
    return _normalize_llm_values(data, catalog)


def fill_slots(
    *,
    provider: str,
    api_key: str,
    brief: str,
    catalog: dict[str, dict],
    model: str,
    example_values: dict[str, str] | None = None,
    project_code: str = "",
    client_name: str = "",
    base_url: str | None = None,
) -> dict[str, str]:
    provider = provider.lower().strip()
    if provider in {"openai", "openrouter"}:
        url = base_url
        if provider == "openrouter" and not url:
            url = "https://openrouter.ai/api/v1"
        return fill_slots_openai(
            api_key=api_key,
            brief=brief,
            catalog=catalog,
            model=model,
            base_url=url,
            example_values=example_values,
            project_code=project_code,
            client_name=client_name,
        )
    if provider == "anthropic":
        return fill_slots_anthropic(
            api_key=api_key,
            brief=brief,
            catalog=catalog,
            model=model,
            example_values=example_values,
            project_code=project_code,
            client_name=client_name,
        )
    raise ValueError(f"Provider não suportado: {provider}")
