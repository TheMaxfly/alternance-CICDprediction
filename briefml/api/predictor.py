"""
predictor.py — API FastAPI pour prédire la gravité d'un accident
(CatBoost product15_v2_time_bucket)

- Charge un modèle CatBoost (.cbm) et un meta.json (features, cat_features, threshold)
- Valide / normalise les 15 champs utilisateur
- Retourne proba + pred_class + label

Lancement :
  uvicorn briefml.api.predictor:app --host 0.0.0.0 --port 8000 --reload

Variables d'environnement (optionnelles) :
  MODEL_PATH=/app/model/catboost_product15_v2_time_bucket_final.cbm
  META_PATH=/app/artifacts/catboost_product15_v2_time_bucket_final_meta.json
  MISSING_CAT=__MISSING__
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# -----------------------------
# Config / Meta
# -----------------------------

# Remonte de briefml/api/ → briefml/ → racine du projet
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "model"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DEFAULT_MODEL_NAME = "catboost_product15_v2_time_bucket_final"

DEFAULT_MODEL_PATH = str(
    MODEL_DIR / f"{DEFAULT_MODEL_NAME}.cbm"
)
DEFAULT_META_PATH = str(
    ARTIFACTS_DIR / f"{DEFAULT_MODEL_NAME}_meta.json"
)
MISSING_CAT = os.getenv("MISSING_CAT", "__MISSING__")

APP_START_TIME = time.time()

PREDICTION_REQUESTS_TOTAL = Counter(
    "prediction_requests_total",
    "Nombre total de requetes envoyees a /predict",
)

PREDICTION_RESULTS_TOTAL = Counter(
    "prediction_results_total",
    "Nombre total de predictions par classe retournee",
    ["label"],
)

PREDICTION_REQUEST_DURATION_SECONDS = Histogram(
    "prediction_request_duration_seconds",
    "Temps de traitement des requetes /predict",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)

PREDICTION_VALIDATION_ERRORS_TOTAL = Counter(
    "prediction_validation_errors_total",
    "Nombre total d'erreurs de validation sur /predict",
)

PREDICTION_HTTP_ERRORS_TOTAL = Counter(
    "prediction_http_errors_total",
    "Nombre total d'erreurs HTTP sur l'API de prediction",
    ["status_code"],
)

APP_UPTIME_SECONDS = Gauge(
    "app_uptime_seconds",
    "Temps ecoule depuis le demarrage de l'application",
)


@dataclass(frozen=True)
class ModelMeta:
    model_name: str
    threshold: float
    features: list[str]
    cat_features: list[str]

    @staticmethod
    def load(meta_path: str | Path) -> ModelMeta:
        p = Path(meta_path)
        if not p.exists():
            raise FileNotFoundError(f"Meta JSON introuvable: {p}")
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)

        for k in ("threshold", "features", "cat_features"):
            if k not in obj:
                raise ValueError(f"Champ manquant dans meta.json: {k}")

        return ModelMeta(
            model_name=str(
                obj.get("model_name", "catboost_product15_v2_time_bucket_final")
            ),
            threshold=float(obj["threshold"]),
            features=list(obj["features"]),
            cat_features=list(obj["cat_features"]),
        )


def load_model_and_meta() -> tuple[CatBoostClassifier, ModelMeta]:
    model_path, meta_path = resolve_model_paths()

    if not model_path.exists():
        raise FileNotFoundError(f"Modèle .cbm introuvable: {model_path}")

    meta = ModelMeta.load(meta_path)

    model = CatBoostClassifier()
    model.load_model(str(model_path))
    return model, meta


def resolve_model_paths(model_name: str | None = None) -> tuple[Path, Path]:
    if model_name is None:
        return (
            Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)),
            Path(os.getenv("META_PATH", DEFAULT_META_PATH)),
        )

    return (
        MODEL_DIR / f"{model_name}.cbm",
        ARTIFACTS_DIR / f"{model_name}_meta.json",
    )


def list_available_models() -> list[str]:
    available_models: list[str] = []

    if not MODEL_DIR.exists():
        return available_models

    for model_path in sorted(MODEL_DIR.glob("*.cbm")):
        model_name = model_path.stem
        meta_path = ARTIFACTS_DIR / f"{model_name}_meta.json"
        if meta_path.exists():
            available_models.append(model_name)

    return available_models


def load_named_model(model_name: str) -> tuple[str, CatBoostClassifier, ModelMeta]:
    model_path, meta_path = resolve_model_paths(model_name)

    if not model_path.exists():
        raise FileNotFoundError(f"Modèle .cbm introuvable: {model_path}")

    if not meta_path.exists():
        raise FileNotFoundError(f"Meta JSON introuvable: {meta_path}")

    model = CatBoostClassifier()
    model.load_model(str(model_path))
    meta = ModelMeta.load(meta_path)
    return model_path.stem, model, meta


def activate_model(model_name: str) -> ModelMeta:
    global ACTIVE_MODEL_NAME, MODEL, META
    available_models = list_available_models()
    if model_name not in available_models:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Modèle introuvable",
                "model_name": model_name,
                "available_models": available_models,
            },
        )

    active_model_name, model, meta = load_named_model(model_name)
    ACTIVE_MODEL_NAME = active_model_name
    MODEL = model
    META = meta
    return meta


# -----------------------------
# Validation / Normalisation
# -----------------------------

# Defaults facultatifs: complète si tu veux autoriser des champs omis.
DEFAULTS: dict[str, Any] = {}

# Champs à forcer en numérique
NUMERIC_FIELDS: set[str] = set()


def normalize_input(payload: dict[str, Any], meta: ModelMeta) -> pd.DataFrame:
    missing = [c for c in meta.features if c not in payload]
    if missing:
        can_fill = [c for c in missing if c in DEFAULTS]
        still_missing = [c for c in missing if c not in DEFAULTS]
        if still_missing:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Champs manquants",
                    "missing_fields": still_missing,
                    "hint": (
                        "Fournis tous les 15 champs, ou définis des DEFAULTS"
                        " côté API si tu veux autoriser des omissions."
                    ),
                },
            )
        for c in can_fill:
            payload[c] = DEFAULTS[c]

    row = {c: payload.get(c, np.nan) for c in meta.features}
    X = pd.DataFrame([row], columns=meta.features).replace({pd.NA: np.nan})  # type: ignore[call-overload]

    # catégorielles -> str + token manquant
    for c in meta.cat_features:
        if c in X.columns:
            X[c] = X[c].astype("string").fillna(MISSING_CAT).astype(str)

    # numériques
    for c in meta.features:
        if c in NUMERIC_FIELDS:
            v = X.at[0, c]
            if pd.isna(v):
                continue
            if isinstance(v, str) and ":" in v:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Format invalide",
                        "field": c,
                        "value": v,
                        "hint": "Le champ doit être un nombre (HH:MM non accepté).",
                    },
                )
            try:
                X[c] = pd.to_numeric(X[c], errors="raise").astype(float)  # type: ignore[union-attr]
            except Exception as err:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Valeur numérique invalide",
                        "field": c,
                        "value": payload.get(c),
                        "hint": "Le champ doit être numérique.",
                    },
                ) from err

    return X


# -----------------------------
# FastAPI
# -----------------------------

app = FastAPI(title="Accidents — CatBoost product15_v2_time_bucket", version="1.0.0")

ACTIVE_MODEL_NAME: str | None = None
MODEL: CatBoostClassifier | None = None
META: ModelMeta | None = None


@app.on_event("startup")
def _startup() -> None:
    global ACTIVE_MODEL_NAME, MODEL, META
    model_path, _ = resolve_model_paths()
    MODEL, META = load_model_and_meta()
    ACTIVE_MODEL_NAME = model_path.stem


@app.get("/health")
def health() -> dict[str, Any]:
    APP_UPTIME_SECONDS.set(time.time() - APP_START_TIME)
    if MODEL is None or META is None:
        return {"status": "loading"}
    return {
        "status": "ok",
        "active_model": ACTIVE_MODEL_NAME,
        "model_name": META.model_name,
        "threshold": META.threshold,
        "n_features": len(META.features),
    }


@app.get("/metrics")
def metrics() -> Response:
    APP_UPTIME_SECONDS.set(time.time() - APP_START_TIME)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


class PredictRequest(BaseModel):
    data: dict[str, Any] = Field(
        ..., description="Dictionnaire des 15 champs utilisateur"
    )


class ModelSelectionRequest(BaseModel):
    model_name: str = Field(..., description="Nom du modèle à charger")


class PredictResponse(BaseModel):
    proba: float
    pred_class: int
    label: str
    threshold: float


@app.get("/models")
def get_models() -> dict[str, Any]:
    return {
        "available_models": list_available_models(),
        "active_model": ACTIVE_MODEL_NAME,
    }


@app.post("/models/select")
def select_model(req: ModelSelectionRequest) -> dict[str, Any]:
    meta = activate_model(req.model_name)
    return {
        "status": "ok",
        "active_model": ACTIVE_MODEL_NAME,
        "model_name": meta.model_name,
        "threshold": meta.threshold,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    start = time.perf_counter()
    PREDICTION_REQUESTS_TOTAL.inc()

    try:
        if MODEL is None or META is None:
            raise HTTPException(
                status_code=503, detail="Modèle non prêt (startup en cours)."
            )

        X = normalize_input(dict(req.data), META)

        proba = float(MODEL.predict_proba(X)[0, 1])
        threshold = float(META.threshold)
        pred_class = int(proba >= threshold)
        label = "grave" if pred_class == 1 else "non_grave"

        PREDICTION_RESULTS_TOTAL.labels(label=label).inc()

        return PredictResponse(
            proba=proba, pred_class=pred_class, label=label, threshold=threshold
        )

    except HTTPException as exc:
        if exc.status_code == 422:
            PREDICTION_VALIDATION_ERRORS_TOTAL.inc()

        PREDICTION_HTTP_ERRORS_TOTAL.labels(status_code=str(exc.status_code)).inc()
        raise

    except Exception:
        PREDICTION_HTTP_ERRORS_TOTAL.labels(status_code="500").inc()
        raise

    finally:
        PREDICTION_REQUEST_DURATION_SECONDS.observe(time.perf_counter() - start)
