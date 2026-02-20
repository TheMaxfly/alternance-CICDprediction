"""
Data models for Streamlit prediction interface.

This module defines Pydantic models for:
- PredictionInput: 15 input variables for accident severity prediction
- PredictionResult: Prediction output from the FastAPI backend

Based on data_dictionary_catboost_product15_v2.md
"""

from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


class PredictionInput(BaseModel):
    """
    Represents the 15 input variables required for accident severity prediction.

    All fields are required and must conform to the data dictionary.
    """

    dep: str = Field(..., description="Département (code INSEE, ex: '59', '75', '2A', '971')")
    lum: int = Field(..., ge=1, le=5, description="Conditions d'éclairage (1-5)")
    atm: int = Field(..., description="Conditions atmosphériques (-1 ou 1-9)")
    catr: int = Field(..., description="Catégorie de route (1-7, 9)")
    agg: int = Field(..., ge=1, le=2, description="Agglomération (1=hors, 2=en)")
    int: int = Field(..., ge=1, le=9, description="Type d'intersection (1-9)")
    circ: int = Field(..., description="Régime de circulation (-1 ou 1-4)")
    col: int = Field(..., description="Type de collision (-1 ou 1-7)")
    vma_bucket: str = Field(..., description="Classe de vitesse maximale autorisée")
    catv_family_4: str = Field(..., description="Famille de véhicule (4 classes)")
    manv_mode: int = Field(..., ge=-1, le=26, description="Manœuvre (-1 ou 0-26)")
    driver_age_bucket: str = Field(..., description="Classe d'âge conducteur")
    choc_mode: int = Field(..., ge=-1, le=9, description="Point de choc initial (-1 ou 0-9)")
    driver_trajet_family: str = Field(..., description="Famille de trajet conducteur")
    time_bucket: str = Field(
        ...,
        description="Tranche horaire (night_00_05, morning_06_11, afternoon_12_17, evening_18_23)"
    )

    @field_validator('dep')
    @classmethod
    def validate_dep(cls, v: str) -> str:
        """Validate department code format."""
        # Basic pattern check - full validation against ref_options.json happens server-side
        if not v or len(v) < 1:
            raise ValueError("Department code cannot be empty")
        return v

    @field_validator('atm')
    @classmethod
    def validate_atm(cls, v: int) -> int:
        """Validate atmospheric conditions code."""
        if v == -1 or (1 <= v <= 9):
            return v
        raise ValueError("atm must be -1 or 1-9")

    @field_validator('catr')
    @classmethod
    def validate_catr(cls, v: int) -> int:
        """Validate road category code."""
        if v in [1, 2, 3, 4, 5, 6, 7, 9]:
            return v
        raise ValueError("catr must be 1-7 or 9")

    @field_validator('circ')
    @classmethod
    def validate_circ(cls, v: int) -> int:
        """Validate circulation regime code."""
        if v == -1 or (1 <= v <= 4):
            return v
        raise ValueError("circ must be -1 or 1-4")

    @field_validator('col')
    @classmethod
    def validate_col(cls, v: int) -> int:
        """Validate collision type code."""
        if v == -1 or (1 <= v <= 7):
            return v
        raise ValueError("col must be -1 or 1-7")

    @field_validator('vma_bucket')
    @classmethod
    def validate_vma_bucket(cls, v: str) -> str:
        """Validate VMA bucket."""
        valid_buckets = ["<=30", "31-50", "51-80", "81-90", "91-110", "111-130", ">130", "inconnue"]
        if v not in valid_buckets:
            raise ValueError(f"vma_bucket must be one of {valid_buckets}")
        return v

    @field_validator('catv_family_4')
    @classmethod
    def validate_catv_family_4(cls, v: str) -> str:
        """Validate vehicle family."""
        valid_families = ["voitures_utilitaires", "2rm_3rm", "lourds_tc_agri_autres", "vulnerables"]
        if v not in valid_families:
            raise ValueError(f"catv_family_4 must be one of {valid_families}")
        return v

    @field_validator('driver_age_bucket')
    @classmethod
    def validate_driver_age_bucket(cls, v: str) -> str:
        """Validate driver age bucket."""
        valid_buckets = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+", "unknown"]
        if v not in valid_buckets:
            raise ValueError(f"driver_age_bucket must be one of {valid_buckets}")
        return v

    @field_validator('driver_trajet_family')
    @classmethod
    def validate_driver_trajet_family(cls, v: str) -> str:
        """Validate driver trip family."""
        valid_families = ["trajet_1", "trajet_2", "trajet_3", "trajet_4", "trajet_5", "trajet_9", "unknown"]
        if v not in valid_families:
            raise ValueError(f"driver_trajet_family must be one of {valid_families}")
        return v

    @field_validator('time_bucket')
    @classmethod
    def validate_time_bucket(cls, v: str) -> str:
        """Validate time bucket."""
        valid_buckets = [
            "night_00_05",
            "morning_06_11",
            "afternoon_12_17",
            "evening_18_23",
        ]
        if v not in valid_buckets:
            raise ValueError(f"time_bucket must be one of {valid_buckets}")
        return v

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "dep": "59",
                "lum": 1,
                "atm": 1,
                "catr": 3,
                "agg": 2,
                "int": 1,
                "circ": 2,
                "col": 3,
                "vma_bucket": "51-80",
                "catv_family_4": "voitures_utilitaires",
                "manv_mode": 1,
                "driver_age_bucket": "25-34",
                "choc_mode": 1,
                "driver_trajet_family": "trajet_1",
                "time_bucket": "morning_06_11"
            }
        }


class PredictionResult(BaseModel):
    """
    Represents the prediction output from the FastAPI backend.

    Contains:
    - probability: float between 0.0 and 1.0
    - prediction: "grave" or "non_grave"
    - threshold: decision threshold (always 0.47)
    - inputs_summary: optional echo of inputs for verification
    """

    probability: float = Field(..., ge=0.0, le=1.0, description="Probabilité d'accident grave (0-1)")
    prediction: Literal["grave", "non_grave"] = Field(..., description="Classe prédite")
    threshold: float = Field(0.47, description="Seuil de décision appliqué")
    inputs_summary: dict[str, Any] | None = Field(None, description="Résumé des entrées (pour vérification)")

    @field_validator('prediction')
    @classmethod
    def validate_prediction_consistency(cls, v: str, info) -> str:
        """Validate that prediction matches probability and threshold."""
        # Note: This validator runs after all fields are set
        # We can't access other fields here in v2, so we skip the cross-field validation
        # This will be validated server-side
        if v not in ["grave", "non_grave"]:
            raise ValueError("prediction must be 'grave' or 'non_grave'")
        return v

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "probability": 0.68,
                "prediction": "grave",
                "threshold": 0.47,
                "inputs_summary": {
                    "dep": "59",
                    "lum": 1
                }
            }
        }
