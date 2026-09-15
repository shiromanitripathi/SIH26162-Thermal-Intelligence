import unittest

from src.models.predictor import predict, predictor


class TestPredictor(unittest.TestCase):

    def test_mock_prediction_structure(self):
        result = predict(
            {
                "event_id": "EVT_TEST_001",
                "features": {},
            }
        )

        self.assertEqual(result["classification"], "MODEL_NOT_AVAILABLE")
        self.assertIsNone(result["model_score"])
        self.assertTrue(result["is_mock"])
        self.assertEqual(result["model_version"], "mock-v0")
        self.assertIsInstance(result["evidence"], list)

    def test_real_model_not_loaded(self):
        self.assertFalse(predictor.is_model_loaded)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            predict("invalid input")


if __name__ == "__main__":
    unittest.main()