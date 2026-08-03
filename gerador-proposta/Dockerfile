# Streamlit proposal generator — Railway / Docker
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501 \
    PROPOSAL_DATA_DIR=/app/data \
    PROPOSAL_OUTPUT_DIR=/tmp/geradas \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY generator/ ./generator/
COPY proposal_library/ ./proposal_library/
COPY .streamlit/ ./.streamlit/
COPY data/ ./data/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')" || exit 1

CMD streamlit run app.py \
  --server.port=${PORT} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
