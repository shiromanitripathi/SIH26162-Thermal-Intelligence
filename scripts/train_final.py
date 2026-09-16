"""
Train the reproducible final demo artifact from the leakage-reduced FIRMS
feature set.

Important: the target is heuristic/weak supervision. Reported test metrics
measure agreement with that labeling scheme; they are not independently
validated industrial-fire accuracy.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score

from src.ml.config import MODELS_DIR, RANDOM_STATE
from src.ml.data_loader import load_dataset
from src.ml.splitting import spatial_train_val_test_split
from src.ml.train_models import build_models, compute_sample_weights


FINAL_FEATURES = [
    "observation_count",
    "day_observations",
    "night_observations",
    "max_frp",
    "std_frp",
    "mean_brightness",
    "max_brightness",
    "mean_bright_t31",
    "max_bright_t31",
    "mean_confidence_score",
]

TARGET = "target_multiclass"

CLASS_MAPPING = {
    0: "Vegetation/agricultural fire candidate (weak label)",
    1: "Industrial fire candidate (weak label)",
    2: "Persistent thermal source candidate (weak label)",
    3: "Other/ephemeral hotspot (weak label)",
}

MODEL_VERSION = "xgboost-leakage-reduced-firms-v1"

ARTIFACT_PATH = MODELS_DIR / "final_multiclass_model.joblib"
METADATA_PATH = MODELS_DIR / "final_model_metadata.json"


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset()

    missing = [
        column
        for column in [*FINAL_FEATURES, TARGET]
        if column not in df.columns
    ]
    if missing:
        raise ValueError(
            "Final training dataset is missing columns: "
            + ", ".join(missing)
        )

    X = df[FINAL_FEATURES].apply(
        pd.to_numeric,
        errors="coerce",
    )
    y = pd.to_numeric(
        df[TARGET],
        errors="coerce",
    )

    if X.isna().any().any() or y.isna().any():
        raise ValueError(
            "Final training data contains missing/non-numeric values."
        )

    y = y.astype(int)

    split_frame = df[
        ["grid_id", "lat_grid", "lon_grid", TARGET]
    ].copy()
    split_frame["_row_index"] = range(len(split_frame))

    train_df, validation_df, test_df = (
        spatial_train_val_test_split(
            split_frame,
            random_state=RANDOM_STATE,
        )
    )

    development_idx = pd.Index(
        list(train_df["_row_index"])
        + list(validation_df["_row_index"])
    )
    test_idx = pd.Index(test_df["_row_index"])

    X_development = X.loc[development_idx]
    y_development = y.loc[development_idx]
    X_test = X.loc[test_idx]
    y_test = y.loc[test_idx]

    model = build_models()["xgboost"]

    model.fit(
        X_development,
        y_development,
        sample_weight=compute_sample_weights(y_development),
    )

    predictions = model.predict(X_test)

    macro_f1 = float(
        f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        )
    )
    balanced_accuracy = float(
        balanced_accuracy_score(
            y_test,
            predictions,
        )
    )

    metadata = {
        "model_version": MODEL_VERSION,
        "target": TARGET,
        "feature_names": FINAL_FEATURES,
        "class_mapping": CLASS_MAPPING,
        "train_plus_validation_rows": len(X_development),
        "untouched_test_rows": len(X_test),
        "test_macro_f1": macro_f1,
        "test_balanced_accuracy": balanced_accuracy,
        "label_status": "heuristic_weak_labels",
        "osm_role": (
            "Contextual evidence only; OSM is not a required model input "
            "for this artifact."
        ),
        "metric_warning": (
            "Metrics measure agreement with the heuristic labeling scheme "
            "and are not independently validated real-world industrial-fire "
            "accuracy."
        ),
    }

    artifact = {
        "model": model,
        "feature_names": FINAL_FEATURES,
        "class_mapping": CLASS_MAPPING,
        "model_version": MODEL_VERSION,
        "metadata": metadata,
    }

    joblib.dump(
        artifact,
        ARTIFACT_PATH,
    )
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Saved model artifact: {ARTIFACT_PATH}")
    print(f"Saved metadata: {METADATA_PATH}")
    print(f"Untouched-test macro F1: {macro_f1:.4f}")
    print(
        "Untouched-test balanced accuracy: "
        f"{balanced_accuracy:.4f}"
    )
    print(
        "Reminder: these metrics measure weak-label agreement, "
        "not independently verified real-world accuracy."
    )


if __name__ == "__main__":
    main()
