# Gerador de Propostas Mosten

Projeto standalone. O LLM preenche textos; o Python monta o PPTX a partir do Modelo-Proposta Técnica.

Duas cascas de UI convivem hoje sobre o mesmo motor (`generator/`, `proposal_library/`):

- **Fase 1 — Streamlit** (`app.py`): a que está em uso. Setup abaixo.
- **Fase 2 — FastAPI + React** (`api/`, `frontend/`): casca nova, já funcional, ainda não decidida como
  substituta. Ver seção "Fase 2" mais abaixo e `docs/plano-migracao-react.md` para o racional completo.

## Setup local (Fase 1 — Streamlit)

```bash
cd gerador-proposta/gerador-proposta   # pasta deste README
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Chave de LLM: copie `.env.example` para `.env` e defina `OPENAI_API_KEY`. Provider e modelo são fixos no código (OpenAI `gpt-4.1-mini`) — não há seletor de provider na UI.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Cobertura atual: funções puras de `generator/engine.py` (classificação de papel de texto, validação de tokens `{NOME}`, scanner de tokens em `.pptx`). Lógica de montagem completa do PPTX (fluxo end-to-end) ainda não tem teste automatizado — validar manualmente ao mexer em `generator/engine.py` ou `generator/packages.py`.

## Deploy Railway (sem GitHub)

```bash
brew install railway   # ou: npm i -g @railway/cli

cd gerador-proposta/gerador-proposta   # pasta deste README
# data/ já vem empacotado (~42MB). Se atualizar o modelo no vault:
#   ./prepare_deploy.sh   # só funciona se o vault Mosten estiver no caminho esperado

railway login
railway init
railway up
railway domain
railway variables set APP_PASSWORD='sua-senha'
```

## Estrutura

```
gerador-proposta/
  app.py                 # entrypoint fino: setup, gate de senha, main()
  ui/
    styles.py            # CSS + variáveis de tema (claro/escuro)
    icons.py              # ícones SVG inline
    formatting.py         # validação/formatação de campos (código, moeda, meses)
    components.py         # componentes reutilizáveis (cards, wizard stepper, loading overlay)
  generation/
    flow.py               # orquestração de geração (package e livre), download, persistência
  screens/
    generator_page.py     # página principal (wizard Tipo → Informações → Gerar)
    other_pages.py         # Propostas geradas / Templates / Histórico / Configurações
  generator/              # engine PPTX + LLM (lógica de negócio, sem Streamlit)
  proposal_library/        # helpers de slide (vendored)
  tests/                   # pytest — generator/engine.py
  data/                    # modelo + slots (obrigatório no cloud)
  Dockerfile / railway.json
```

`generator/` e `proposal_library/` não importam Streamlit — é a camada que uma futura migração de frontend (ver `docs/plano-migracao-react.md`) reaproveitaria por trás de uma API.

## Fase 2 (FastAPI + React)

Casca alternativa sobre o mesmo `generator/`. Contrato completo e decisões de design em
`docs/plano-migracao-react.md`. Resumo do que muda vs. Fase 1:

- Sem persistência em disco: o PPTX gerado fica em memória (TTL de 10min) até o download; sem
  `data/geradas/` compartilhado entre usuários.
- Corrige dois bugs encontrados na Fase 1 durante a construção desta API (ver `api/service.py`):
  Escopo Fechado agora isola a própria seção do template em vez de excluí-la, e o token
  `{LOGO_CLIENTE}` é limpo quando nenhum logo é resolvido, em vez de vazar como texto literal no slide.

### Rodar em dev (dois processos)

```bash
# terminal 1 — API
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# terminal 2 — frontend (proxy /api -> :8000, ver frontend/vite.config.ts)
cd frontend
npm install
npm run dev
```

### Rodar em produção (um serviço só)

```bash
docker build -f Dockerfile.react -t gerador-proposta-react .
docker run -p 8000:8000 --env-file .env gerador-proposta-react
```

`npm run build` manda o build do React para `frontend_dist/` (fora de `frontend/` — ver
`frontend/vite.config.ts`); `api/main.py` serve esse diretório estático no mesmo processo/porta
da API, sem CORS.

### Testes

Cobertos em `tests/test_api.py` (contrato de todos os endpoints, os 3 modos de geração, e os dois
bugs acima como regressão) — já incluídos no `pytest` da seção Testes acima.

## Segurança

- Chave OpenAI vem de `OPENAI_API_KEY` no `.env` do servidor — não fica em sessão de usuário nem em código.
- Em URL pública, use `APP_PASSWORD` (senha única compartilhada, sem isolamento por usuário). Na
  Fase 2 isso vira um cookie de sessão assinado (`api/session.py`) em vez de checagem por rerun.
