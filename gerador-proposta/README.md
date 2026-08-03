# Gerador de Propostas Mosten

Projeto standalone (Streamlit). O LLM preenche textos; o Python monta o PPTX a partir do Modelo-Proposta Técnica.

## Setup local

```bash
cd /Users/matheusreis/Documents/gerador-proposta
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy Railway (sem GitHub)

```bash
brew install railway   # ou: npm i -g @railway/cli

cd /Users/matheusreis/Documents/gerador-proposta
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
  app.py
  Dockerfile / railway.json
  data/                 # modelo + slots (obrigatório no cloud)
  generator/            # engine PPTX + LLM
  proposal_library/     # helpers de slide (vendored)
```

## Segurança

- API key fica só na sessão do Streamlit.
- Em URL pública, use `APP_PASSWORD`.
