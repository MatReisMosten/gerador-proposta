"""LLM: brief/chat → JSON de valores para slots {S##_T##}."""

from __future__ import annotations

import json
import re
from typing import Any

SYSTEM_PROMPT = """Você é um redator comercial da Mosten.
Sua tarefa é preencher TODOS os slots de uma proposta técnica em PowerPoint.
Responda APENAS com um único objeto JSON válido (sem markdown, sem comentários).
Chaves do JSON = nomes dos slots exatamente como fornecidos (ex: "{S01_T00}").
Valores = strings em português brasileiro, adequadas ao papel (title/subtitle/body/label).
Preserve quebras de linha com \\n quando o exemplo original tiver várias linhas.
Para labels curtos (O DESAFIO, NOSSA SOLUÇÃO, números 1-4, R$), mantenha o label se fizer sentido.
Não invente preços se o brief disser "a definir" — use "A definir" / "—".
Não deixe slots vazios: se faltar info, escreva um texto coerente e conservador.
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
    # Compact catalog to control tokens
    compact = {}
    for key, info in catalog.items():
        compact[key] = {
            "role": info.get("role"),
            "slide": info.get("slide"),
            "hint": (info.get("original_example") or "")[:160],
        }

    parts = [
        f"Cliente: {client_name or '(não informado)'}",
        f"Código da proposta: {project_code or '(gerar se fizer sentido, ex: XXX001-26)'}",
        "",
        "BRIEF DO USUÁRIO:",
        brief.strip(),
        "",
        "CATÁLOGO DE SLOTS (preencha TODOS):",
        json.dumps(compact, ensure_ascii=False),
    ]

    if example_values:
        # Few-shot truncated — only a sample of keys to show style
        sample_keys = list(example_values.keys())[:25]
        sample = {k: example_values[k][:200] for k in sample_keys}
        parts.extend(
            [
                "",
                "EXEMPLO DE ESTILO (proposta Vigia — use só como referência de tom, NÃO copie o conteúdo):",
                json.dumps(sample, ensure_ascii=False),
            ]
        )

    parts.append(
        "\nRetorne um JSON com exatamente as mesmas chaves do catálogo."
    )
    return "\n".join(parts)


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
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url or None)
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
    return {str(k): str(v) for k, v in data.items()}


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
    return {str(k): str(v) for k, v in data.items()}


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
