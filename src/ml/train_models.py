from __future__ import annotations

import json
import time

import joblib
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from src.ml.config import (
    MODELS_DIR,
    RANDOM_STATE,
    TARGET,
)
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


MODEL_NAMES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "hist_gradient_boosting",
    "xgboost",
]


def build_models() -> dict:
    """Create the five benchmark classifiers."""

    return {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
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


def compute_sample_weights(
    y: pd.Series,
) -> pd.Series:
    """Create inverse-frequency class weights."""

    counts = y.value_counts()
    total = len(y)
    n_classes = len(counts)

    weights = {
        cls: total / (n_classes * count)
        for cls, count in counts.items()
    }

    return y.map(weights)


def train_and_evaluate(
    name: str,
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
):
    """Train one model and evaluate it on validation data."""

    print("\n" + "=" * 60)
    print(f"TRAINING: {name}")
    print("=" * 60)

    start_time = time.time()

    if name in {
        "xgboost",
        "hist_gradient_boosting",
    }:
        sample_weights = compute_sample_weights(
            y_train
        )

        model.fit(
            X_train,
            y_train,
            sample_weight=sample_weights,
        )

    else:
        model.fit(
            X_train,
            y_train,
        )

    training_time = time.time() - start_time

    predictions = model.predict(X_val)

    macro_f1 = f1_score(
        y_val,
        predictions,
        average="macro",
        zero_division=0,
    )

    balanced_accuracy = balanced_accuracy_score(
        y_val,
        predictions,
    )

    result = {
        "model": name,
        "macro_f1": float(macro_f1),
        "balanced_accuracy": float(
            balanced_accuracy
        ),
        "training_seconds": round(
            training_time,
            2,
        ),
    }

    print(
        f"Macro F1:          "
        f"{macro_f1:.4f}"
    )

    print(
        f"Balanced Accuracy:  "
        f"{balanced_accuracy:.4f}"
    )

    print(
        f"Training Time:      "
        f"{training_time:.2f}s"
    )

    return model, result


def main():

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading dataset...")

    df = load_dataset()

    print("Building features...")

    X, y = build_features(df)

    # Preserve original row positions so that
    # spatial splitting and feature matrices remain aligned.
    data = df.copy()

    data["_row_index"] = range(
        len(data)
    )

    train_df, validation_df, test_df = (
        spatial_train_val_test_split(data)
    )

    train_indices = train_df[
        "_row_index"
    ]

    validation_indices = validation_df[
        "_row_index"
    ]

    test_indices = test_df[
        "_row_index"
    ]

    X_train = X.loc[train_indices]
    y_train = y.loc[train_indices]

    X_val = X.loc[validation_indices]
    y_val = y.loc[validation_indices]

    X_test = X.loc[test_indices]
    y_test = y.loc[test_indices]

    print("\n=== DATA SPLITS ===")

    print(
        "Train:",
        X_train.shape,
    )

    print(
        "Validation:",
        X_val.shape,
    )

    print(
        "Test:",
        X_test.shape,
    )

    models = build_models()

    results = []

    for name in MODEL_NAMES:

        model = models[name]

        trained_model, result = (
            train_and_evaluate(
                name,
                model,
                X_train,
                y_train,
                X_val,
                y_val,
            )
        )

        results.append(result)

        model_path = (
            MODELS_DIR
            / f"{name}_baseline.joblib"
        )

        joblib.dump(
            trained_model,
            model_path,
        )

        print(
            "Saved:",
            model_path,
        )

    results_df = (
        pd.DataFrame(results)
        .sort_values(
            "macro_f1",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print(
        results_df[
            [
                "model",
                "macro_f1",
                "balanced_accuracy",
                "training_seconds",
            ]
        ].to_string(
            index=False
        )
    )

    results_path = (
        MODELS_DIR
        / "baseline_results.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    metadata = {
        "target": TARGET,
        "features": X.columns.tolist(),

        "train_rows": len(X_train),
        "validation_rows": len(X_val),
        "test_rows": len(X_test),

        "models": results,

        "test_evaluation_status":
            "untouched",

        "note": (
            "Validation metrics measure "
            "agreement with the current "
            "heuristic/weak-labeling scheme. "
            "They are not independent "
            "real-world ground-truth accuracy."
        ),
    }

    metadata_path = (
        MODELS_DIR
        / "baseline_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "\nSaved benchmark results:",
        results_path,
    )

    print(
        "Saved metadata:",
        metadata_path,
    )

    print(
        "\nBaseline training complete."
    )


if __name__ == "__main__":
    main()
