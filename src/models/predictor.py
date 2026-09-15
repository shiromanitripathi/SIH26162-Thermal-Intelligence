"""
Temporary prediction interface for SIH26162.

Development-only implementation.
The real ML model and final feature schema are not frozen yet.
"""

from typing import Any, Mapping


class Predictor:
    """Stable backend-facing predictor interface."""

    def __init__(self) -> None:
        self.model = None
        self.model_version = "mock-v0"

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def predict(self, input_data: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(input_data, Mapping):
            raise TypeError("input_data must be a mapping/dictionary.")

        return {
            "classification": "MODEL_NOT_AVAILABLE",
            "model_score": None,
            "evidence": [
                "Development placeholder only. No trained model is loaded."
            ],
            "model_version": self.model_version,
            "is_mock": True,
        }


# Single shared predictor instance.
# Later, the real trained model can be loaded once into this object.
predictor = Predictor()


def predict(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Public prediction function used by the backend."""
    return predictor.predict(input_data)