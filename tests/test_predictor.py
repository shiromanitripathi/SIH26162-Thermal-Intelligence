import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.features.feature_config import ALL_MODEL_FEATURES
from src.models.predictor import (
    ThermalSourcePredictor,
    predict,
    predictor,
)


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
            self.assertEqual(
                result["model_version"],
                "mock-v0",
            )
            self.assertIsInstance(
                result["evidence"],
                list,
            )

    @unittest.skipUnless(
        predictor.is_model_loaded,
        "Final model artifact is not available locally",
    )
    def test_real_model_loaded(self):
        features = {
            name: 0.0
            for name in ALL_MODEL_FEATURES
        }

        features.update(
            {
                "observation_count": 20,
                "active_days": 10,
                "persistence_days": 60,
                "night_ratio": 0.4,
                "mean_frp": 10.0,
                "max_frp": 20.0,
                "osm_min_distance_m": 2000.0,
            }
        )

        result = predict(
            {
                "event_id": "EVT_TEST_001",
                "features": features,
            }
        )

        self.assertIsNotNone(result["model_score"])
        self.assertFalse(result["is_mock"])
        self.assertIsInstance(
            result["evidence"],
            list,
        )

    def test_missing_artifact_falls_back_cleanly(self):
        with TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)

            local_predictor = ThermalSourcePredictor(
                model_path=base / "missing_model.joblib",
                metadata_path=base / "missing_metadata.json",
            )

            self.assertFalse(
                local_predictor.is_model_loaded
            )

            result = local_predictor.predict(
                {
                    "event_id": "EVT_MISSING_MODEL",
                    "features": {},
                }
            )

            self.assertEqual(
                result["classification"],
                "MODEL_NOT_AVAILABLE",
            )
            self.assertIsNone(
                result["model_score"]
            )
            self.assertTrue(
                result["is_mock"]
            )

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            predict("invalid input")


if __name__ == "__main__":
    unittest.main()