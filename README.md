# BriefML — Prédiction de Gravité d'Accidents Routiers

Modèle CatBoost (`product15_v2_time_bucket`) exposé via une API FastAPI et une interface Streamlit multi-pages.

## Structure du projet

```
BriefML/
├── briefml/              # Package source principal
│   ├── api/
│   │   └── predictor.py  # API FastAPI (CatBoost)
│   └── ui/
│       ├── app.py        # Entrée Streamlit
│       ├── pages/        # 6 pages de formulaire
│       └── lib/          # Modules partagés (client API, validation, etc.)
├── data/                 # Données CSV + ref_options.json
├── notebooks/            # Notebooks d'exploration/entraînement
├── model/                # Modèle CatBoost (.cbm)
├── artifacts/            # Méta-données du modèle (meta.json)
├── tests/
│   ├── unit/
│   └── integration/
├── docker/               # Dockerfiles
│   ├── Dockerfile        # Multi-stage : api + streamlit
│   └── mlflow.Dockerfile
├── scripts/
│   └── start.py          # Lanceur de développement local
├── docs/                 # Documentation technique
├── docker-compose.yml
└── pyproject.toml
```

## Lancement rapide (développement)

```bash
uv run python scripts/start.py
```

- API : `http://localhost:8000`
- Interface : `http://localhost:8501`

## Lancement séparé

**API FastAPI :**
```bash
uv run uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000 --reload
```

**Interface Streamlit :**
```bash
API_URL=http://localhost:8000 uv run streamlit run briefml/ui/app.py
```

**Vérifier l'API :**
```bash
curl -s http://localhost:8000/health
```

## Docker

```bash
# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (POSTGRES_PASSWORD obligatoire)

# Lancer tous les services
docker-compose up --build

# Build manuel des images
docker build -f docker/Dockerfile --target api -t briefml-api .
docker build -f docker/Dockerfile --target streamlit -t briefml-ui .
```

## Tests

```bash
# Tests unitaires
uv run pytest tests/unit/ -v

# Tests d'intégration (API doit être démarrée)
API_URL=http://localhost:8000 uv run pytest tests/integration/ -v
```

## Données et notebooks (GitHub)

Les fichiers lourds (`.cbm`, `.csv`, `.parquet`, notebooks volumineux) sont gérés via **Git LFS**.

```bash
git lfs install
git lfs pull
git lfs ls-files
```

Voir aussi :
- `data/README.md`
- `notebooks/README.md`

## Variables d'environnement

Voir `.env.example` pour la liste complète. Les variables clés :

| Variable | Défaut | Description |
|---|---|---|
| `MODEL_PATH` | `model/catboost_product15_v2_time_bucket_final.cbm` | Chemin du modèle |
| `META_PATH` | `artifacts/catboost_product15_v2_time_bucket_final_meta.json` | Méta-données |
| `MISSING_CAT` | `__MISSING__` | Token pour les catégorielles manquantes |
| `API_URL` | `http://localhost:8000` | URL de l'API (pour Streamlit) |
| `POSTGRES_PASSWORD` | *(requis)* | Mot de passe PostgreSQL |

## Documentation

- [Dictionnaire de données](docs/data_dictionary.md)
- [Dictionnaire API](docs/api_dictionary.md)
- [CI/CD](docs/ci_cd.md)
