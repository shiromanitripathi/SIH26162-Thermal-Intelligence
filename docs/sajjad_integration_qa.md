# Sajjad Integration QA Plan

## Predictor QA

- [ ] Valid dictionary input returns a structured response.
- [ ] Invalid non-dictionary input is rejected cleanly.
- [ ] Mock predictor clearly identifies itself with is_mock=true.
- [ ] model_score is null while no real model is loaded.
- [ ] model_version is included.
- [ ] No fake FIRMS observations, labels, accuracy, or model metrics are introduced.

## Prediction API QA

When POST /api/predict is integrated:

- [ ] Valid request returns HTTP 200.
- [ ] Response matches the agreed prediction schema.
- [ ] Invalid or missing request fields return validation errors.
- [ ] Invalid Pydantic input returns HTTP 422.
- [ ] Predictor failure is handled cleanly.
- [ ] ML logic is not duplicated inside the API route.
- [ ] Mock output remains clearly marked.

## Backend Integration QA

- [ ] FastAPI application starts successfully.
- [ ] /api/health works.
- [ ] Hotspot or event endpoints return documented JSON.
- [ ] Invalid resource ID returns a clean 404.
- [ ] Swagger/OpenAPI loads correctly.
- [ ] CORS works for the configured frontend origin.
- [ ] All automated tests pass.

## Security QA

- [ ] No API keys or passwords are committed.
- [ ] FIRMS key is read from environment variables.
- [ ] .env remains ignored by Git.
- [ ] .env.example contains placeholders only.

## Future Real Model QA

- [ ] Model artifact comes from the ML team.
- [ ] Feature names and order exactly match the approved schema.
- [ ] Model version is recorded.
- [ ] Backend inference matches ML reference predictions.
- [ ] Development mock behavior is disabled for the final system.
