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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# -----------------------------
# Config / Meta
# -----------------------------

# Remonte de briefml/api/ → briefml/ → racine du projet
BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_MODEL_PATH = str(
    BASE_DIR / "model" / "catboost_product15_v2_time_bucket_final.cbm"
)
DEFAULT_META_PATH = str(
    BASE_DIR / "artifacts" / "catboost_product15_v2_time_bucket_final_meta.json"
)
MISSING_CAT = os.getenv("MISSING_CAT", "__MISSING__")


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
    model_path = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    meta_path = Path(os.getenv("META_PATH", DEFAULT_META_PATH))

    if not model_path.exists():
        raise FileNotFoundError(f"Modèle .cbm introuvable: {model_path}")

    meta = ModelMeta.load(meta_path)

    model = CatBoostClassifier()
    model.load_model(str(model_path))
    return model, meta


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
    X = pd.DataFrame([row], columns=meta.features).replace({pd.NA: np.nan})

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
                X[c] = pd.to_numeric(X[c], errors="raise").astype(float)
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

MODEL: CatBoostClassifier | None = None
META: ModelMeta | None = None


@app.on_event("startup")
def _startup() -> None:
    global MODEL, META
    MODEL, META = load_model_and_meta()


@app.get("/health")
def health() -> dict[str, Any]:
    if MODEL is None or META is None:
        return {"status": "loading"}
    return {
        "status": "ok",
        "model_name": META.model_name,
        "threshold": META.threshold,
        "n_features": len(META.features),
    }


class PredictRequest(BaseModel):
    data: dict[str, Any] = Field(
        ..., description="Dictionnaire des 15 champs utilisateur"
    )


class PredictResponse(BaseModel):
    proba: float
    pred_class: int
    label: str
    threshold: float


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    if MODEL is None or META is None:
        raise HTTPException(
            status_code=503, detail="Modèle non prêt (startup en cours)."
        )

    X = normalize_input(dict(req.data), META)

    proba = float(MODEL.predict_proba(X)[0, 1])
    threshold = float(META.threshold)
    pred_class = int(proba >= threshold)
    label = "grave" if pred_class == 1 else "non_grave"

    return PredictResponse(
        proba=proba, pred_class=pred_class, label=label, threshold=threshold
    )
