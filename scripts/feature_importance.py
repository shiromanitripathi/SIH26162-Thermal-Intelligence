from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from src.ml.config import RANDOM_STATE
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


# ---------------------------------------------------------------------
# Features removed because they are directly or indirectly involved
# in constructing the heuristic target.
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
# Load real OSM context
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
            f"No OSM tile files found in {osm_dir}"
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

    if osm["grid_id"].duplicated().any():

        duplicate_count = (
            osm["grid_id"]
            .duplicated()
            .sum()
        )

        raise ValueError(
            f"Duplicate OSM grid IDs detected: "
            f"{duplicate_count}"
        )

    print(
        f"OSM coverage: {len(osm):,} grid cells"
    )

    return osm


# ---------------------------------------------------------------------
# Build XGBoost model
# ---------------------------------------------------------------------

def build_xgboost():

    return XGBClassifier(
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


# ---------------------------------------------------------------------
# Class weights
# ---------------------------------------------------------------------

def class_weights(y):

    counts = y.value_counts()

    total = len(y)

    n_classes = len(counts)

    weights = {
        cls: total / (n_classes * count)
        for cls, count in counts.items()
    }

    return y.map(weights)


# ---------------------------------------------------------------------
# Train model
# ---------------------------------------------------------------------

def train_xgboost(X_train, y_train):

    model = build_xgboost()

    model.fit(
        X_train,
        y_train,
        sample_weight=class_weights(y_train),
    )

    return model


# ---------------------------------------------------------------------
# Extract feature importance
# ---------------------------------------------------------------------

def get_feature_importance(
    model,
    feature_names,
):

    importance = model.feature_importances_

    result = pd.DataFrame({
        "feature": feature_names,
        "importance": importance,
    })

    result = result.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)

    total = result["importance"].sum()

    if total > 0:

        result["importance_percent"] = (
            result["importance"] / total
        ) * 100

    else:

        result["importance_percent"] = 0.0

    return result


# ---------------------------------------------------------------------
# Save and print feature importance
# ---------------------------------------------------------------------

def save_importance(
    result,
    name,
):

    output_dir = Path(
        "models"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{name}_feature_importance.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved: {output_path}"
    )

    print(
        "\nFeature importance:"
    )

    print(
        result.to_string(
            index=False
        )
    )

    return output_path


# ---------------------------------------------------------------------
# Plot feature importance
# ---------------------------------------------------------------------

