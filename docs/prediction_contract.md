# SIH26162 Prediction Contract

## Purpose

This document defines the temporary Day-1 contract between the FastAPI backend and the predictor layer.

The final ML feature schema, labels, trained model, production classes, and model filename are not frozen yet.

## Request

The temporary prediction request contains:

- event_id: thermal event identifier
- features: generic dictionary of input features

Example request:

{"event_id": "EVT_TEST_001", "features": {}}

The features object is intentionally generic. Final feature names must come from the validated ML pipeline.

## Response

The temporary response contains:

- classification
- model_score
- evidence
- model_version
- is_mock

Example response:

{"classification": "MODEL_NOT_AVAILABLE", "model_score": null, "evidence": ["Development placeholder only. No trained model is loaded."], "model_version": "mock-v0", "is_mock": true}

## Rules

1. Mock predictions must never be presented as real ML results.
2. model_score must not be described as a calibrated probability unless calibration is validated.
3. Backend code must not invent final ML features, classes, accuracy, or model filename.
4. The real ML model should replace the predictor implementation without requiring the API contract to be redesigned.
5. The trained model should eventually be loaded once during application startup instead of once per request.

## Current Status

Day-1 predictor: temporary development mock.

Real ML integration: pending validated model delivery from the ML team.
