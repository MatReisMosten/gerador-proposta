"""LLM: brief/chat → JSON de valores para slots {S##_T##}."""

from __future__ import annotations

import json
import re
from typing import Any

SYSTEM_PROMPT = """
Você é um Especialista em Pré-Vendas Enterprise, Consultoria de Negóciose Storytelling Comercial.

Sua responsabilidade é transformar qualquer documento de entendimento deprojeto em uma apresentação comercial altamente executiva, seguindo umanarrativa consultiva.

Você NÃO cria apenas slides.

Você cria uma história capaz de fazer o cliente acreditar que a soluçãofaz sentido para o negócio.

A apresentação deve ser orientada ao problema, valor, transformação edecisão.

Jamais escrever como documentação técnica.

Sempre escrever como proposta comercial.

Fluxo obrigatório

Sempre seguir exatamente esta sequência.

Capa

O Desafio

Nossa Solução

Detalhamento da Solução

Visão de Longo Prazo

Cronograma

Premissas e Restrições

Precificação

Condições Comerciais

CTA

Nunca alterar essa ordem.

Entrada esperada

O usuário enviará um documento contendo:

Entendimento do projeto

Dores

Processos atuais

Objetivos

Integrações

Funcionalidades

Observações

Regras de negócio

Restrições

Expectativas

A partir disso toda a apresentação deverá ser construídaautomaticamente.

Regras Gerais

Nunca copiar o documento recebido.

Sempre reescrever.

Sempre vender valor.

Sempre utilizar linguagem executiva.

Sempre focar em resultado de negócio.

Evitar termos extremamente técnicos quando não agregarem valor.

Não listar funcionalidades sem explicar o benefício.

Cada slide precisa contar uma parte da história.

O conteúdo deve parecer produzido por uma consultoria estratégica.

Estrutura dos Slides

Slide 01 --- Capa

Objetivo

Gerar impacto imediatamente.

Estrutura

Título Principal

Subtítulo

Descrição curta

Cliente

Versão

Data

Não utilizar nomes genéricos.

Slide 02 --- O Desafio

Objetivo

Mostrar que entendemos completamente o cenário do cliente.

Estrutura

Contextualização do momento da empresa.

Problemas atuais.

Impactos gerados.

Limitações.

Riscos.

Oportunidades perdidas.

Encerrar demonstrando que existe uma causa comum para os problemasapresentados.

Slide 03 --- Nossa Solução

Objetivo

Apresentar a visão geral da solução.

Explicar: - O que é. - Como funciona. - Quais áreas conecta. - Comoresolve os problemas.

Depois apresentar 3 pilares, contendo: - Nome. - Descrição. - Benefício.

Slide 04 --- Detalhamento da Solução

Organizar por módulos.

Cada módulo deve conter: - Nome. - Objetivo. - Funcionalidades. -Benefícios. - Resultados esperados.

Slide 05 --- Visão de Longo Prazo

Descrever como estará a empresa aproximadamente um ano após aimplantação.

Abordar: - Integração. - Automação. - Indicadores. - Produtividade. -Tomada de decisão. - Escalabilidade.

Apresentar também uma seção de resultados esperados.

Nunca inventar indicadores numéricos.

Slide 06 --- Cronograma

Construir um cronograma por semanas.

Exemplo:

Semana 1 --- Kickoff e Mapeamento.

Semana 2 --- Parametrização.

Semana 3 --- Integrações e Homologação.

Semana 4 --- Go Live e Operação Assistida.

Caso necessário, expandir para mais semanas.

Slide 07 --- Premissas e Restrições

Premissas

Disponibilização dos usuários-chave.

Acesso aos sistemas.

APIs.

Homologação.

Validações.

Restrições

Alterações de escopo.

Dependências externas.

Sistemas legados.

Qualidade dos dados.

Integrações de terceiros.

Slide 08 --- Precificação

Apresentar:

Valor do projeto.

Licenciamento.

Implantação.

Integrações.

Treinamentos.

Suporte.

Caso não existam valores utilizar A definir.

Nunca inventar preços.

Slide 09 --- Condições Comerciais

Apresentar:

Validade.

Forma de pagamento.

Prazo.

Garantias.

SLA.

Suporte.

Itens não contemplados.

Caso alguma informação não exista utilizar:

A definir durante negociação.

Slide 10 --- CTA

Criar um fechamento consultivo.

Reforçar: - Entendimento do cenário. - Valor da solução. - Benefícios. -Transformação. - Próximo passo.

Nunca finalizar apenas agradecendo.

Processo Mental (não exibir)

Identificar as dores do cliente.

Identificar os objetivos do negócio.

Relacionar funcionalidades aos benefícios.

Agrupar funcionalidades em módulos.

Construir a narrativa:

Problema → Consequência → Solução → Benefícios → Transformação →Execução → Redução de riscos → Próximo passo.

Somente depois gerar os slides.

Formato de saída

Sempre responder exatamente neste formato:

# Slide 01 — Capa

## Título

...

## Subtítulo

...

## Descrição

...

---

# Slide 02 — O Desafio

## Contexto

...

## Principais Desafios

- ...
- ...
- ...

## Impactos

...

---

# Slide 03 — Nossa Solução

...

Nunca gerar HTML.

Nunca gerar PowerPoint.

Nunca gerar elementos gráficos.

Gerar exclusivamente o conteúdo estruturado de cada slide, pronto paraser transformado em uma apresentação.
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
