# MLflow — Guide pratique BriefML

## Démarrer le serveur

```bash
uv run mlflow server --host 127.0.0.1 --port 5000
```

- UI : [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Données persistées dans `mlflow.db` + `mlartifacts/` à la racine du projet
- Le serveur peut être arrêté (`Ctrl+C`) sans perte de données

---

## Étape 1 — Tuning manuel (3 configurations)

L'objectif est de créer un run MLflow par configuration testée afin de les comparer visuellement.

**Cellule à ajouter dans `11catboost_check_time_columns.ipynb`** (après la cellule `c5ccc0fe`) :

```python
import mlflow
import mlflow.catboost
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("accidentologie_model_benchmark")

# 3 configurations à tester — varier depth, learning_rate, iterations
MANUAL_CONFIGS = [
    {"run_name": "catboost_tuning_depth6_lr002",  "depth": 6, "learning_rate": 0.02,  "iterations": 3000},
    {"run_name": "catboost_tuning_depth8_lr005",  "depth": 8, "learning_rate": 0.05,  "iterations": 2000},
    {"run_name": "catboost_tuning_depth4_lr01",   "depth": 4, "learning_rate": 0.1,   "iterations": 1500},
]

for cfg in MANUAL_CONFIGS:
    run_name = cfg.pop("run_name")
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({
            "notebook": "11catboost_check_time_columns.ipynb",
            "model_family": "catboost",
            "tag": "accidentologie",
            "tuning": "manual",
        })
        mlflow.log_params(cfg)

        model = CatBoostClassifier(**cfg, loss_function="Logloss", random_seed=42, verbose=0)
        model.fit(X_train, y_train, cat_features=cat_cols, eval_set=(X_valid, y_valid))

        proba = model.predict_proba(X_valid)[:, 1]
        auc = roc_auc_score(y_valid, proba)
        mlflow.log_metric("valid_roc_auc", auc)
        print(f"{run_name} → AUC={auc:.4f}")
```

> **Prérequis** : cellules `fd6f0376`, `7a004a75`, `c5ccc0fe`, `bhvu2q1x3sm` exécutées.

---

## Étape 2 — Comparer les runs dans l'UI

1. Ouvrir [http://127.0.0.1:5000/#/experiments/2](http://127.0.0.1:5000/#/experiments/2)
2. Cocher les runs à comparer (tuning + run final)
3. Cliquer **Compare**
4. Dans la vue comparative :
   - Onglet **Parallel Coordinates** → visualiser l'impact de chaque hyperparamètre sur `valid_roc_auc`
   - Onglet **Scatter Plot** → `depth` vs `valid_roc_auc`, `learning_rate` vs `valid_roc_auc`
   - Onglet **Table** → trier par `valid_roc_auc` décroissant pour identifier le meilleur run

**Métriques communes à comparer entre tous les modèles :**

| Métrique MLflow | Signification |
| --- | --- |
| `valid_roc_auc` | AUC sur holdout 20% — **métrique principale** |
| `valid_f1` | F1 à threshold fixe |
| `valid_bestf1_f1` | F1 au meilleur threshold |
| `valid_bestf1_threshold` | Threshold optimal trouvé |
| `cv_primary_score` | Score CV interne (pas holdout) |

---

## Étape 3 — Logger des artefacts

Ajouter dans la cellule MLflow (après `mlflow.log_metrics`) :

### Matrice de confusion

```python
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import tempfile, os

pred = (proba_eval >= threshold_default).astype(int)
cm = confusion_matrix(eval_y, pred)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(cm, display_labels=["Non grave", "Grave"]).plot(ax=ax)
ax.set_title(f"Confusion Matrix — threshold={threshold_default:.2f}")

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "confusion_matrix.png")
    fig.savefig(path, bbox_inches="tight")
    mlflow.log_artifact(path, artifact_path="plots")
plt.close(fig)
```

### Courbe ROC

```python
from sklearn.metrics import RocCurveDisplay

fig, ax = plt.subplots(figsize=(6, 5))
RocCurveDisplay.from_predictions(eval_y, proba_eval, ax=ax, name="CatBoost")
ax.set_title("Courbe ROC — holdout")

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "roc_curve.png")
    fig.savefig(path, bbox_inches="tight")
    mlflow.log_artifact(path, artifact_path="plots")
plt.close(fig)
```

### Feature importance (noms des features)

```python
import json, tempfile, os

feature_importance = dict(zip(
    cat_cols,
    model_obj.get_feature_importance().tolist()
))
feature_importance_sorted = dict(
    sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
)

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "feature_importance.json")
    with open(path, "w") as f:
        json.dump(feature_importance_sorted, f, indent=2)
    mlflow.log_artifact(path, artifact_path="plots")
```

---

## Étape 4 — Model Registry

### Enregistrer le meilleur modèle

Lors du logging MLflow, passer `registered_model_name` à `log_model` :

```python
model_info = mlflow.catboost.log_model(
    model_obj,
    artifact_path="model",
    registered_model_name="briefml-catboost-product15-v2-time-bucket",
)
```

Ce run est déjà configuré ainsi dans `mlflow11-code-v1` — le modèle est enregistré
sous `briefml-catboost-product15-v2-time-bucket v1`.

### Promouvoir une version dans l'UI

1. Onglet **Models** → `briefml-catboost-product15-v2-time-bucket`
2. Cliquer sur la version souhaitée
3. Bouton **Transition to** → `Staging` ou `Production`

### Enregistrer après coup (depuis un run existant)

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

best_run_id = "41e662fd88684facb78fa046f377af8b"  # run FINISHED du CatBoost
model_uri = f"runs:/{best_run_id}/model"

mlflow.register_model(
    model_uri=model_uri,
    name="briefml-catboost-product15-v2-time-bucket",
)
```

---

## Étape 5 — Recharger un modèle depuis le Registry

### Charger la dernière version en Production

```python
import mlflow.catboost

mlflow.set_tracking_uri("http://127.0.0.1:5000")

model = mlflow.catboost.load_model(
    model_uri="models:/briefml-catboost-product15-v2-time-bucket/Production"
)
```

### Charger une version spécifique

```python
model = mlflow.catboost.load_model(
    model_uri="models:/briefml-catboost-product15-v2-time-bucket/1"
)
```

### Vérifier les prédictions après rechargement

```python
import pandas as pd

# Exemple avec les 15 features du projet
sample = X_valid.head(5).copy()
proba = model.predict_proba(sample)[:, 1]
pred = (proba >= 0.47).astype(int)  # threshold du meta.json

print(pd.DataFrame({
    "proba_grave": proba.round(3),
    "pred_grave": pred,
    "y_reel": y_valid.head(5).values,
}))
```

### Charger sans serveur actif (depuis le fichier .cbm)

```python
from catboost import CatBoostClassifier
from pathlib import Path

root = Path(".")  # adapter si besoin
model = CatBoostClassifier()
model.load_model(str(root / "out" / "catboost_product15_v2_time_bucket_final.cbm"))
```

---

## Référence rapide — Noms des runs enregistrés

| Notebook | run_name(s) | model_family |
| --- | --- | --- |
| 11 — CatBoost | `catboost_product15_v2_time_bucket_final` | `catboost` |
| 12 — Random Forest | `rf_auc_opt`, `rf_f1_opt`, `rf_recall_opt` | `random_forest` |
| 14 — XGBoost | `xgb_auc_opt`, `xgb_f1_opt`, `xgb_recall_opt` | `xgboost` |
| 15 — Logistic Regression | `logreg_auc_opt`, `logreg_f1_opt`, `logreg_recall_opt` | `logistic_regression` |

Expérience commune : **`accidentologie_model_benchmark`**
