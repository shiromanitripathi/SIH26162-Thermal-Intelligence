from __future__ import annotations

import numpy as np
import pandas as pd

from src.ml.config import FIRMS_FEATURES, TARGET


def build_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Build a clean feature matrix and target vector."""

    missing = [
        column
        for column in FIRMS_FEATURES + [TARGET]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required ML columns: " + ", ".join(missing)
        )

    X = df[FIRMS_FEATURES].copy()
    y = df[TARGET].copy()

    # Force every model feature to numeric.
    for column in X.columns:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    # Reject invalid numerical values.
    if X.isna().any().any():
        bad_columns = X.columns[X.isna().any()].tolist()
        raise ValueError(
            "Non-numeric or missing feature values found in: "
            + ", ".join(bad_columns)
        )

    X = X.replace([np.inf, -np.inf], np.nan)

    if X.isna().any().any():
        raise ValueError("Infinite feature values detected.")

    # Validate target.
    y = pd.to_numeric(y, errors="coerce")

    if y.isna().any():
        raise ValueError("Target contains missing/non-numeric values.")

    y = y.astype(int)

    valid_classes = {0, 1, 2, 3}
    observed_classes = set(y.unique())

    if not observed_classes.issubset(valid_classes):
        raise ValueError(
            f"Unexpected target classes: "
            f"{sorted(observed_classes - valid_classes)}"
        )

    return X, y


def validate_feature_ranges(X: pd.DataFrame) -> dict:
    """Check basic physical and mathematical constraints."""

    checks = {}

    non_negative = [
        "observation_count",
        "active_days",
        "day_observations",
        "night_observations",
        "mean_frp",
        "max_frp",
        "std_frp",
        "type_2_count",
        "persistence_days",
    ]

    for column in non_negative:
        checks[f"{column}_non_negative"] = bool(
            (X[column] >= 0).all()
        )

    ratio_columns = [
        "recurrence_ratio",
        "night_ratio",
        "type_2_ratio",
    ]

    for column in ratio_columns:
        checks[f"{column}_between_0_1"] = bool(
            X[column].between(0, 1).all()
        )

    checks["day_plus_night_equals_observations"] = bool(
        (
            X["day_observations"]
            + X["night_observations"]
            == X["observation_count"]
        ).all()
    )

    checks["active_days_not_exceeding_observations"] = bool(
        (
            X["active_days"] <= X["observation_count"]
        ).all()
    )

    checks["all_constraints_pass"] = all(checks.values())

    return checks


if __name__ == "__main__":
    from src.ml.data_loader import load_dataset

    df = load_dataset()

    X, y = build_features(df)
    checks = validate_feature_ranges(X)

    print("=== FEATURE ENGINEERING ===")
    print("Feature matrix:", X.shape)
    print("Target:", y.shape)

    print("\n=== FEATURE RANGE AUDIT ===")
    for name, result in checks.items():
        print(f"{name}: {result}")
