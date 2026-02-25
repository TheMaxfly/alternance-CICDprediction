# BriefML — Prediction de Gravite d'Accidents Routiers

Modele CatBoost (`product15_v2_time_bucket`) expose via une API FastAPI et une interface Streamlit multi-pages.
Trois variantes de modeles sont disponibles, optimisees avec Optuna et Hyperopt.

## Structure du projet

```
BriefML/
├── briefml/              # Package source principal
│   ├── api/
│   │   └── predictor.py  # API FastAPI (CatBoost)
│   └── ui/
│       ├── app.py        # Entree Streamlit
│       ├── pages/        # 6 pages de formulaire
│       └── lib/          # Modules partages (client API, validation, etc.)
├── data/                 # Donnees CSV + ref_options.json
├── notebooks/            # Notebooks d'exploration/entrainement
├── model/                # Modeles CatBoost (.cbm)
├── artifacts/            # Meta-donnees des modeles (meta.json)
├── mlartifacts/          # Artifacts MLflow (modeles logges)
├── tests/
│   ├── unit/
│   └── integration/
├── docker/               # Dockerfiles
│   ├── Dockerfile        # Multi-stage : api + streamlit
│   └── mlflow.Dockerfile
├── scripts/
│   ├── start.py                # Lanceur de developpement local
│   └── export_mlflow_models.py # Export des modeles depuis MLflow
├── docs/                 # Documentation technique
├── docker-compose.yml
├── start_mlflow.sh       # Lanceur MLflow local
└── pyproject.toml
```

## Modeles disponibles

Trois modeles CatBoost sont disponibles, chacun avec son fichier `.cbm` et son `_meta.json` :

| Modele | Fichier .cbm | Optimisation | Threshold | PR AUC | Recall | Precision |
|---|---|---|---|---|---|---|
| **Original** | `catboost_product15_v2_time_bucket_final.cbm` | Optuna (equilibre) | 0.47 | — | — | — |
| **Optuna recall** | `catboost_optuna_best.cbm` | Optuna 30 trials, F-beta(2) | 0.304 | 0.7147 | 0.9201 | 0.4948 |
| **Hyperopt recall** | `catboost_hyperopt_best.cbm` | Hyperopt TPE 30 trials, F-beta(2) | 0.160 | 0.7154 | 0.9223 | 0.4904 |

- **Original** : modele de base, seuil equilibre precision/recall
- **Optuna recall** : optimise pour maximiser le recall (ne rater aucun accident grave), seuil F-beta(2), precision >= 0.30
- **Hyperopt recall** : meme objectif avec Hyperopt (TPE bayesien), seuil plus bas, recall legerement superieur

Les notebooks d'entrainement :
- `notebooks/11catboost_check_time_columns.ipynb` — modele original
- `notebooks/11c_catboost_optuna_recall_mlflow.ipynb` — Optuna
- `notebooks/11d_catboost_hyperopt_recall_mlflow.ipynb` — Hyperopt

## Lancement rapide (developpement)

```bash
# Lance API + Streamlit ensemble (modele par defaut : original)
uv run python scripts/start.py
```

- API : `http://localhost:8000`
- Interface : `http://localhost:8501`

## Lancement avec choix du modele

L'API charge le modele et le threshold via les variables `MODEL_PATH` et `META_PATH`.

**Modele original (par defaut) :**
```bash
uv run uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000 --reload
```

**Modele Optuna (recall optimise) :**
```bash
MODEL_PATH=model/catboost_optuna_best.cbm \
META_PATH=artifacts/catboost_optuna_best_meta.json \
uv run uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000 --reload
```

**Modele Hyperopt (recall optimise) :**
```bash
MODEL_PATH=model/catboost_hyperopt_best.cbm \
META_PATH=artifacts/catboost_hyperopt_best_meta.json \
uv run uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000 --reload
```

**Interface Streamlit :**
```bash
API_URL=http://localhost:8000 uv run streamlit run briefml/ui/app.py
```

**Verifier l'API (affiche le modele charge et son threshold) :**
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

## Export des modeles depuis MLflow

Si les fichiers `.cbm` ne sont pas presents localement, ils peuvent etre extraits depuis MLflow :

```bash
# Prerequis : MLflow doit tourner (voir readme_mlflow.md)
./start_mlflow.sh

# Exporter les modeles Optuna et Hyperopt depuis MLflow
uv run python scripts/export_mlflow_models.py
```

Voir [readme_mlflow.md](readme_mlflow.md) pour le guide complet MLflow.

## Docker

```bash
# Configurer les variables d'environnement
cp .env.example .env
# Editer .env (POSTGRES_PASSWORD obligatoire)

# Lancer tous les services (API + Streamlit + MLflow + PostgreSQL)
docker-compose up --build

# Build manuel des images
docker build -f docker/Dockerfile --target api -t briefml-api .
docker build -f docker/Dockerfile --target streamlit -t briefml-ui .
```

Pour changer de modele en Docker, modifier les variables dans `docker-compose.yml` :
```yaml
api:
  environment:
    MODEL_PATH: /app/model/catboost_optuna_best.cbm
    META_PATH: /app/artifacts/catboost_optuna_best_meta.json
```

## Tests

```bash
# Tests unitaires
uv run pytest tests/unit/ -v

# Tests d'integration (API doit etre demarree)
API_URL=http://localhost:8000 uv run pytest tests/integration/ -v
```

## Donnees et notebooks (GitHub)

Les fichiers lourds (`.cbm`, `.csv`, `.parquet`, notebooks volumineux) sont geres via **Git LFS**.

```bash
git lfs install
git lfs pull
git lfs ls-files
```

Voir aussi :
- `data/README.md`
- `notebooks/README.md`

## Variables d'environnement

Voir `.env.example` pour la liste complete. Les variables cles :

| Variable | Defaut | Description |
|---|---|---|
| `MODEL_PATH` | `model/catboost_product15_v2_time_bucket_final.cbm` | Chemin du modele .cbm |
| `META_PATH` | `artifacts/catboost_product15_v2_time_bucket_final_meta.json` | Meta-donnees (threshold, features) |
| `MISSING_CAT` | `__MISSING__` | Token pour les categorielles manquantes |
| `API_URL` | `http://localhost:8000` | URL de l'API (pour Streamlit) |
| `POSTGRES_PASSWORD` | *(requis)* | Mot de passe PostgreSQL |

## Documentation

- [readme_mlflow.md](readme_mlflow.md) — Guide MLflow (tracking, export, chargement)
- [Dictionnaire de donnees](docs/data_dictionary.md)
- [Dictionnaire API](docs/api_dictionary.md)
- [CI/CD](docs/ci_cd.md)
