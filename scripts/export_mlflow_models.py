"""
Export des meilleurs modeles CatBoost depuis MLflow vers .cbm + meta.json.

Usage (depuis la racine du projet) :
    python scripts/export_mlflow_models.py

Prerequis : MLflow server accessible sur http://127.0.0.1:5000
    mlflow server --backend-store-uri sqlite:///mlflow.db \
        --default-artifact-root ./mlartifacts

Ce script :
1. Charge les meilleurs runs Optuna et Hyperopt depuis MLflow
2. Exporte chaque modele en .cbm dans model/
3. Genere le meta.json correspondant dans artifacts/
4. Les fichiers sont prets pour predictor.py via MODEL_PATH / META_PATH
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import mlflow

# --- Config ---
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "model"
ARTIFACTS_DIR = ROOT / "artifacts"

FEATURES = [
    "dep",
    "lum",
    "atm",
    "catr",
    "agg",
    "int",
    "circ",
    "col",
    "vma_bucket",
    "catv_family_4",
    "manv_mode",
    "driver_age_bucket",
    "choc_mode",
    "driver_trajet_family",
    "time_bucket",
]

# Experiments et run IDs connus (mis a jour apres chaque execution des notebooks)
MODELS = {
    "catboost_optuna_best": {
        "experiment_name": "optuna-catboost-recall",
        "run_id": "f66bc2e7987d4740bcfe6b03f1986662",
    },
    "catboost_hyperopt_best": {
        "experiment_name": "hyperopt-catboost-recall",
        "run_id": "efe13ed7d0054e3ca33e57eb799ec919",
    },
}


def export_model(model_name: str, run_id: str, experiment_name: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"Export: {model_name}")
    print(f"  Run ID     : {run_id}")
    print(f"  Experiment : {experiment_name}")
    print(f"{'=' * 60}")

    # Charger le modele depuis MLflow
    model_uri = f"runs:/{run_id}/model"
    print(f"  Chargement depuis MLflow: {model_uri}")
    model = mlflow.catboost.load_model(model_uri)

    # Recuperer les metriques et params du run
    client = mlflow.MlflowClient()
    run = client.get_run(run_id)
    metrics = run.data.metrics
    params = run.data.params

    # Sauvegarder le .cbm
    MODEL_DIR.mkdir(exist_ok=True)
    cbm_path = MODEL_DIR / f"{model_name}.cbm"
    model.save_model(str(cbm_path))
    print(f"  .cbm exporte : {cbm_path}")

    # Construire le meta.json
    threshold = metrics.get("threshold", 0.5)

    # Recuperer les hyperparametres CatBoost depuis les params MLflow
    catboost_param_keys = [
        "depth",
        "learning_rate",
        "l2_leaf_reg",
        "random_strength",
        "min_data_in_leaf",
        "border_count",
        "scale_pos_weight",
        "bootstrap_type",
        "bagging_temperature",
        "subsample",
    ]
    catboost_params = {}
    for k in catboost_param_keys:
        if k in params:
            val = params[k]
            try:
                val = float(val)
                if val == int(val):
                    val = int(val)
            except (ValueError, OverflowError):
                pass
            catboost_params[k] = val

    meta = {
        "model_name": model_name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "threshold": threshold,
        "features": FEATURES,
        "cat_features": FEATURES,
        "catboost_params": catboost_params,
        "metrics": {
            k: round(v, 6)
            for k, v in metrics.items()
            if k
            in (
                "threshold",
                "pr_auc",
                "roc_auc",
                "recall",
                "precision",
                "f1",
                "f2",
                "accuracy",
            )
        },
        "mlflow_run_id": run_id,
        "mlflow_experiment": experiment_name,
    }

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    meta_path = ARTIFACTS_DIR / f"{model_name}_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  meta.json exporte : {meta_path}")

    # Resume
    print("\n  Metriques :")
    for k in ("pr_auc", "roc_auc", "recall", "precision", "f1", "f2", "threshold"):
        if k in metrics:
            print(f"    {k:12s}: {metrics[k]:.4f}")

    print("\n  Utilisation dans predictor.py :")
    print(f"    MODEL_PATH={cbm_path}")
    print(f"    META_PATH={meta_path}")


def main() -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")

    for model_name, config in MODELS.items():
        try:
            export_model(model_name, config["run_id"], config["experiment_name"])
        except Exception as e:
            print(f"\nERREUR pour {model_name}: {e}", file=sys.stderr)
            print(
                "  Verifiez que MLflow server est lance et que le run_id est correct."
            )
            continue

    print(f"\n{'=' * 60}")
    print("Export termine.")
    print(f"Fichiers dans : {MODEL_DIR} et {ARTIFACTS_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
