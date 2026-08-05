# Pacote de dados para deploy (Railway/Docker)

Contém:

- `slide-mestre-template.pptx` — template master com seções (CAPA, DOR, OPORTUNIDADE, SOLUÇÃO, …, Professional Service)
- `Modelo-Proposta-Tecnica-v1.0-variaveis.pptx` + `*-slots.json` (legado; não usado pelo modo Livre atual)
- `packages.json` — registry de tipos de proposta
- `packages/*.pptx` — templates standalone opcionais
- `UNS001-26-vigia-valores.json` + `assets/logo-nph.png` (opcionais)

Não versionar os `.pptx` no git (estão no `.gitignore`).

## Modo Livre

Usa o **slide mestre**. A geração:

1. Escaneia tokens nomeados `{TOKEN}` no PPTX (texto cru é ignorado)
2. LLM preenche só essas chaves
3. Copia o mestre, remove a seção Professional Service
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
