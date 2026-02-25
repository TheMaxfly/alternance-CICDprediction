# Guide de démarrage

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets)
- Docker (optionnel)

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/TheMaxfly/alternance-CICDprediction.git
cd alternance-CICDprediction

# Installer les dépendances
uv sync --all-groups

# Installer les pre-commit hooks
uv run pre-commit install
```

## Lancer l'application

### Mode développement (API + UI)

```bash
uv run python scripts/start.py
```

- API disponible sur : `http://localhost:8000`
- UI Streamlit sur : `http://localhost:8501`
- Documentation API : `http://localhost:8000/docs`

### Séparément

```bash
# API seule
uvicorn briefml.api.predictor:app --port 8000 --reload

# UI seule
streamlit run briefml/ui/app.py
```

## Via Docker

```bash
# Construire et lancer l'API
docker build -f docker/Dockerfile --target api -t briefml-api .
docker run -p 8000:8000 briefml-api

# Construire et lancer l'UI
docker build -f docker/Dockerfile --target streamlit -t briefml-ui .
docker run -p 8501:8501 briefml-ui
```

## Lancer les tests

```bash
uv run pytest tests/unit/ -v
```

## Variables d'environnement

| Variable | Valeur par défaut | Description |
|---|---|---|
| `API_URL` | `http://localhost:8000` | URL de l'API FastAPI |
