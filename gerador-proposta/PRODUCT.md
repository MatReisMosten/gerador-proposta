# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Time comercial Mosten. Usa o gerador para montar propostas comerciais em PPTX com agilidade e consistência de template, sem redesenhar slides do zero.

## Product Purpose

Gerar propostas comerciais Mosten em PowerPoint a partir de um slide mestre oficial e de insumos do time (cliente, código, brief, logo, premissas, etc.). Sucesso = proposta pronta para download, alinhada ao template e utilizável no ciclo comercial.

## Positioning

Modo Livre com LLM preenche apenas tokens `{NOME}` do mestre — a narrativa comercial nasce do brief/contexto, sem redesenhar a estrutura visual dos slides. Pacotes (Professional Service, Suporte, PassLog, Discovery, Clarion) geram seções fixas do mestre com campos variáveis. Escopo Fechado (DP World) isola a seção do mestre e preenche os textos via LLM a partir dos insumos — só `{COD_PROJETO}`, sem nome nem logo do cliente.

## Operating Context

- App Streamlit (`streamlit run app.py`)
- Tipos de proposta registrados em `data/packages.json`: Professional Service, Suporte, Controle de Acesso (PassLog), Discovery, Clarion, Escopo Fechado (DP World), Livre
- Template canônico: `data/slide-mestre-template.pptx`
- Saída em `data/geradas/`
- Provider/modelo de LLM fixos no código (OpenAI, `gpt-4.1-mini`); chave via `OPENAI_API_KEY` no `.env` do servidor — não há campo de chave por sessão de usuário. Senha opcional de acesso via `APP_PASSWORD` em deploy público.

## Capabilities and Constraints

- Preenche placeholders e monta PPTX; não é editor visual de slides
- Dados do formulário são para geração na sessão (não são o repositório de propostas da empresa)
- Tipos e seções do mestre definem o que pode ser gerado; conteúdo inventado fora do brief/template não é fonte de verdade

## Brand Commitments

- Identidade Mosten (nome, voz e assets de marca oficiais)
- Templates oficiais do slide mestre — não substituir por layouts ad hoc
- Logo Mosten em `data/assets/logo-mosten.png`; design system Mosten (Orla/ODS) disponível no projeto para UI

## Evidence on Hand

- `app.py` — UI Streamlit do gerador
- `data/slide-mestre-template.pptx` — template mestre
- `data/packages.json` — tipologias
- `data/assets/logo-mosten.png` — wordmark Mosten
- Skills locais de design system Mosten em `.cursor/skills/mosten-design-system*`
- Não fabricar depoimentos, cases, preços ou clientes sem fonte

## Product Principles

1. Template oficial primeiro — a estrutura visual vem do mestre, não de improvisação
2. Identidade Mosten preservada em UI e entregáveis
3. Comercial no centro — fluxo curto: tipo → informações → gerar → baixar
4. Modo Livre acelera narrativa sem redesenhar slides
5. Não inventar fatos de produto, marca ou cliente ausentes das fontes
