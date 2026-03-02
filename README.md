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
├── monitoring/           # Configuration monitoring + dashboard Grafana
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── scripts/
│   ├── start.py                # Lanceur de developpement local
│   ├── start_monitoring.sh     # Lanceur stack monitoring + URLs utiles
│   └── export_mlflow_models.py # Export des modeles depuis MLflow
├── docs/                 # Documentation technique
├── DASHBOARD_DESIGN.md   # Justification du dashboard Grafana
├── docker-compose.yml
├── locustfile.py         # Scenario Locust pour /predict
├── stresstest.md         # Rapport de stress test
├── start_mlflow.sh       # Lanceur MLflow local
├── .env.example          # Variables attendues pour Docker Compose
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

La stack Docker Compose integre desormais :

- API FastAPI
- Streamlit
- MLflow
- PostgreSQL
- Prometheus
- Grafana
- node-exporter
- cAdvisor

### Lancement

```bash
# Configurer les variables d'environnement
cp .env.example .env
# Editer .env (POSTGRES_PASSWORD obligatoire)

# Lancer toute la stack (app + monitoring)
docker compose up --build
```

Lanceur pratique (demarre la stack, attend les endpoints et ouvre les interfaces) :

```bash
./scripts/start_monitoring.sh
```

Avec Locust :

```bash
./scripts/start_monitoring.sh --with-locust
```

Services exposes :
- API FastAPI : `http://localhost:8000`
- Metrics Prometheus (API) : `http://localhost:8000/metrics`
- Streamlit : `http://localhost:8501`
- MLflow UI : `http://localhost:5000`
- Prometheus : `http://localhost:9090`
- Grafana : `http://localhost:3000`
- node-exporter : `http://localhost:9100`
- cAdvisor : `http://localhost:8080`
- PostgreSQL (conteneur) : `localhost:5433`

### Choisir le modele

Par defaut l'API charge le modele original. Pour utiliser un autre modele,
passer la variable `MODEL_NAME` :

```bash
# Modele Optuna
MODEL_NAME=catboost_optuna_best docker compose up --build

# Modele Hyperopt
MODEL_NAME=catboost_hyperopt_best docker compose up --build
```

### Test du workflow complet

```bash
# 1. Lancer les services
docker compose up --build -d

# 2. Verifier que tout est healthy
docker compose ps

# 3. Tester MLflow
curl -s http://localhost:5000/health

# 4. Tester l'API (affiche modele + threshold)
curl -s http://localhost:8000/health | python3 -m json.tool

# 5. Tester le endpoint /metrics
curl -s http://localhost:8000/metrics | rg "prediction_|app_uptime_seconds"

# 6. Tester une prediction
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data":{"dep":"75","lum":"1","atm":"1","catr":"3","agg":"1","int":"1","circ":"2","col":"6","vma_bucket":"50","catv_family_4":"car","manv_mode":"straight","driver_age_bucket":"25-34","choc_mode":"front","driver_trajet_family":"commute","time_bucket":"morning_rush"}}' \
  | python3 -m json.tool

# 7. Verifier les targets Prometheus
# http://localhost:9090/targets

# 8. Ouvrir Grafana
# http://localhost:3000

# 9. Arreter
docker compose down
```

### Volumes persistants

| Volume | Contenu | Persistence |
|---|---|---|
| `pgdata` | Base PostgreSQL (metriques, params MLflow) | Survit aux `docker-compose down` |
| `mlflow_artifacts` | Modeles logges, graphiques, CSV | Survit aux `docker-compose down` |
| `prometheus_data` | Historique des series temporelles Prometheus | Survit aux `docker-compose down` |
| `grafana_data` | Dashboards, datasources, preferences Grafana | Survit aux `docker-compose down` |

Pour supprimer les volumes (reset complet) :
```bash
docker compose down -v
```

### Build manuel

```bash
docker build -f docker/Dockerfile --target api -t briefml-api .
docker build -f docker/Dockerfile --target streamlit -t briefml-ui .
docker build -f docker/mlflow.Dockerfile -t briefml-mlflow .
```

## Monitoring et Observabilite

L'API expose des metriques Prometheus via `prometheus_client` sur :

- `GET /metrics`

Metriques custom principales :

- `prediction_requests_total`
- `prediction_results_total{label="grave|non_grave"}`
- `prediction_request_duration_seconds`
- `prediction_validation_errors_total`
- `prediction_http_errors_total{status_code="..."}`
- `app_uptime_seconds`

Prometheus scrape 4 jobs :

- `fastapi`
- `node-exporter`
- `cadvisor`
- `prometheus`

Le dashboard Grafana versionne dans le repo se trouve ici :

- `monitoring/grafana-dashboard.json`

Le document de conception associe est :

- `DASHBOARD_DESIGN.md`

## Stress testing (Locust)

Le scenario de test de charge est fourni dans :

- `locustfile.py`

Lancement manuel :

```bash
uv run locust -f locustfile.py --host http://localhost:8000
```

Interface web :

- `http://localhost:8089`

Le rapport de test de charge se trouve dans :

- `stresstest.md`

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
| `MODEL_NAME` | `catboost_product15_v2_time_bucket_final` | Nom du modele (Docker : construit MODEL_PATH et META_PATH) |
| `MODEL_PATH` | `model/{MODEL_NAME}.cbm` | Chemin du modele .cbm |
| `META_PATH` | `artifacts/{MODEL_NAME}_meta.json` | Meta-donnees (threshold, features) |
| `MISSING_CAT` | `__MISSING__` | Token pour les categorielles manquantes |
| `API_URL` | `http://localhost:8000` | URL de l'API (pour Streamlit) |
| `MLFLOW_TRACKING_URI` | `http://mlflow:5000` | URL MLflow (Docker, interne) |
| `POSTGRES_USER` | `briefml` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | *(requis)* | Mot de passe PostgreSQL |
| `POSTGRES_DB` | `mlflow` | Base PostgreSQL utilisee par MLflow |
| `GRAFANA_ADMIN_USER` | `admin` | Utilisateur admin Grafana |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Mot de passe admin Grafana |

## CI/CD (GitHub Actions)

6 workflows automatises + 1 workflow de deploiement de modele :

| Workflow | Declencheur | Description |
|---|---|---|
| `ci.yml` | Push/PR sur develop | Lint (Ruff), types (Pyright), securite (Bandit), tests + coverage |
| `build.yml` | Push sur develop/main | Build et push des images Docker vers GHCR |
| `release.yml` | Apres CI sur main | Semantic versioning automatique |
| `cd-azure.yml` | Release ou manuel | Deploiement sur Azure Container Apps |
| `deploy-model.yml` | Manuel | Deployer un modele specifique (original/optuna/hyperopt) |
| `docs.yml` | Push sur main | Build et deploy de la documentation MkDocs |
| `sync-develop.yml` | Tag de release | Sync main → develop apres release |

### Deployer un modele en production

Le workflow `deploy-model.yml` permet de changer de modele sans modifier le code :

1. Aller dans **Actions > Deploy Model > Run workflow**
2. Choisir le modele : `catboost_optuna_best`, `catboost_hyperopt_best`, ou l'original
3. Choisir l'environnement : `production` ou `staging`
4. Le workflow valide les fichiers, rebuild l'image et deploie

## Documentation

- [readme_mlflow.md](readme_mlflow.md) — Guide MLflow (tracking, export, chargement)
- [Dictionnaire de donnees](docs/data_dictionary.md)
- [Dictionnaire API](docs/api_dictionary.md)
- [CI/CD](docs/ci_cd.md)
