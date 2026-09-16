from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from src.ml.config import RANDOM_STATE
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


# ---------------------------------------------------------------------
# Features used in the leakage-reduced experiment
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
# Load real OSM
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

    duplicate_ids = (
        osm["grid_id"]
        .duplicated()
        .sum()
    )

    if duplicate_ids:
        raise ValueError(
            f"Duplicate OSM grid IDs detected: {duplicate_ids}"
        )

    print(
        f"OSM coverage: {len(osm):,} grid cells"
    )

    return osm


# ---------------------------------------------------------------------
# Train model
# ---------------------------------------------------------------------

def train_model(
    name,
    model,
    X_train,
    y_train,
):

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

    training_time = round(
        time.time() - start,
        2,
    )

    return model, training_time


# ---------------------------------------------------------------------
# Evaluate model on untouched test set
# ---------------------------------------------------------------------

def evaluate_model(
    name,
    model,
    X_test,
    y_test,
    training_time,
):

    predictions = model.predict(
        X_test
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    balanced_accuracy = balanced_accuracy_score(
        y_test,
        predictions,
    )

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1, 2, 3],
    )

    print(
        f"\n{name}"
    )

    print(
        f"Macro F1: "
        f"{macro_f1:.4f}"
    )

    print(
        f"Balanced Accuracy: "
        f"{balanced_accuracy:.4f}"
    )

    print(
        f"Training time: "
        f"{training_time:.2f}s"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(
        cm
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2, 3],
            target_names=[
                "class_0",
                "class_1",
                "class_2",
                "class_3",
            ],
            zero_division=0,
        )
    )

    return {
        "model": name,
        "macro_f1": macro_f1,
        "balanced_accuracy": balanced_accuracy,
        "training_seconds": training_time,
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    print("=" * 80)
    print("HELD-OUT TEST EVALUATION")
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
        f"Full feature count: {X.shape[1]}"
    )

    # ---------------------------------------------------------------
    # Preserve row indices
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
    # Use exact FIRMS/OSM overlap
    # ---------------------------------------------------------------

    data = data[
        data["grid_id"].isin(
            osm_grid_ids
        )
    ].copy()

    print(
        f"Matched FIRMS/OSM cells: "
        f"{len(data):,}"
    )

    firms_grid_ids = set(
        data["grid_id"]
    )

    if firms_grid_ids != osm_grid_ids:

        raise ValueError(
            "FIRMS and OSM grid IDs do not match exactly."
        )

    # ---------------------------------------------------------------
    # Create ONE spatial split
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

    print(
        f"Train cells: "
        f"{len(train_df):,}"
    )

    print(
        f"Validation cells: "
        f"{len(val_df):,}"
    )

    print(
        f"Test cells: "
        f"{len(test_df):,}"
    )

    # ---------------------------------------------------------------
    # Verify no spatial overlap
    # ---------------------------------------------------------------

    train_ids = set(
        train_df["grid_id"]
    )

    val_ids = set(
        val_df["grid_id"]
    )

    test_ids = set(
        test_df["grid_id"]
    )

    assert not (
        train_ids & val_ids
    )

    assert not (
        train_ids & test_ids
    )

    assert not (
        val_ids & test_ids
    )

    print(
        "Spatial separation verified."
    )

    # ---------------------------------------------------------------
    # Indices
    # ---------------------------------------------------------------

    train_idx = train_df[
        "_row_index"
    ]

    val_idx = val_df[
        "_row_index"
    ]

    test_idx = test_df[
        "_row_index"
    ]

    y_train = y.loc[
        train_idx
    ]

    y_val = y.loc[
        val_idx
    ]

    y_test = y.loc[
        test_idx
    ]

    # ---------------------------------------------------------------
    # IMPORTANT:
    # Validation set is retained but NOT used for final test metrics.
    #
    # We train on TRAIN + VALIDATION after the development stage.
    # The TEST set remains untouched until final evaluation.
    # ---------------------------------------------------------------

    development_idx = pd.Index(
        list(train_idx) +
        list(val_idx)
    )

    y_development = y.loc[
        development_idx
    ]

    # ---------------------------------------------------------------
    # Full FIRMS features
    # ---------------------------------------------------------------

    X_full_development = X.loc[
        development_idx
    ].copy()

    X_full_test = X.loc[
        test_idx
    ].copy()

    # ---------------------------------------------------------------
    # Leakage-reduced FIRMS features
    # ---------------------------------------------------------------

    X_reduced_development = (
        X_full_development.drop(
            columns=LEAKAGE_REDUCED_REMOVED_FEATURES
        )
    )

    X_reduced_test = (
        X_full_test.drop(
            columns=LEAKAGE_REDUCED_REMOVED_FEATURES
        )
    )

    # ---------------------------------------------------------------
    # OSM features
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

    test_grid_ids = test_df[
        "grid_id"
    ].tolist()

    X_osm_development = (
        osm_indexed.loc[
            development_grid_ids,
            OSM_FEATURES,
        ].copy()
    )

    X_osm_test = (
        osm_indexed.loc[
            test_grid_ids,
            OSM_FEATURES,
        ].copy()
    )

    X_osm_development.index = (
        development_idx
    )

    X_osm_test.index = (
        test_idx
    )

    # ---------------------------------------------------------------
    # Leakage-reduced FIRMS + OSM
    # ---------------------------------------------------------------

    X_reduced_osm_development = pd.concat(
        [
            X_reduced_development,
            X_osm_development,
        ],
        axis=1,
    )

    X_reduced_osm_test = pd.concat(
        [
            X_reduced_test,
            X_osm_test,
        ],
        axis=1,
    )

    # ---------------------------------------------------------------
    # Experiments
    # ---------------------------------------------------------------

    experiments = {

        "full_firms": (
            X_full_development,
            X_full_test,
        ),

        "leakage_reduced_firms": (
            X_reduced_development,
            X_reduced_test,
        ),

        "leakage_reduced_firms_osm": (
            X_reduced_osm_development,
            X_reduced_osm_test,
        ),
    }

    # ---------------------------------------------------------------
    # Verify matrices
    # ---------------------------------------------------------------

    for experiment_name, (
        X_development,
        X_test,
    ) in experiments.items():

        if X_development.isnull().any().any():

            raise ValueError(
                f"NaN values found in "
                f"{experiment_name} development data."
            )

        if X_test.isnull().any().any():

            raise ValueError(
                f"NaN values found in "
                f"{experiment_name} test data."
            )

        if len(X_development) != len(
            y_development
        ):

            raise ValueError(
                f"Development size mismatch "
                f"for {experiment_name}."
            )

        if len(X_test) != len(
            y_test
        ):

            raise ValueError(
                f"Test size mismatch "
                f"for {experiment_name}."
            )

    # ---------------------------------------------------------------
    # Train and evaluate
    # ---------------------------------------------------------------

    all_results = []

    for experiment_name, (
        X_development,
        X_test,
    ) in experiments.items():

        print("\n" + "=" * 80)

        print(
            f"TEST EXPERIMENT: "
            f"{experiment_name}"
        )

        print("=" * 80)

        print(
            f"Development features: "
            f"{X_development.shape[1]}"
        )

        print(
            f"Development cells: "
            f"{len(X_development):,}"
        )

        print(
            f"Untouched test cells: "
            f"{len(X_test):,}"
        )

        models = build_models()

        for name, model in models.items():

            print(
                f"\nTraining {name} "
                f"on development set..."
            )

            trained_model, training_time = (
                train_model(
                    name,
                    model,
                    X_development,
                    y_development,
                )
            )

            result = evaluate_model(
                name,
                trained_model,
                X_test,
                y_test,
                training_time,
            )

            result[
                "experiment"
            ] = experiment_name

            result[
                "feature_count"
            ] = X_development.shape[1]

            result[
                "test_cells"
            ] = len(X_test)

            all_results.append(
                result
            )

    # ---------------------------------------------------------------
    # Save results
    # ---------------------------------------------------------------

    results = pd.DataFrame(
        all_results
    )

    results = results[
        [
            "experiment",
            "model",
            "feature_count",
            "test_cells",
            "macro_f1",
            "balanced_accuracy",
            "training_seconds",
        ]
    ]

    output_dir = Path(
        "models"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "held_out_test_results.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("HELD-OUT TEST RESULTS")
    print("=" * 80)

    print(
        results.to_string(
            index=False
        )
    )

    print(
        f"\nSaved: {output_path}"
    )


if __name__ == "__main__":
    main()