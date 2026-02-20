# =============================================================================
# Dockerfile pour MLflow Tracking Server
# Backend: PostgreSQL | Artifacts: stockage local
# =============================================================================

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir mlflow[extras]==2.21.* psycopg2-binary

EXPOSE 5000

CMD mlflow server \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --default-artifact-root /mlflow/artifacts \
    --host 0.0.0.0 \
    --port 5000
