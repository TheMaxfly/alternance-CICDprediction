# =============================================================================
# Multi-stage Dockerfile pour BriefML (API FastAPI + Streamlit)
# Utilise uv pour une installation rapide des dependances
# =============================================================================

# --------------- Stage 1: base avec dependances ---------------
FROM python:3.12-slim AS base

# Installer les dependances systeme necessaires pour CatBoost/numpy
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 curl && \
    rm -rf /var/lib/apt/lists/*

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copier les fichiers de dependances en premier (cache Docker)
COPY pyproject.toml ./

# Installer les dependances (sans le projet lui-meme)
RUN uv pip install --system --no-cache -r pyproject.toml

# Copier le code source
COPY briefml/ ./briefml/
COPY scripts/ ./scripts/
COPY model/ ./model/
COPY data/ ./data/
COPY artifacts/ ./artifacts/

# --------------- Stage 2: API FastAPI ---------------
FROM base AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "briefml.api.predictor:app", "--host", "0.0.0.0", "--port", "8000"]

# --------------- Stage 3: Streamlit ---------------
FROM base AS streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["python", "-m", "streamlit", "run", "briefml/ui/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
