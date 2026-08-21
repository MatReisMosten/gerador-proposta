# Plano técnico — Fase 2: FastAPI + React

Status: **implementado** (`api/`, `frontend/`, `Dockerfile.react`), rodando lado a lado com a Fase 1 —
nenhuma das duas foi removida. Uso atual do gerador segue interno (um time comercial); a decisão de
qual casca vira a principal em produção ainda está em aberto. Implementado a pedido explícito antes
do critério de gatilho original (crescimento multi-squad) se confirmar — ver histórico da conversa.

O que existe e foi validado (browser real + Docker real + pytest):
- API completa (`api/`) cobrindo os 3 modos de geração, auth por senha via cookie assinado, download
  efêmero em memória.
- Frontend React (`frontend/`) com o wizard completo nos moldes do Streamlit, tokens de marca Mosten
  em CSS de verdade (sem hackear DOM de outro framework).
- `Dockerfile.react`: build multi-stage único, testado localmente (`docker build` + `docker run` +
  geração real dentro do container).
- Dois bugs da Fase 1 encontrados e corrigidos nesta camada (não retroportados ao Streamlit sem
  pedido): Escopo Fechado excluía a própria seção em vez de isolá-la; token `{LOGO_CLIENTE}` vazava
  como texto literal quando nenhum logo era resolvido.

O que falta para considerar isto "pronto para substituir a Fase 1" (não feito ainda):
- Decisão de negócio: qual stack fica em produção.
- Deploy real no Railway (só testado local + Docker local).
- `escopo_fechado`/`livre` sem cobertura de teste com chamada real ao LLM (os testes automatizados
  usam `fill_slots` mockado — só o modo `package` foi validado com chamada real ao OpenAI, manualmente).

## Objetivo

Trocar a camada de interface (Streamlit) por React, mantendo `generator/` e `proposal_library/` como estão — essas pastas já não importam Streamlit e contêm a lógica de negócio real (parametrização de PPTX, scanner de tokens, chamada ao LLM). Não é reescrita de produto, é troca de casca.

## Contrato de API (FastAPI)

| Método | Rota | Equivalente hoje | Observação |
|---|---|---|---|
| GET | `/api/proposal-types` | `list_proposal_types()` | Lista tipos + campos de `data/packages.json` |
| GET | `/api/templates/summary` | `_template_summary()` | Seções e tokens do slide mestre |
| POST | `/api/proposals/package` | `_run_package_generation` | multipart: `type_id`, campos do pacote, `client_name`, `project_code`, `logo` (arquivo opcional) |
| POST | `/api/proposals/livre` | `_run_livre_generation` | multipart: `brief`, `transcription`, `estimate`, `client_name`, `project_code`, `logo` |
| GET | `/api/proposals/{id}/download` | `st.download_button` | Stream do `.pptx` gerado |
| POST | `/api/auth/login` | `gate_password()` | Substitui o gate por sessão (cookie assinado ou JWT curto) |

As duas rotas de POST devolvem o binário do PPTX direto na resposta (streaming), não um ID persistido — ver decisão de storage abaixo.

## Decisão: não persistir histórico compartilhado em disco

Hoje `render_historico`/`render_geradas` leem `data/geradas/*.pptx` e `*.values.json` do disco — qualquer usuário do app vê o histórico de geração de todo mundo, e múltiplas instâncias/restarts do Railway não compartilham disco de forma confiável.

Recomendação para a Fase 2: gerar e devolver o arquivo na resposta HTTP, sem persistir no servidor. Isso é consistente com o texto que o próprio app já mostra ao usuário ("seus dados são utilizados apenas para gerar a proposta e não são armazenados" — `FOOTER_NOTE` em `ui/components.py`). Se "Propostas geradas"/"Histórico" precisarem sobreviver a um reload de página, usar `localStorage` no navegador (client-side, por usuário) em vez de storage compartilhado no servidor.

## Deploy — um serviço, não dois

Manter FastAPI servindo tanto a API quanto os arquivos estáticos do build do React (`StaticFiles`) num único container Railway. Evita CORS, evita gerenciar dois serviços/domínios, mantém o modelo de deploy atual (`railway up`, uma URL, um `APP_PASSWORD`/sessão).

```dockerfile
# build stage: node -> vite build -> frontend/dist
# runtime stage: python -> fastapi serve api/ + arquivos estáticos de frontend/dist
```

## Passo a passo incremental (sem big-bang)

1. **API isolada, sem tocar no Streamlit.** Criar `api/` com FastAPI expondo as rotas acima, chamando `generator/` diretamente. Testar via `curl`/Postman. `app.py` (Streamlit) continua rodando em paralelo — zero risco para quem usa hoje.
2. **Scaffold do React** em `frontend/` (Vite + TypeScript). Reproduzir o wizard (Tipo → Informações → Gerar) usando os tokens de marca Mosten (`#612CB5`, Inter Tight) como design tokens reais (Tailwind config ou CSS variables), não como overrides de CSS mirando DOM interno de outro framework.
3. **Integrar** o React local contra a API local; validar o fluxo completo ponta a ponta (os 7 tipos de proposta).
4. **Dockerfile novo** com build do React + FastAPI servindo estático; ajustar variáveis Railway.
5. **Cutover**: trocar a imagem do serviço Railway; manter o Dockerfile do Streamlit como rollback por um ciclo de release.
6. **Descomissionar** `app.py`, `ui/`, `pages/`, `generation/` (a camada Streamlit) só depois de validar o React em produção por alguns dias.

## O que muda de verdade (riscos a não subestimar)

- **Toolchain**: entra Node.js no projeto (hoje é 100% Python). Precisa decidir onde isso roda no CI/deploy.
- **Upload de arquivo**: o uploader nativo do Streamlit vira `multipart/form-data` + dropzone customizado no React — reimplementar UX de drag-and-drop do zero.
- **Autenticação**: `APP_PASSWORD` único vira sessão real (cookie/JWT). Ainda pode ser senha única compartilhada se o uso continuar interno — não precisa de SSO agora.
- **Espera do LLM**: a geração do modo Livre chama o LLM (segundos, não long-running) — um `fetch` bloqueante com spinner no React resolve; não precisa de fila de jobs/websocket.
- **Estimativa**: 1,5–3 semanas de uma pessoa (API ~2-3 dias; paridade de UI em React ~1-1,5 semana; deploy/cutover ~2-3 dias). Não é troca de tarde.

## O que NÃO muda

`generator/engine.py`, `generator/llm.py`, `generator/packages.py`, `generator/paths.py`, `proposal_library/*` — motor de geração de PPTX e prompt do LLM ficam intactos. A Fase 2 é só uma nova porta de entrada para esse motor.
