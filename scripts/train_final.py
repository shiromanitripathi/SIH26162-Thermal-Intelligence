"""
Single-file training script for the SIH26162 Thermal Source Classifier.

Reads the aggregated FIRMS spatial dataset, splits it by 0.10-degree spatial
blocks (so nearby grid cells do not leak between train and test), trains a
4-class XGBoost model with balanced class weights, evaluates it, and saves:
  - models/final_multiclass_model.joblib
  - models/final_model_metadata.json

Run from project root:
    python -m scripts.train_final
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, classification_report, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

# ---------------------------------------------------------------------------
# 1. Paths & Model Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "firms_spatial_features.csv"
MODELS_DIR = PROJECT_ROOT / "models"
ARTIFACT_PATH = MODELS_DIR / "final_multiclass_model.joblib"
METADATA_PATH = MODELS_DIR / "final_model_metadata.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20
SPATIAL_BLOCK_SIZE_DEG = 0.10  # ~11 km grid blocks to prevent spatial leakage
MODEL_VERSION = "xgboost-leakage-reduced-firms-v1"

# 10 FIRMS thermal/temporal features used at inference time
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


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # 2. Load & Validate Dataset
    # -----------------------------------------------------------------------
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    required_cols = ["lat_grid", "lon_grid", *FINAL_FEATURES, TARGET]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError("Dataset is missing required columns: " + ", ".join(missing))

    X = df[FINAL_FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce")
    if X.isna().any().any() or y.isna().any():
        raise ValueError("Training data contains missing or non-numeric values.")
    y = y.astype(int)

    # -----------------------------------------------------------------------
    # 3. Spatial Block Train/Test Split (80% train / 20% test)
    #    Grouping by 0.10-degree lat/lon blocks ensures nearby hotspots stay
    #    together in either train or test, avoiding spatial leakage.
    # -----------------------------------------------------------------------
    lat_block = np.floor(df["lat_grid"] / SPATIAL_BLOCK_SIZE_DEG).astype(int)
    lon_block = np.floor(df["lon_grid"] / SPATIAL_BLOCK_SIZE_DEG).astype(int)
    spatial_groups = lat_block.astype(str) + "_" + lon_block.astype(str)

    splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    train_idx, test_idx = next(splitter.split(X, y, groups=spatial_groups))

    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

    # -----------------------------------------------------------------------
    # 4. Train XGBoost Classifier with Balanced Class Weights
    #    Balanced sample weights prevent rare classes (industrial/persistent)
    #    from being ignored by the majority vegetation/ephemeral classes.
    # -----------------------------------------------------------------------
    sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        num_class=4,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train, sample_weight=sample_weights)

    # -----------------------------------------------------------------------
    # 5. Evaluate on Held-Out Spatial Test Split
    # -----------------------------------------------------------------------
    predictions = model.predict(X_test)
    macro_f1 = float(f1_score(y_test, predictions, average="macro", zero_division=0))
    balanced_accuracy = float(balanced_accuracy_score(y_test, predictions))

    print("\n=== Test Split Classification Report ===")
    print(classification_report(y_test, predictions, digits=4, zero_division=0))

    # -----------------------------------------------------------------------
    # 6. Save Model Artifact & Metadata for FastAPI Predictor
    # -----------------------------------------------------------------------
    metadata = {
        "model_version": MODEL_VERSION,
        "target": TARGET,
        "feature_names": FINAL_FEATURES,
        "class_mapping": CLASS_MAPPING,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "test_macro_f1": macro_f1,
        "test_balanced_accuracy": balanced_accuracy,
        "label_status": "heuristic_weak_labels",
        "osm_role": "Contextual evidence only; OSM is not a model input.",
    }

    artifact = {
        "model": model,
        "feature_names": FINAL_FEATURES,
        "class_mapping": CLASS_MAPPING,
        "model_version": MODEL_VERSION,
        "metadata": metadata,
    }

    joblib.dump(artifact, ARTIFACT_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved model artifact: {ARTIFACT_PATH}")
    print(f"Saved metadata:       {METADATA_PATH}")
    print(f"Test Macro F1:        {macro_f1:.4f}")
    print(f"Test Balanced Acc:    {balanced_accuracy:.4f}")


if __name__ == "__main__":
    main()
