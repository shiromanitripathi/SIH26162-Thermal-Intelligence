# Final ML Model Handoff Checklist

## Model Artifact

- [ ] Final model filename
- [ ] Model artifact format/library
- [ ] Model version
- [ ] Exact model loading method
- [ ] Required Python/package versions

## Feature Contract

- [ ] Exact feature names
- [ ] Exact feature order
- [ ] Input data types
- [ ] Required vs optional features
- [ ] Missing-value handling
- [ ] Valid ranges where applicable

## Preprocessing

- [ ] Exact preprocessing steps
- [ ] Encoders/scalers included or supplied
- [ ] Categorical mappings
- [ ] Missing-value preprocessing
- [ ] Inference preprocessing matches training

## Output Contract

- [ ] Final class mapping
- [ ] Prediction output type
- [ ] Probability/confidence availability
- [ ] Confidence meaning documented
- [ ] Evidence/top-factor availability

## Validation

- [ ] Representative valid input record supplied
- [ ] Expected prediction for reference record supplied
- [ ] Training/evaluation methodology documented
- [ ] Weak-label limitations documented
- [ ] Spatial/temporal leakage considerations documented

## Backend Integration

- [ ] Model can load without notebook execution
- [ ] Model path agreed
- [ ] Environment variables documented
- [ ] Missing artifact behavior agreed
- [ ] Predictor response matches API contract