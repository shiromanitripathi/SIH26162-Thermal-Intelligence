# SIH26162 Prediction Contract

## Status

The backend supports a stable prediction API while allowing the final trained
artifact to be installed separately.

The current labels are heuristic/weak labels. They are not independently
verified industrial-fire ground truth.

## Public endpoint

`POST /api/predict`

Request:

```json
{
  "event_id": "GRID_OR_EVENT_ID",
  "features": {
    "...": "exact feature values required by the installed artifact"
  }
}
```

Response:

```json
{
  "classification": "MODEL_NOT_AVAILABLE or artifact class label",
  "model_score": null,
  "evidence": [],
  "model_version": "mock-v0",
  "is_mock": true
}
```

## Runtime rules

1. A real artifact must contain `model` and `feature_names`.
2. `class_mapping` and `model_version` should be stored in the artifact.
3. Runtime feature order comes only from the artifact's `feature_names`.
4. Missing required features produce HTTP 422 when a real model is loaded.
5. Missing OSM context is never converted to zero automatically.
6. If the model has no `predict_proba`, `model_score` remains `null`.
7. `model_score` must not be described as a calibrated probability unless
   calibration is separately validated.
8. If no artifact is installed, the API returns `MODEL_NOT_AVAILABLE` and
   `is_mock=true`; it does not fabricate a prediction.
9. OSM is contextual evidence unless a specific validated artifact explicitly
   includes OSM fields as model inputs.
10. Reported ML metrics measure agreement with weak labels, not independently
    validated real-world industrial-fire accuracy.

## Final demo training script

`scripts/train_final.py` creates:

- `models/final_multiclass_model.joblib`
- `models/final_model_metadata.json`

The artifact uses the leakage-reduced FIRMS feature set documented by the ML
validation work. OSM remains contextual evidence for this artifact.
