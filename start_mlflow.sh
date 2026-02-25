#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
(sleep 2 && xdg-open http://127.0.0.1:5000) &
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
