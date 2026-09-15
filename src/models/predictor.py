"""
Production-ready predictor interface for SIH26162 Thermal Intelligence.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union

from src.features.feature_config import PROJECT_ROOT, ALL_MODEL_FEATURES
from src.features.build_features import fetch_osm_context_single

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_ARTIFACT_PATH = MODELS_DIR / "baseline_rf_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"


class ThermalSourcePredictor:
    """Predictor class for evaluating thermal source persistence and industrial context."""
    
    def __init__(self, model_path: Path = MODEL_ARTIFACT_PATH, metadata_path: Path = METADATA_PATH):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self._load_artifacts()
        
    def _load_artifacts(self):
        """Load serialized model artifact and metadata."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}. Run model training first.")
            
        artifact = joblib.load(self.model_path)
        self.model = artifact["model"]
        self.scaler = artifact.get("scaler", None)
        self.feature_names = artifact.get("feature_names", ALL_MODEL_FEATURES)
        
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def predict(self, input_features: Union[Dict[str, Any], pd.Series, pd.DataFrame]) -> Dict[str, Any]:
        """
        Make explainable prediction for input thermal grid cell.
        Accepts dictionary, pandas Series, or DataFrame.
        """
        if isinstance(input_features, dict):
            df = pd.DataFrame([input_features])
        elif isinstance(input_features, pd.Series):
            df = pd.DataFrame([input_features.to_dict()])
        elif isinstance(input_features, pd.DataFrame):
            df = input_features.copy()
        else:
            raise ValueError("Input features must be a dict, pandas Series, or DataFrame.")
            
        # Ensure all required feature columns exist, auto-impute defaults if missing
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
        
        # Extract row details for evidence summary
        row = df.iloc[0]
        grid_id = str(row.get("grid_id", f"{row.get('lat_grid', 0.0)}_{row.get('lon_grid', 0.0)}"))
        active_days = int(row.get("active_days", 1))
        persistence_days = int(row.get("persistence_days", 1))
        obs_count = int(row.get("observation_count", 1))
        night_ratio = float(row.get("night_ratio", 0.0))
        mean_frp = float(row.get("mean_frp", 0.0))
        osm_ind_count = int(row.get("osm_industrial_count", 0))
        osm_min_dist = float(row.get("osm_min_distance_m", 2000.0))
        
        evidence = {
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
        
        # Format human-readable evidence points
        explanation_lines = [
            f"Classification: {label} (Confidence: {prob*100:.1f}%)",
            f"• Thermal Persistence: Active on {active_days} distinct days over a span of {persistence_days} days.",
            f"• Diurnal Signature: Night observation ratio of {night_ratio*100:.1f}% ({int(obs_count*night_ratio)} night observations).",
            f"• Radiative Power: Mean Fire Radiative Power (FRP) of {mean_frp:.2f} MW.",
            f"• Infrastructure Context: {osm_ind_count} nearby OSM industrial features within 2km (min dist: {osm_min_dist:.1f}m)."
        ]
        
        return {
            "grid_id": grid_id,
            "predicted_class": pred_class,
            "confidence_score": round(prob, 4),
            "classification_label": label,
            "evidence": evidence,
            "explanation_summary": "\n".join(explanation_lines)
        }


_global_predictor = None

def get_predictor() -> ThermalSourcePredictor:
    """Singleton getter for API router service integration."""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = ThermalSourcePredictor()
    return _global_predictor
