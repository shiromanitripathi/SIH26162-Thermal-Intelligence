import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

from src.models.predictor import (
    ThermalSourcePredictor,
    predict,
    predictor,
)


class _FakeModel:
    classes_ = np.array([0, 1])

    def predict(self, X):
        return np.array([1])

    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])


class TestPredictor(unittest.TestCase):
    def test_mock_prediction_structure_when_model_missing(self):
        with patch.object(predictor, "model", None):
            result = predictor.predict(
                {
                    "event_id": "EVT_TEST_001",
                    "features": {},
                }
            )

        self.assertEqual(
            result["classification"],
            "MODEL_NOT_AVAILABLE",
        )
        self.assertIsNone(result["model_score"])
        self.assertTrue(result["is_mock"])
        self.assertEqual(result["model_version"], "mock-v0")
        self.assertIsInstance(result["evidence"], list)

    def test_real_model_loaded(self):
        if not predictor.is_model_loaded:
            self.skipTest(
                "Final model artifact is not available locally."
            )

        features = {
            name: 1.0
            for name in predictor.feature_names
        }
        result = predict(
            {
                "event_id": "EVT_TEST_REAL",
                "features": features,
            }
        )

        self.assertNotEqual(
            result["classification"],
            "MODEL_NOT_AVAILABLE",
        )
        self.assertFalse(result["is_mock"])

    def test_missing_artifact_falls_back_cleanly(self):
        with TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.joblib"
            local_predictor = ThermalSourcePredictor(
                model_path=missing_path,
                metadata_path=Path(temp_dir) / "missing.json",
            )

            result = local_predictor.predict(
                {
                    "event_id": "EVT_MISSING",
                    "features": {},
                }
            )

        self.assertEqual(
            result["classification"],
            "MODEL_NOT_AVAILABLE",
        )
        self.assertIsNone(result["model_score"])

    def test_loaded_model_rejects_missing_features(self):
        with TemporaryDirectory() as temp_dir:
            local_predictor = ThermalSourcePredictor(
                model_path=Path(temp_dir) / "missing.joblib",
                metadata_path=Path(temp_dir) / "missing.json",
            )

            local_predictor.model = _FakeModel()
            local_predictor.feature_names = ["feature_a", "feature_b"]
            local_predictor.class_mapping = {1: "candidate"}

            with self.assertRaises(ValueError):
                local_predictor.predict(
                    {
                        "event_id": "EVT_STRICT",
                        "features": {
                            "feature_a": 1.0,
                        },
                    }
                )

    def test_loaded_model_uses_predicted_class_probability(self):
        with TemporaryDirectory() as temp_dir:
            local_predictor = ThermalSourcePredictor(
                model_path=Path(temp_dir) / "missing.joblib",
                metadata_path=Path(temp_dir) / "missing.json",
            )

            local_predictor.model = _FakeModel()
            local_predictor.feature_names = ["feature_a", "feature_b"]
            local_predictor.class_mapping = {1: "candidate"}
            local_predictor.model_version = "test-v1"

            result = local_predictor.predict(
                {
                    "event_id": "EVT_SCORE",
                    "features": {
                        "feature_a": 1.0,
                        "feature_b": 2.0,
                    },
                }
            )

        self.assertEqual(result["predicted_class"], 1)
        self.assertAlmostEqual(result["model_score"], 0.8)
        self.assertEqual(result["classification"], "candidate")

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            predict("invalid input")


if __name__ == "__main__":
    unittest.main()
