# Pacote de dados para deploy (Railway/Docker)

Contém:

- `slide-mestre-template.pptx` — template master com seções (CAPA, DOR, OPORTUNIDADE, SOLUÇÃO, …, Professional Service, SUPORTE, CONTROLE DE ACESSO (PASSLOG), DISCOVERY, CLARION)
- `Modelo-Proposta-Tecnica-v1.0-variaveis.pptx` + `*-slots.json` (legado; não usado pelo modo Livre atual)
- `packages.json` — registry de tipos de proposta
- `packages/*.pptx` — templates standalone opcionais
- `UNS001-26-vigia-valores.json` + `assets/logo-nph.png` (opcionais)

Não versionar os `.pptx` no git (estão no `.gitignore`).

## Modo Livre

Usa o **slide mestre**. A geração:

1. Escaneia tokens nomeados `{TOKEN}` no PPTX (texto cru é ignorado)
2. LLM preenche só essas chaves
3. Copia o mestre, remove as seções de pacote (Professional Service, SUPORTE, PassLog, Discovery, Clarion)
4. Substitui apenas `{TOKEN}`; rótulos/footers fixos permanecem
5. Aplica logo do cliente quando houver `{LOGO_CLIENTE}`

Novos tokens no PowerPoint entram no catálogo automaticamente no próximo run.

## Professional Service

Usa a seção **Professional Service** do slide mestre. A geração:

1. Copia o master
2. Mantém só os slides dessa seção (proposta isolada)
3. Substitui apenas tokens `{...}` (ex.: `{COD_CLIENTE}`, `{DATA_ATUAL}`)
4. Preenche células vazias da tabela "Modelo de Investimento"
5. Não altera textos brutos do template

## Suporte

Usa a seção **SUPORTE** do slide mestre. A geração:

1. Copia o master
2. Mantém só os slides dessa seção (proposta isolada)
3. Substitui `{COD_PROJETO}`, `{NOME_CLIENTE}`, `{VALOR}`, `{TEMPO_CONTRATO}`, `{DATA}`
4. Não altera textos fixos do template (SLA, canais, condições etc.)

## Controle de Acesso (PassLog)

Usa a seção **CONTROLE DE ACESSO (PASSLOG)** do slide mestre. A geração:

1. Copia o master
2. Mantém só os slides dessa seção (proposta isolada)
3. Substitui `{COD_PROJETO}`, `{DATA}`, `{NOME_CLIENTE}`, `{VALOR}`, `{DESAFIO_1_CLIENTE}`, `{DESAFIO_2_CLIENTE}`
4. Aplica logo quando houver `{LOGO_CLIENTE}`
5. Campos na UI: logo, cliente, código, preço, dor do cliente e brief/contexto (MD/TXT)

## Discovery

Usa a seção **DISCOVERY** do slide mestre. A geração:

1. Copia o master
2. Mantém só os slides dessa seção (proposta isolada)
3. Substitui `{COD_PROJETO}`, `{DATA}`, `{NOME_CLIENTE}`, `{VALOR}`, `{DESCRICAO_1_DOR}`, `{DESCRICAO_2_DOR}`
4. Aplica logo quando houver `{LOGO_CLIENTE}`
5. Campos na UI: logo, cliente, código, preço, dor do cliente e brief/contexto (MD/TXT)

## Clarion

Usa a seção **CLARION** do slide mestre. A geração:

1. Copia o master
2. Mantém só os slides dessa seção (deck de produto estático)
3. Sem formulário de informações — o wizard pula direto do tipo para gerar
