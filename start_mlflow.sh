#!/bin/bash
cd "$(dirname "$0")"
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
