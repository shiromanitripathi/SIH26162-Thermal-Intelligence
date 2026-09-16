# Final Model Artifact Handoff

## Artifact identity

Model version: `xgboost-leakage-reduced-firms-v1`

Required local files:
- `models/final_multiclass_model.joblib`
- `models/final_model_metadata.json`

These files are intentionally ignored by Git and must be provisioned separately from a trusted team handoff.

## SHA-256 verification

Model:
`1FC022AD9B3B9CB68DFA403D93E54C6FFE551A18C4992DE31CBC3FCED25AC272`

Metadata:
`20DCB93E86919C4DF24DDBF3670968895B96AD43693DDA72ED4E730CB4E7EB67`

Windows PowerShell verification:

```powershell
Get-FileHash .\models\final_multiclass_model.joblib -Algorithm SHA256
Get-FileHash .\models\final_model_metadata.json -Algorithm SHA256
```

## Runtime used for artifact generation

- Python 3.12.3
- XGBoost 3.4.1
- scikit-learn 1.6.0
- joblib 1.4.2

The application runtime pins XGBoost 3.4.1 because the persisted estimator is an XGBoost classifier.

## Feature contract

The model requires exactly these ten features:

1. `observation_count`
2. `day_observations`
3. `night_observations`
4. `max_frp`
5. `std_frp`
6. `mean_brightness`
7. `max_brightness`
8. `mean_bright_t31`
9. `max_bright_t31`
10. `mean_confidence_score`

Missing or non-finite required features must not be fabricated.

## Class mapping

- 0: Vegetation/agricultural fire candidate (weak label)
- 1: Industrial fire candidate (weak label)
- 2: Persistent thermal source candidate (weak label)
- 3: Other/ephemeral hotspot (weak label)

These are heuristic weak labels, not verified ground-truth identities.

## Final artifact evaluation metadata

- Training rows: 518711
- Untouched test rows: 125839
- Macro F1: 0.82210158435369
- Balanced accuracy: 0.9289004646804202
- Label status: `heuristic_weak_labels`

The reported metrics measure agreement with the weak-label target definition. They must not be described as verified real-world industrial-fire accuracy.

## Security

`joblib`/pickle-style artifacts can execute code during deserialization. Only load the artifact obtained through the trusted project-team handoff and verify its SHA-256 before use.

## Current reproducibility limitation

The SHA-256 of the original historical FIRMS training dataset has not yet been recorded in this handoff. Do not invent or infer a dataset hash.
