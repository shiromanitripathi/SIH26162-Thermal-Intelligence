# Sajjad Integration QA Plan

## Predictor QA

- [x] Valid dictionary input returns a structured response.
- [x] Invalid non-dictionary input is rejected cleanly.
- [x] Mock predictor clearly identifies itself with is_mock=true.
- [x] model_score is null while no real model is loaded.
- [x] model_version is included.
- [x] No fake FIRMS observations, labels, accuracy, or model metrics are introduced.

## Prediction API QA

- [x] Valid request returns HTTP 200.
- [x] Response matches the agreed prediction schema.
- [x] Invalid or missing request fields return validation errors.
- [x] Invalid Pydantic input returns HTTP 422.
- [x] Predictor failure is handled cleanly.
- [x] ML logic is not duplicated inside the API route.
- [x] Mock output remains clearly marked.

## Backend Integration QA

- [x] FastAPI application starts successfully.
- [x] /api/health works.
- [x] Hotspot or event endpoints return documented JSON.
- [x] Invalid resource ID returns a clean 404.
- [x] Swagger/OpenAPI loads correctly.
- [x] CORS works for the configured frontend origin.
- [x] All automated tests pass.

## Security QA

- [ ] No API keys or passwords are committed.
- [ ] FIRMS key is read from environment variables.
- [x] .env remains ignored by Git.
- [x] .env.example contains placeholders only.

## Future Real Model QA

- [ ] Model artifact comes from the ML team.
- [ ] Feature names and order exactly match the approved schema.
- [ ] Model version is recorded.
- [ ] Backend inference matches ML reference predictions.
- [ ] Development mock behavior is disabled for the final system.