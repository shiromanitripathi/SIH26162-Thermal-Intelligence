import unittest
from unittest.mock import patch
from src.models.predictor import predict, predictor, ThermalSourcePredictor


class TestPredictor(unittest.TestCase):

    def test_mock_prediction_structure_when_model_missing(self):
        # Test fallback behavior when model is not loaded
        with patch.object(predictor, 'model', None):
            result = predictor.predict({"event_id": "EVT_TEST_001", "features": {}})
            self.assertEqual(result["classification"], "MODEL_NOT_AVAILABLE")
            self.assertIsNone(result["model_score"])
            self.assertTrue(result["is_mock"])
            self.assertEqual(result["model_version"], "mock-v0")
            self.assertIsInstance(result["evidence"], list)

    def test_real_model_loaded(self):
        # Verify real model is loaded when artifact exists
        self.assertTrue(predictor.is_model_loaded)
        result = predict({"event_id": "EVT_TEST_001", "features": {"active_days": 10}})
        self.assertIsNotNone(result["model_score"])
        self.assertFalse(result["is_mock"])
        self.assertIsInstance(result["evidence"], list)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            predict("invalid input")


if __name__ == "__main__":
    unittest.main()