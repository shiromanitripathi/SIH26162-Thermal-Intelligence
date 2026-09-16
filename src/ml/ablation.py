from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from src.ml.config import RANDOM_STATE
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


# ---------------------------------------------------------------------
# Features directly or indirectly used in the heuristic target
# ---------------------------------------------------------------------

LEAKAGE_REDUCED_REMOVED_FEATURES = [
    "active_days",
    "persistence_days",
    "night_ratio",
    "type_2_count",
    "mean_frp",
    "recurrence_ratio",
    "obs_per_active_day",
    "type_2_ratio",
]


# ---------------------------------------------------------------------
# Real OSM features
# ---------------------------------------------------------------------

OSM_FEATURES = [
    "osm_feature_count",
    "osm_industrial_count",
    "osm_power_count",
    "osm_manmade_count",
    "osm_min_distance_m",
]


# ---------------------------------------------------------------------
# Class weights
# ---------------------------------------------------------------------

def class_weights(y):
    counts = y.value_counts()
    total = len(y)
    n_classes = len(counts)

    return y.map({
        cls: total / (n_classes * count)
        for cls, count in counts.items()
    })


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------

def build_models():
    return {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )),
        ]),

        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),

        "random_forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),

        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=300,
            learning_rate=0.08,
            max_leaf_nodes=31,
            random_state=RANDOM_STATE,
        ),

        "xgboost": XGBClassifier(
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
        ),
    }


# ---------------------------------------------------------------------
# Training and evaluation
# ---------------------------------------------------------------------

