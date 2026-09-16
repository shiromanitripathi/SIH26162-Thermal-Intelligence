"""
Strict backend-facing predictor for SIH26162.

The predictor never invents missing model features, OSM context, confidence
scores, or class meanings. A trained artifact is optional at development time;
when it is absent the API returns an explicit MODEL_NOT_AVAILABLE response.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd

from src.features.feature_config import PROJECT_ROOT


MODELS_DIR = PROJECT_ROOT / "models"
MODEL_ARTIFACT_PATH = Path(
    os.getenv(
        "MODEL_ARTIFACT_PATH",
        str(MODELS_DIR / "final_multiclass_model.joblib"),
    )
)
METADATA_PATH = Path(
    os.getenv(
        "MODEL_METADATA_PATH",
        str(MODELS_DIR / "final_model_metadata.json"),
    )
)


class ThermalSourcePredictor:
    def __init__(
        self,
        model_path: Path = MODEL_ARTIFACT_PATH,
        metadata_path: Path = METADATA_PATH,
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.model = None
        self.feature_names: list[str] = []
        self.class_mapping: dict[Any, str] = {}
        self.model_version = "mock-v0"
        self.metadata: dict[str, Any] = {}
        self._load_artifacts()

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def _load_artifacts(self) -> None:
        if not self.model_path.exists():
            return

        try:
            artifact = joblib.load(self.model_path)

            if not isinstance(artifact, dict):
                raise ValueError(
                    "Model artifact must be a dictionary contract."
                )

            if "model" not in artifact:
                raise ValueError(
                    "Model artifact is missing the 'model' entry."
                )

            feature_names = artifact.get("feature_names")
            if not feature_names:
                raise ValueError(
                    "Model artifact is missing feature_names."
                )

            self.model = artifact["model"]
            self.feature_names = list(feature_names)
            self.model_version = str(
                artifact.get("model_version", "unversioned-model")
            )
            self.metadata = dict(artifact.get("metadata", {}))

            mapping = artifact.get("class_mapping", {})
            self.class_mapping = {
                self._normalize_class_key(key): str(value)
                for key, value in dict(mapping).items()
            }

            if self.metadata_path.exists():
                external_metadata = json.loads(
                    self.metadata_path.read_text(encoding="utf-8")
                )
                self.metadata.update(external_metadata)

        except Exception as exc:
            print(f"Warning loading model artifact: {exc}")
            self.model = None
            self.feature_names = []
            self.class_mapping = {}
            self.model_version = "mock-v0"
            self.metadata = {}

    @staticmethod
    def _normalize_class_key(value: Any) -> Any:
        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value

        return value

    def _mock_result(self, grid_id: str | None = None) -> dict[str, Any]:
        evidence = [
            "No trained final model artifact is loaded. "
            "No classification or model score has been fabricated."
        ]
        return {
            "grid_id": grid_id,
            "classification": "MODEL_NOT_AVAILABLE",
            "predicted_class": None,
            "confidence_score": None,
            "model_score": None,
            "classification_label": None,
            "evidence": evidence,
            "explanation_summary": evidence[0],
            "model_version": "mock-v0",
            "is_mock": True,
        }

    def predict(
        self,
        input_data: Mapping[str, Any] | pd.Series | pd.DataFrame,
    ) -> dict[str, Any]:
        if not isinstance(
            input_data,
            (Mapping, pd.Series, pd.DataFrame),
        ):
            raise TypeError(
                "input_data must be a mapping, pandas Series, or DataFrame."
            )

        event_id: str | None = None

        if isinstance(input_data, Mapping):
            raw = dict(input_data)
            event_id = (
                str(raw["event_id"])
                if raw.get("event_id") is not None
                else None
            )
            nested = raw.get("features")
            if nested is not None:
                if not isinstance(nested, Mapping):
                    raise TypeError("features must be a mapping/dictionary.")
                features = dict(nested)
            else:
                features = raw

            df = pd.DataFrame([features])

        elif isinstance(input_data, pd.Series):
            df = pd.DataFrame([input_data.to_dict()])

        else:
            df = input_data.copy()

        if len(df) != 1:
            raise ValueError(
                "The prediction API accepts exactly one event at a time."
            )

        row_dict = df.iloc[0].to_dict()
        grid_id_value = (
            row_dict.get("grid_id")
            or event_id
        )
        grid_id = (
            str(grid_id_value)
            if grid_id_value is not None
            else None
        )

        if not self.is_model_loaded:
            return self._mock_result(grid_id)

        missing = [
            name
            for name in self.feature_names
            if name not in df.columns
            or pd.isna(df.iloc[0][name])
        ]
        if missing:
            raise ValueError(
                "Missing required model features: "
                + ", ".join(missing)
            )

        X_input = df[self.feature_names].copy()

        for name in self.feature_names:
            X_input[name] = pd.to_numeric(
                X_input[name],
                errors="coerce",
            )

        values = X_input.to_numpy(dtype=float)

        if not np.isfinite(values).all():
            raise ValueError(
                "Model features must contain only finite numeric values."
            )

        raw_prediction = self.model.predict(X_input)[0]
        pred_class = self._normalize_class_key(raw_prediction)

        model_score: float | None = None

        if hasattr(self.model, "predict_proba"):
            probabilities = np.asarray(
                self.model.predict_proba(X_input)
            )
            if probabilities.ndim == 2 and probabilities.shape[0] == 1:
                classes = [
                    self._normalize_class_key(value)
                    for value in getattr(
                        self.model,
                        "classes_",
                        range(probabilities.shape[1]),
                    )
                ]
                if pred_class in classes:
                    class_index = classes.index(pred_class)
                    model_score = float(
                        probabilities[0][class_index]
                    )

        label = self.class_mapping.get(
            pred_class,
            f"Class {pred_class}",
        )

        evidence = [
            f"Model classification: {label}."
        ]

        if model_score is not None:
            evidence.append(
                "Predicted-class model score: "
                f"{model_score:.4f}. "
                "Treat this as an uncalibrated model score unless "
                "calibration has been separately validated."
            )

        observed_evidence = [
            ("active_days", "Observed active days"),
            ("persistence_days", "Observed persistence days"),
            ("night_ratio", "Observed night ratio"),
            ("mean_frp", "Observed mean FRP"),
            ("observation_count", "Observed FIRMS count"),
        ]

        for key, label_text in observed_evidence:
            value = row_dict.get(key)
            if value is not None and not pd.isna(value):
                evidence.append(f"{label_text}: {value}.")

        osm_available = row_dict.get("osm_context_available")
        if osm_available is True:
            for key, label_text in [
                (
                    "osm_industrial_count",
                    "Mapped industrial features in OSM context",
                ),
                (
                    "osm_min_distance_m",
                    "Nearest mapped OSM context distance (m)",
                ),
            ]:
                value = row_dict.get(key)
                if value is not None and not pd.isna(value):
                    evidence.append(f"{label_text}: {value}.")
        elif osm_available is False:
            evidence.append(
                "OSM context is marked unavailable for this event; "
                "missing OSM values are not interpreted as zero."
            )

        return {
            "grid_id": grid_id,
            "classification": label,
            "predicted_class": pred_class,
            "confidence_score": model_score,
            "model_score": model_score,
            "classification_label": label,
            "evidence": evidence,
            "explanation_summary": "\n".join(evidence),
            "model_version": self.model_version,
            "is_mock": False,
        }


predictor = ThermalSourcePredictor()


def get_predictor() -> ThermalSourcePredictor:
    return predictor


def predict(input_data: Mapping[str, Any]) -> dict[str, Any]:
    return predictor.predict(input_data)