def plot_importance(
    result,
    name,
):

    plot_data = result.copy()

    plot_data = plot_data.sort_values(
        "importance"
    )

    plt.figure(
        figsize=(10, 6)
    )

    plt.barh(
        plot_data["feature"],
        plot_data["importance"],
    )

    plt.xlabel(
        "XGBoost Feature Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.title(
        f"Feature Importance - {name}"
    )

    plt.tight_layout()

    output_dir = Path(
        "models"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{name}_feature_importance.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved plot: {output_path}"
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print("XGBOOST FEATURE IMPORTANCE ANALYSIS")
    print("=" * 80)

    # ---------------------------------------------------------------
    # Load FIRMS
    # ---------------------------------------------------------------

    print(
        "\nLoading FIRMS spatial dataset..."
    )

    df = load_dataset()

    X, y = build_features(
        df
    )

    print(
        f"FIRMS cells: {len(df):,}"
    )

    print(
        f"Full FIRMS features: {X.shape[1]}"
    )

    # ---------------------------------------------------------------
    # Preserve row index
    # ---------------------------------------------------------------

    data = df.copy()

    data["_row_index"] = range(
        len(data)
    )

    # ---------------------------------------------------------------
    # Load real OSM
    # ---------------------------------------------------------------

    osm = load_real_osm()

    osm_grid_ids = set(
        osm["grid_id"]
    )

    # ---------------------------------------------------------------
    # Exact FIRMS/OSM overlap
    # ---------------------------------------------------------------

    data = data[
        data["grid_id"].isin(
            osm_grid_ids
        )
    ].copy()

    if len(data) != len(osm):

        raise ValueError(
            "FIRMS and OSM overlap size mismatch."
        )

    firms_grid_ids = set(
        data["grid_id"]
    )

    if firms_grid_ids != osm_grid_ids:

        raise ValueError(
            "FIRMS and OSM grid IDs do not match exactly."
        )

    print(
        f"Matched cells: {len(data):,}"
    )

    # ---------------------------------------------------------------
    # SAME spatial split used previously
    # ---------------------------------------------------------------

    train_df, val_df, test_df = (
        spatial_train_val_test_split(
            data,
            random_state=RANDOM_STATE,
        )
    )

    train_idx = train_df[
        "_row_index"
    ]

    val_idx = val_df[
        "_row_index"
    ]

    test_idx = test_df[
        "_row_index"
    ]

    development_idx = pd.Index(
        list(train_idx) +
        list(val_idx)
    )

    print(
        f"Development cells: "
        f"{len(development_idx):,}"
    )

    print(
        f"Untouched test cells: "
        f"{len(test_idx):,}"
    )

    # ---------------------------------------------------------------
    # Target
    # ---------------------------------------------------------------

    y_development = y.loc[
        development_idx
    ]

    # ---------------------------------------------------------------
    # Full FIRMS
    # ---------------------------------------------------------------

    X_full_development = X.loc[
        development_idx
    ].copy()

    # ---------------------------------------------------------------
    # Leakage-reduced FIRMS
    # ---------------------------------------------------------------

    X_reduced_development = (
        X_full_development.drop(
            columns=LEAKAGE_REDUCED_REMOVED_FEATURES
        )
    )

    # ---------------------------------------------------------------
    # OSM development features
    # ---------------------------------------------------------------

    osm_indexed = osm.set_index(
        "grid_id"
    )

    development_grid_ids = data.loc[
        data["_row_index"].isin(
            development_idx
        ),
        "grid_id",
    ].tolist()

    X_osm_development = (
        osm_indexed.loc[
            development_grid_ids,
            OSM_FEATURES,
        ].copy()
    )

    X_osm_development.index = (
        development_idx
    )

    # ---------------------------------------------------------------
    # Reduced FIRMS + OSM
    # ---------------------------------------------------------------

    X_reduced_osm_development = pd.concat(
        [
            X_reduced_development,
            X_osm_development,
        ],
        axis=1,
    )

    # ---------------------------------------------------------------
    # Experiments
    # ---------------------------------------------------------------

    experiments = {

        "leakage_reduced_firms": (
            X_reduced_development,
        ),

        "leakage_reduced_firms_osm": (
            X_reduced_osm_development,
        ),
    }

    # ---------------------------------------------------------------
    # Train and calculate importance
    # ---------------------------------------------------------------

    for experiment_name, (
        X_train,
    ) in experiments.items():

        print("\n" + "=" * 80)

        print(
            f"EXPERIMENT: "
            f"{experiment_name}"
        )

        print("=" * 80)

        print(
            f"Feature count: "
            f"{X_train.shape[1]}"
        )

        print(
            "Training XGBoost..."
        )

        model = train_xgboost(
            X_train,
            y_development,
        )

        result = get_feature_importance(
            model,
            X_train.columns,
        )

        save_importance(
            result,
            experiment_name,
        )

        plot_importance(
            result,
            experiment_name,
        )

    # ---------------------------------------------------------------
    # Compare OSM importance
    # ---------------------------------------------------------------

    firms_path = Path(
        "models/"
        "leakage_reduced_firms_feature_importance.csv"
    )

    osm_path = Path(
        "models/"
        "leakage_reduced_firms_osm_feature_importance.csv"
    )

    if firms_path.exists() and osm_path.exists():

        firms_result = pd.read_csv(
            firms_path
        )

        osm_result = pd.read_csv(
            osm_path
        )

        osm_only = osm_result[
            osm_result["feature"].isin(
                OSM_FEATURES
            )
        ].copy()

        print("\n" + "=" * 80)
        print("OSM FEATURE IMPORTANCE")
        print("=" * 80)

        if len(osm_only) > 0:

            print(
                osm_only.to_string(
                    index=False
                )
            )

        else:

            print(
                "No OSM features found."
            )

        # -----------------------------------------------------------
        # Save combined comparison
        # -----------------------------------------------------------

        comparison = osm_result.merge(
            firms_result[
                [
                    "feature",
                    "importance",
                    "importance_percent",
                ]
            ],
            on="feature",
            how="left",
            suffixes=(
                "_osm",
                "_firms",
            ),
        )

        comparison_path = Path(
            "models/"
            "feature_importance_comparison.csv"
        )

        comparison.to_csv(
            comparison_path,
            index=False,
        )

        print(
            f"\nSaved comparison: "
            f"{comparison_path}"
        )


if __name__ == "__main__":
    main()