def train_model(name, model, X_train, y_train, X_val, y_val):

    start = time.time()

    if name in {
        "hist_gradient_boosting",
        "xgboost",
    }:
        model.fit(
            X_train,
            y_train,
            sample_weight=class_weights(y_train),
        )
    else:
        model.fit(
            X_train,
            y_train,
        )

    predictions = model.predict(X_val)

    return {
        "model": name,
        "macro_f1": f1_score(
            y_val,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "balanced_accuracy": balanced_accuracy_score(
            y_val,
            predictions,
        ),
        "training_seconds": round(
            time.time() - start,
            2,
        ),
    }


# ---------------------------------------------------------------------
# Load real persisted OSM context
# ---------------------------------------------------------------------

def load_real_osm():

    osm_dir = Path(
        "data/processed/osm_context_tiles"
    )

    tile_files = sorted(
        osm_dir.glob("tile_*.csv")
    )

    if not tile_files:
        raise FileNotFoundError(
            "No persisted OSM tile files found in "
            f"{osm_dir}"
        )

    print(
        f"Loading {len(tile_files)} persisted OSM tile files..."
    )

    frames = []

    required_columns = [
        "grid_id",
        *OSM_FEATURES,
    ]

    for path in tile_files:

        tile = pd.read_csv(path)

        missing = [
            col
            for col in required_columns
            if col not in tile.columns
        ]

        if missing:
            raise ValueError(
                f"{path} is missing columns: {missing}"
            )

        tile = tile[
            required_columns
        ].copy()

        frames.append(tile)

    osm = pd.concat(
        frames,
        ignore_index=True,
    )

    duplicate_grid_ids = (
        osm["grid_id"]
        .duplicated()
        .sum()
    )

    if duplicate_grid_ids:
        raise ValueError(
            "Duplicate OSM grid IDs detected: "
            f"{duplicate_grid_ids}"
        )

    print(
        f"OSM coverage: {len(osm):,} grid cells"
    )

    return osm


# ---------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print("LEAKAGE-REDUCED FIRMS + OSM ABLATION")
    print("=" * 80)

    # ---------------------------------------------------------------
    # Load FIRMS spatial dataset
    # ---------------------------------------------------------------

    print("\nLoading FIRMS spatial dataset...")

    df = load_dataset()

    X, y = build_features(df)

    print(
        f"FIRMS rows: {len(df):,}"
    )

    print(
        f"Full FIRMS features: {X.shape[1]}"
    )

    # ---------------------------------------------------------------
    # Preserve original row indices
    # ---------------------------------------------------------------

    data = df.copy()

    data["_row_index"] = range(
        len(data)
    )

    # ---------------------------------------------------------------
    # Load real OSM
    # ---------------------------------------------------------------

    osm = load_real_osm()

    # ---------------------------------------------------------------
    # Restrict experiments to exact FIRMS/OSM overlap
    # ---------------------------------------------------------------

    osm_grid_ids = set(
        osm["grid_id"]
    )

    matched_mask = data[
        "grid_id"
    ].isin(osm_grid_ids)

    data = data.loc[
        matched_mask
    ].copy()

    print(
        f"Matched FIRMS/OSM cells: "
        f"{len(data):,}"
    )

    if len(data) != len(osm):
        raise ValueError(
            "FIRMS/OSM matching is not one-to-one. "
            f"FIRMS matched: {len(data)}, "
            f"OSM rows: {len(osm)}"
        )

    # ---------------------------------------------------------------
    # Verify exact grid-ID match
    # ---------------------------------------------------------------

    firms_grid_ids = set(
        data["grid_id"]
    )

    if firms_grid_ids != osm_grid_ids:
        raise ValueError(
            "FIRMS and OSM grid-ID sets do not match exactly."
        )

    print(
        "FIRMS and OSM grid IDs match exactly."
    )

    # ---------------------------------------------------------------
    # Create ONE spatial split for all experiments
    # ---------------------------------------------------------------

    print(
        "\nCreating controlled spatial split..."
    )

    train_df, val_df, test_df = (
        spatial_train_val_test_split(
            data,
            random_state=RANDOM_STATE,
        )
    )

    train_ids = set(
        train_df["grid_id"]
    )

    val_ids = set(
        val_df["grid_id"]
    )

    test_ids = set(
        test_df["grid_id"]
    )

    # ---------------------------------------------------------------
    # Verify spatial separation
    # ---------------------------------------------------------------

    if train_ids & val_ids:
        raise ValueError(
            "Spatial overlap detected between train and validation."
        )

    if train_ids & test_ids:
        raise ValueError(
            "Spatial overlap detected between train and test."
        )

    if val_ids & test_ids:
        raise ValueError(
            "Spatial overlap detected between validation and test."
        )

    print(
        f"Train cells: {len(train_df):,}"
    )

    print(
        f"Validation cells: {len(val_df):,}"
    )

    print(
        f"Test cells: {len(test_df):,}"
    )

    print(
        "Spatial separation verified."
    )

    # ---------------------------------------------------------------
    # Row indices
    # ---------------------------------------------------------------

    train_idx = train_df[
        "_row_index"
    ]

    val_idx = val_df[
        "_row_index"
    ]

    y_train = y.loc[
        train_idx
    ]

    y_val = y.loc[
        val_idx
    ]

    # ---------------------------------------------------------------
    # Full FIRMS
    # ---------------------------------------------------------------

    X_firms_train = X.loc[
        train_idx
    ].copy()

    X_firms_val = X.loc[
        val_idx
    ].copy()

    # ---------------------------------------------------------------
    # Leakage-reduced FIRMS
    # ---------------------------------------------------------------

    missing_removed = [
        col
        for col in LEAKAGE_REDUCED_REMOVED_FEATURES
        if col not in X_firms_train.columns
    ]

    if missing_removed:
        raise ValueError(
            "Expected leakage-related features not found: "
            f"{missing_removed}"
        )

    X_reduced_train = (
        X_firms_train.drop(
            columns=LEAKAGE_REDUCED_REMOVED_FEATURES
        )
    )

    X_reduced_val = (
        X_firms_val.drop(
            columns=LEAKAGE_REDUCED_REMOVED_FEATURES
        )
    )

    # ---------------------------------------------------------------
    # OSM features
    # ---------------------------------------------------------------

    osm_indexed = osm.set_index(
        "grid_id"
    )

    train_grid_ids = train_df[
        "grid_id"
    ].tolist()

    val_grid_ids = val_df[
        "grid_id"
    ].tolist()

    X_osm_train = osm_indexed.loc[
        train_grid_ids,
        OSM_FEATURES,
    ].copy()

    X_osm_val = osm_indexed.loc[
        val_grid_ids,
        OSM_FEATURES,
    ].copy()

    # Align indices with FIRMS matrices.
    X_osm_train.index = train_idx
    X_osm_val.index = val_idx

    # ---------------------------------------------------------------
    # Leakage-reduced FIRMS + real OSM
    # ---------------------------------------------------------------

    X_reduced_osm_train = pd.concat(
        [
            X_reduced_train,
            X_osm_train,
        ],
        axis=1,
    )

    X_reduced_osm_val = pd.concat(
        [
            X_reduced_val,
            X_osm_val,
        ],
        axis=1,
    )

    # ---------------------------------------------------------------
    # Define experiments
    # ---------------------------------------------------------------

    experiments = {

        "full_firms": (
            X_firms_train,
            X_firms_val,
        ),

        "leakage_reduced_firms": (
            X_reduced_train,
            X_reduced_val,
        ),

        "leakage_reduced_firms_osm": (
            X_reduced_osm_train,
            X_reduced_osm_val,
        ),
    }

    # ---------------------------------------------------------------
    # Validation checks
    # ---------------------------------------------------------------

    for experiment_name, (
        X_train,
        X_val,
    ) in experiments.items():

        if X_train.isnull().any().any():
            raise ValueError(
                f"NaN values found in "
                f"{experiment_name} train data."
            )

        if X_val.isnull().any().any():
            raise ValueError(
                f"NaN values found in "
                f"{experiment_name} validation data."
            )

        if not X_train.index.equals(
            y_train.index
        ):
            raise ValueError(
                f"Training index mismatch in "
                f"{experiment_name}."
            )

        if not X_val.index.equals(
            y_val.index
        ):
            raise ValueError(
                f"Validation index mismatch in "
                f"{experiment_name}."
            )

    # ---------------------------------------------------------------
    # Print experiment definitions
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("EXPERIMENT DEFINITIONS")
    print("=" * 80)

    for experiment_name, (
        X_train,
        X_val,
    ) in experiments.items():

        print(
            f"\n{experiment_name}"
        )

        print(
            f"Features: {X_train.shape[1]}"
        )

        print(
            "Feature names:"
        )

        print(
            ", ".join(
                X_train.columns
            )
        )

    # ---------------------------------------------------------------
    # Train models
    # ---------------------------------------------------------------

    all_results = []

    for experiment_name, (
        X_train,
        X_val,
    ) in experiments.items():

        print("\n" + "=" * 80)
        print(
            f"EXPERIMENT: {experiment_name}"
        )
        print("=" * 80)

        models = build_models()

        for name, model in models.items():

            print(
                f"\nTraining {name}..."
            )

            result = train_model(
                name,
                model,
                X_train,
                y_train,
                X_val,
                y_val,
            )

            result["experiment"] = (
                experiment_name
            )

            result["feature_count"] = (
                X_train.shape[1]
            )

            all_results.append(
                result
            )

            print(
                f"Macro F1: "
                f"{result['macro_f1']:.4f}"
            )

            print(
                f"Balanced Accuracy: "
                f"{result['balanced_accuracy']:.4f}"
            )

            print(
                f"Training time: "
                f"{result['training_seconds']:.2f}s"
            )

    # ---------------------------------------------------------------
    # Results
    # ---------------------------------------------------------------

    results = pd.DataFrame(
        all_results
    )

    results = results[
        [
            "experiment",
            "model",
            "feature_count",
            "macro_f1",
            "balanced_accuracy",
            "training_seconds",
        ]
    ]

    # ---------------------------------------------------------------
    # Comparison table
    # ---------------------------------------------------------------

    baseline = results[
        results["experiment"]
        == "full_firms"
    ][
        [
            "model",
            "macro_f1",
            "balanced_accuracy",
        ]
    ].rename(
        columns={
            "macro_f1": "full_macro_f1",
            "balanced_accuracy":
                "full_balanced_accuracy",
        }
    )

    reduced = results[
        results["experiment"]
        == "leakage_reduced_firms"
    ][
        [
            "model",
            "macro_f1",
            "balanced_accuracy",
        ]
    ].rename(
        columns={
            "macro_f1":
                "reduced_macro_f1",
            "balanced_accuracy":
                "reduced_balanced_accuracy",
        }
    )

    reduced_osm = results[
        results["experiment"]
        == "leakage_reduced_firms_osm"
    ][
        [
            "model",
            "macro_f1",
            "balanced_accuracy",
        ]
    ].rename(
        columns={
            "macro_f1":
                "reduced_osm_macro_f1",
            "balanced_accuracy":
                "reduced_osm_balanced_accuracy",
        }
    )

    comparison = (
        baseline
        .merge(
            reduced,
            on="model",
        )
        .merge(
            reduced_osm,
            on="model",
        )
    )

    comparison[
        "macro_f1_change_after_leakage_reduction"
    ] = (
        comparison["reduced_macro_f1"]
        - comparison["full_macro_f1"]
    )

    comparison[
        "balanced_accuracy_change_after_leakage_reduction"
    ] = (
        comparison["reduced_balanced_accuracy"]
        - comparison["full_balanced_accuracy"]
    )

    comparison[
        "macro_f1_osm_delta"
    ] = (
        comparison[
            "reduced_osm_macro_f1"
        ]
        - comparison[
            "reduced_macro_f1"
        ]
    )

    comparison[
        "balanced_accuracy_osm_delta"
    ] = (
        comparison[
            "reduced_osm_balanced_accuracy"
        ]
        - comparison[
            "reduced_balanced_accuracy"
        ]
    )

    # ---------------------------------------------------------------
    # Save results
    # ---------------------------------------------------------------

    output_dir = Path(
        "models"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        output_dir
        / "ablation_results.csv"
    )

    comparison_path = (
        output_dir
        / "leakage_osm_comparison.csv"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    comparison.to_csv(
        comparison_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # Print results
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("ABLATION RESULTS")
    print("=" * 80)

    print(
        results.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("LEAKAGE + OSM COMPARISON")
    print("=" * 80)

    print(
        comparison.to_string(
            index=False
        )
    )

    print(
        "\nSaved:"
    )

    print(
        results_path
    )

    print(
        comparison_path
    )


if __name__ == "__main__":
    main()