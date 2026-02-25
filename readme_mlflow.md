# Guide MLflow — BriefML

MLflow est utilise pour tracker les experiences d'optimisation des hyperparametres
(Optuna, Hyperopt) et stocker les modeles CatBoost.

## Architecture

```
MLflow Server (http://127.0.0.1:5000)
├── Backend store : sqlite:///mlflow.db  (metriques, params, tags)
└── Artifact store : ./mlartifacts/      (modeles, graphiques, CSV)

Experiences enregistrees :
├── optuna-catboost-recall   (experiment 3)  — Optuna 30 trials
└── hyperopt-catboost-recall (experiment 4)  — Hyperopt 30 trials
```

## 1. Lancer le serveur MLflow

### En local (developpement)

```bash
# Option 1 : script fourni
./start_mlflow.sh

# Option 2 : commande directe
mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db
```

L'UI est accessible sur `http://127.0.0.1:5000`.

### Avec Docker Compose

```bash
docker-compose up mlflow postgres
```

MLflow utilise alors PostgreSQL comme backend store (plus robuste).

## 2. Enregistrer un modele dans MLflow (depuis un notebook)

### Etape 1 — Se connecter

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("mon-experience")
```

### Etape 2 — Logger un run (parametres + metriques + modele)

```python
import mlflow.catboost
from catboost import CatBoostClassifier

model = CatBoostClassifier(depth=6, learning_rate=0.027, ...)
model.fit(X_train, y_train, cat_features=cat_cols, eval_set=(X_valid, y_valid))

with mlflow.start_run(run_name="mon_modele"):
    # Hyperparametres
    mlflow.log_param("depth", 6)
    mlflow.log_param("learning_rate", 0.027)

    # Metriques
    mlflow.log_metric("pr_auc", 0.7147)
    mlflow.log_metric("recall", 0.9201)
    mlflow.log_metric("threshold", 0.304)

    # Modele complet
    mlflow.catboost.log_model(model, artifact_path="model")

    # Artifacts supplementaires (graphiques, CSV, etc.)
    mlflow.log_artifact("confusion_matrix.png")
```

Apres execution, le run apparait dans l'UI MLflow avec :
- Les parametres dans l'onglet "Parameters"
- Les metriques dans l'onglet "Metrics"
- Le modele et les fichiers dans l'onglet "Artifacts"

### Etape 3 — Recuperer le run_id

Le run_id est affiche dans la sortie :
```
View run mon_modele at: http://127.0.0.1:5000/#/experiments/3/runs/f66bc2e7987d...
```

Le run_id ici est `f66bc2e7987d...`. Il est aussi visible dans l'UI MLflow.

## 3. Charger un modele depuis MLflow

### Par run_id (methode directe)

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

run_id = "f66bc2e7987d4740bcfe6b03f1986662"
model = mlflow.catboost.load_model(f"runs:/{run_id}/model")

# model est un CatBoostClassifier pret a predire
proba = model.predict_proba(X_new)[:, 1]
```

### En cherchant le meilleur run automatiquement

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Trouver le meilleur run par PR AUC
runs = mlflow.search_runs(
    experiment_ids=["3"],
    order_by=["metrics.pr_auc DESC"],
    max_results=1,
)
run_id = runs.iloc[0]["run_id"]
print(f"Meilleur run : {run_id}")
print(f"PR AUC : {runs.iloc[0]['metrics.pr_auc']:.4f}")

model = mlflow.catboost.load_model(f"runs:/{run_id}/model")
```

### Recuperer les metriques et parametres d'un run

```python
client = mlflow.MlflowClient()
run = client.get_run(run_id)

# Metriques (dict)
metrics = run.data.metrics
print(f"Recall    : {metrics['recall']:.4f}")
print(f"Threshold : {metrics['threshold']:.4f}")

