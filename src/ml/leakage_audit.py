from __future__ import annotations

import pandas as pd

from src.ml.config import (
    FIRMS_FEATURES,
    TARGET,
    TARGET_COLUMNS,
    IDENTIFIER_COLUMNS,
)


def audit_feature_schema(df: pd.DataFrame) -> dict:
    """Check that model features cannot accidentally contain identifiers or targets."""

    feature_set = set(FIRMS_FEATURES)
    target_set = set(TARGET_COLUMNS)
    identifier_set = set(IDENTIFIER_COLUMNS)

    target_in_features = sorted(feature_set & target_set)
    identifiers_in_features = sorted(feature_set & identifier_set)

    return {
        "feature_count": len(FIRMS_FEATURES),
        "target_in_features": target_in_features,
        "identifiers_in_features": identifiers_in_features,
        "schema_safe": (
            len(target_in_features) == 0
            and len(identifiers_in_features) == 0
        ),
    }


def audit_target_relationships(df: pd.DataFrame) -> dict:
    """Measure relationships between the weak label and label-generating variables.

    This is intentionally diagnostic. Strong relationships are expected because
    the current target is heuristic/weakly supervised.
    """

    direct_label_dependencies = [
        "active_days",
        "persistence_days",
        "night_ratio",
        "type_2_count",
        "mean_frp",
    ]

    derived_label_dependencies = [
        "recurrence_ratio",
        "type_2_ratio",
        "obs_per_active_day",
    ]

    correlations = {}

    for column in direct_label_dependencies:
        if column in df.columns:
            correlations[column] = float(
                df[column].corr(df[TARGET])
            )

    return {
        "target": TARGET,
        "direct_label_dependencies": [
            column for column in direct_label_dependencies
            if column in df.columns
        ],
        "derived_label_dependencies": [
            column for column in derived_label_dependencies
            if column in df.columns
        ],
        "diagnostic_correlations": correlations,
        "warning": (
            "The target is heuristic/weakly supervised. "
            "The model can learn patterns used to generate the target, "
            "including direct and derived label-related features. "
            "Therefore, benchmark metrics measure agreement with the "
            "heuristic labels and must not be interpreted as independent "
            "real-world classification accuracy."
        ),
    }


def audit_label_consistency(df: pd.DataFrame) -> dict:
    """Check consistency between the multiclass and binary targets."""

    if "target_persistent_source" not in df.columns:
        return {
            "available": False,
            "consistent": None,
        }

    expected_binary = df[TARGET].isin([1, 2]).astype(int)
    actual_binary = df["target_persistent_source"].astype(int)

    mismatches = int((expected_binary != actual_binary).sum())

    return {
        "available": True,
        "mismatches": mismatches,
        "consistent": mismatches == 0,
    }


def run_full_audit(df: pd.DataFrame) -> dict:
    """Run all pre-training leakage and label audits."""

    schema = audit_feature_schema(df)
    relationships = audit_target_relationships(df)
    labels = audit_label_consistency(df)

    return {
        "schema": schema,
        "target_relationships": relationships,
        "label_consistency": labels,
    }


if __name__ == "__main__":
    from src.ml.data_loader import load_dataset

    df = load_dataset()
    report = run_full_audit(df)

    print("=== FEATURE SCHEMA AUDIT ===")
    for key, value in report["schema"].items():
        print(f"{key}: {value}")

    print("\n=== TARGET RELATIONSHIP AUDIT ===")
    for key, value in report["target_relationships"].items():
        print(f"{key}: {value}")

    print("\n=== LABEL CONSISTENCY AUDIT ===")
    for key, value in report["label_consistency"].items():
        print(f"{key}: {value}")
