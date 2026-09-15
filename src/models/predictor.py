"""
Production-ready predictor interface for SIH26162 Thermal Intelligence.
Provides both object-oriented ThermalSourcePredictor and functional predict() API.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union, Mapping, List

from src.features.feature_config import PROJECT_ROOT, ALL_MODEL_FEATURES

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_ARTIFACT_PATH = MODELS_DIR / "baseline_rf_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"


class ThermalSourcePredictor:
    """Predictor class for evaluating thermal source persistence and industrial context."""
    
    def __init__(self, model_path: Path = MODEL_ARTIFACT_PATH, metadata_path: Path = METADATA_PATH):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.scaler = None
        self.feature_names = ALL_MODEL_FEATURES
        self.model_version = "rf-baseline-v1.0"
        self._load_artifacts()
        
    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def _load_artifacts(self):
        """Load serialized model artifact and metadata."""
        if not self.model_path.exists():
            self.model = None
            return
            
        try:
            artifact = joblib.load(self.model_path)
            self.model = artifact["model"]
            self.scaler = artifact.get("scaler", None)
            self.feature_names = artifact.get("feature_names", ALL_MODEL_FEATURES)
            
            if self.metadata_path.exists():
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            print(f"Warning loading model artifact: {e}")
            self.model = None

    def predict(self, input_data: Union[Mapping[str, Any], Dict[str, Any], pd.Series, pd.DataFrame]) -> Dict[str, Any]:
        """
        Make explainable prediction for input thermal grid cell or event payload.
        Accepts dict/mapping, pandas Series, or DataFrame.
        """
        if not isinstance(input_data, (Mapping, dict, pd.Series, pd.DataFrame)):
            raise TypeError("input_data must be a mapping/dict, pandas Series, or DataFrame.")
            
        if not self.is_model_loaded:
            return {
                "classification": "MODEL_NOT_AVAILABLE",
                "model_score": None,
                "evidence": ["Development placeholder only. No trained model is loaded."],
                "model_version": "mock-v0",
                "is_mock": True,
            }
            
        # Unpack nested features dict if passed from prediction API router
        if isinstance(input_data, Mapping):
            raw_dict = dict(input_data)
            if "features" in raw_dict and isinstance(raw_dict["features"], dict):
                features_dict = dict(raw_dict["features"])
                features_dict["grid_id"] = raw_dict.get("event_id", features_dict.get("grid_id", "cell_0_0"))
            else:
                features_dict = raw_dict
            df = pd.DataFrame([features_dict])
        elif isinstance(input_data, pd.Series):
            df = pd.DataFrame([input_data.to_dict()])
        elif isinstance(input_data, pd.DataFrame):
            df = input_data.copy()
            
        # Auto-impute missing feature columns safely
        for col in self.feature_names:
            if col not in df.columns:
                if col.startswith("osm_"):
                    df[col] = 0.0 if col != "osm_min_distance_m" else 2000.0
                else:
                    df[col] = 0.0
                    
        X_input = df[self.feature_names].fillna(0.0)
        
        # Predict class and probability
        pred_class = int(self.model.predict(X_input)[0])
        prob = float(self.model.predict_proba(X_input)[0][1]) if hasattr(self.model, "predict_proba") else 0.5
        
        label = "Persistent Thermal Source / Industrial Candidate" if pred_class == 1 else "Ephemeral / Presumed Vegetation Fire"
        
        # Extract evidence metrics
        row = df.iloc[0]
        grid_id = str(row.get("grid_id", f"{row.get('lat_grid', 0.0)}_{row.get('lon_grid', 0.0)}"))
        active_days = int(row.get("active_days", 1))
        persistence_days = int(row.get("persistence_days", 1))
        obs_count = int(row.get("observation_count", 1))
        night_ratio = float(row.get("night_ratio", 0.0))
        mean_frp = float(row.get("mean_frp", 0.0))
        osm_ind_count = int(row.get("osm_industrial_count", 0))
        osm_min_dist = float(row.get("osm_min_distance_m", 2000.0))
        
        evidence_lines = [
            f"Classification: {label} (Confidence: {prob*100:.1f}%)",
            f"Thermal Persistence: Active on {active_days} distinct days over a span of {persistence_days} days.",
            f"Diurnal Signature: Night observation ratio of {night_ratio*100:.1f}% ({int(obs_count*night_ratio)} night observations).",
            f"Radiative Power: Mean Fire Radiative Power (FRP) of {mean_frp:.2f} MW.",
            f"Infrastructure Context: {osm_ind_count} nearby OSM industrial features within 2km (min dist: {osm_min_dist:.1f}m)."
        ]
        
        evidence_dict = {
            "observation_count": obs_count,
            "active_days": active_days,
            "persistence_days": persistence_days,
            "recurrence_ratio": round(float(row.get("recurrence_ratio", 0.0)), 4),
            "night_ratio": round(night_ratio, 4),
            "mean_frp": round(mean_frp, 2),
            "max_frp": round(float(row.get("max_frp", 0.0)), 2),
            "osm_industrial_count": osm_ind_count,
            "osm_power_count": int(row.get("osm_power_count", 0)),
            "osm_min_distance_m": round(osm_min_dist, 2)
        }
        
        return {
            "grid_id": grid_id,
            "classification": label,
            "predicted_class": pred_class,
            "confidence_score": round(prob, 4),
            "model_score": round(prob, 4),
            "classification_label": label,
            "evidence": evidence_lines,
            "evidence_dict": evidence_dict,
            "explanation_summary": "\n".join(evidence_lines),
            "model_version": self.model_version,
            "is_mock": False
        }


# Single shared predictor instance
predictor = ThermalSourcePredictor()


def get_predictor() -> ThermalSourcePredictor:
    """Singleton getter for API router service integration."""
    return predictor


def predict(input_data: Union[Mapping[str, Any], Dict[str, Any]]) -> dict[str, Any]:
    """Public prediction function used by backend routers."""
    return predictor.predict(input_data)