# Parametres (dict, valeurs en string)
params = run.data.params
print(f"Depth : {params['depth']}")
```

## 4. Exporter un modele en .cbm pour l'API

### Methode 1 — Script automatique

```bash
# Exporte les modeles Optuna et Hyperopt en .cbm + meta.json
uv run python scripts/export_mlflow_models.py
```

Fichiers generes :
- `model/catboost_optuna_best.cbm`
- `model/catboost_hyperopt_best.cbm`
- `artifacts/catboost_optuna_best_meta.json`
- `artifacts/catboost_hyperopt_best_meta.json`

### Methode 2 — Manuellement en Python

```python
import json
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Charger depuis MLflow
run_id = "f66bc2e7987d4740bcfe6b03f1986662"
model = mlflow.catboost.load_model(f"runs:/{run_id}/model")

# Sauvegarder en .cbm
model.save_model("model/catboost_optuna_best.cbm")

# Generer le meta.json (requis par predictor.py)
client = mlflow.MlflowClient()
run = client.get_run(run_id)

meta = {
    "model_name": "catboost_optuna_best",
    "threshold": run.data.metrics["threshold"],
    "features": [
        "dep", "lum", "atm", "catr", "agg", "int", "circ", "col",
        "vma_bucket", "catv_family_4", "manv_mode", "driver_age_bucket",
        "choc_mode", "driver_trajet_family", "time_bucket",
    ],
    "cat_features": [
        "dep", "lum", "atm", "catr", "agg", "int", "circ", "col",
        "vma_bucket", "catv_family_4", "manv_mode", "driver_age_bucket",
        "choc_mode", "driver_trajet_family", "time_bucket",
    ],
}
with open("artifacts/catboost_optuna_best_meta.json", "w") as f:
    json.dump(meta, f, indent=2)
```

### Methode 3 — Depuis les cellules d'export dans les notebooks

Les notebooks 11c (Optuna) et 11d (Hyperopt) contiennent une cellule
"Export .cbm + meta.json" qui charge le modele depuis MLflow et l'exporte.
Il suffit d'executer cette cellule (le serveur MLflow doit tourner).

## 5. Utiliser le modele exporte dans l'API

```bash
# Lancer l'API avec le modele Optuna
MODEL_PATH=model/catboost_optuna_best.cbm \
META_PATH=artifacts/catboost_optuna_best_meta.json \
uv run uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000

# Verifier quel modele est charge
curl -s http://localhost:8000/health | python3 -m json.tool
# → {"status": "ok", "model_name": "catboost_optuna_best", "threshold": 0.304, ...}
```

## 6. Runs MLflow existants

| Experience | Run name | Run ID | Modele |
|---|---|---|---|
| `optuna-catboost-recall` (exp 3) | `optuna_best_recall_catboost` | `f66bc2e7987d4740bcfe6b03f1986662` | Optuna 30 trials |
| `hyperopt-catboost-recall` (exp 4) | `hyperopt_best_recall_catboost` | `efe13ed7d0054e3ca33e57eb799ec919` | Hyperopt 30 trials |

## 7. Commandes utiles

```bash
# Lancer MLflow
./start_mlflow.sh

# Lister les experiences
mlflow experiments search --view-type ALL

# Lister les runs d'une experience
mlflow runs list --experiment-id 3

# Exporter les modeles
uv run python scripts/export_mlflow_models.py

# UI MLflow
# http://127.0.0.1:5000
```

## Schema recapitulatif

```
Notebook (entrainement)
    │
    ├── mlflow.catboost.log_model(model)
    │         │
    │         ▼
    │   MLflow Server (http://127.0.0.1:5000)
    │     run_id: f66bc2e7...
    │     ├── metrics: {pr_auc, recall, threshold, ...}
    │     ├── params:  {depth, learning_rate, ...}
    │     └── artifacts/model/  (fichiers du modele)
    │
    │
Export (.cbm + meta.json)
    │   scripts/export_mlflow_models.py
    │   ou cellule d'export dans le notebook
    │
    ├── mlflow.catboost.load_model("runs:/{run_id}/model")
    │         │
    │         ▼
    ├── model.save_model("model/xxx.cbm")
    ├── json.dump(meta, "artifacts/xxx_meta.json")
    │
    │
predictor.py (API FastAPI)
    │   MODEL_PATH=model/xxx.cbm
    │   META_PATH=artifacts/xxx_meta.json
    │
    ├── model.load_model(MODEL_PATH)    → CatBoostClassifier
    └── ModelMeta.load(META_PATH)       → threshold + features
```
