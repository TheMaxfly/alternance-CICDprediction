#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WITH_LOCUST=false
LOCUST_LOG="/tmp/briefml-locust.log"

for arg in "$@"; do
  case "$arg" in
    --with-locust)
      WITH_LOCUST=true
      ;;
    *)
      echo "Usage: $0 [--with-locust]"
      exit 1
      ;;
  esac
done

wait_for_url() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"

  for _ in $(seq 1 "$attempts"); do
    if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
      echo "[monitoring] $label ready: $url"
      return 0
    fi
    sleep 2
  done

  echo "[monitoring] Timeout while waiting for $label: $url" >&2
  return 1
}

open_url() {
  local url="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || true
  fi
}

cd "$PROJECT_DIR"

echo "[monitoring] Starting Docker Compose stack..."
docker compose up -d --build

wait_for_url "http://localhost:8000/health" "API"
wait_for_url "http://localhost:8501/_stcore/health" "Streamlit"
wait_for_url "http://localhost:9090/-/ready" "Prometheus"
wait_for_url "http://localhost:9093/-/ready" "Alertmanager"
wait_for_url "http://localhost:3000/api/health" "Grafana"
wait_for_url "http://localhost:3001" "Uptime Kuma"
wait_for_url "http://localhost:5000/health" "MLflow"

if [ "$WITH_LOCUST" = true ]; then
  if command -v uv >/dev/null 2>&1; then
    echo "[monitoring] Starting Locust in background..."
    nohup uv run locust -f locustfile.py --host http://localhost:8000 \
      >"$LOCUST_LOG" 2>&1 &
    wait_for_url "http://localhost:8089" "Locust"
  else
    echo "[monitoring] uv not found, Locust was not started." >&2
  fi
fi

echo "[monitoring] Opening useful URLs..."
open_url "http://localhost:3000"
open_url "http://localhost:9090/targets"
open_url "http://localhost:9090/alerts"
open_url "http://localhost:9093"
open_url "http://localhost:8000/metrics"
open_url "http://localhost:8501"
open_url "http://localhost:3001"
open_url "http://localhost:5000"

if [ "$WITH_LOCUST" = true ]; then
  open_url "http://localhost:8089"
fi

cat <<EOF
[monitoring] Stack is ready.

Useful URLs:
- Grafana:    http://localhost:3000
- Prometheus: http://localhost:9090/targets
- Alerts:     http://localhost:9090/alerts
- Alertmgr:   http://localhost:9093
- API health: http://localhost:8000/health
- API metrics:http://localhost:8000/metrics
- Streamlit:  http://localhost:8501
- UptimeKuma: http://localhost:3001
- MLflow:     http://localhost:5000
EOF

if [ "$WITH_LOCUST" = true ]; then
  cat <<EOF
- Locust:     http://localhost:8089

Locust logs:
- $LOCUST_LOG
EOF
fi
