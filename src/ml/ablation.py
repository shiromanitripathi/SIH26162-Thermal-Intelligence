from __future__ import annotations

import time

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

from src.ml.config import RANDOM_STATE, FIRMS_FEATURES, TARGET
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


REMOVED_FEATURES = [
    "active_days",
    "persistence_days",
    "night_ratio",
    "type_2_count",
]


def class_weights(y):
    counts = y.value_counts()
    total = len(y)
    n_classes = len(counts)

    return y.map({
        cls: total / (n_classes * count)
        for cls, count in counts.items()
    })


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


def main():

    print("Loading dataset...")

    df = load_dataset()

    X, y = build_features(df)

    data = df.copy()
    data["_row_index"] = range(len(data))

    train_df, val_df, _ = spatial_train_val_test_split(data)

    train_idx = train_df["_row_index"]
    val_idx = val_df["_row_index"]

    X_train_full = X.loc[train_idx]
    X_val_full = X.loc[val_idx]

    y_train = y.loc[train_idx]
    y_val = y.loc[val_idx]

    X_train_reduced = X_train_full.drop(
        columns=REMOVED_FEATURES
    )

    X_val_reduced = X_val_full.drop(
        columns=REMOVED_FEATURES
    )

    experiments = {
        "full_features": (
            X_train_full,
            X_val_full,
        ),
        "rule_features_removed": (
            X_train_reduced,
            X_val_reduced,
        ),
    }

    all_results = []

    for experiment_name, (
        X_train,
        X_val,
    ) in experiments.items():

        print("\n" + "=" * 70)
        print(
            f"EXPERIMENT: {experiment_name}"
        )
        print("=" * 70)

        print(
            "Features:",
            X_train.shape[1],
        )

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

            all_results.append(result)

            print(
                f"Macro F1: "
                f"{result['macro_f1']:.4f}"
            )

            print(
                f"Balanced Accuracy: "
                f"{result['balanced_accuracy']:.4f}"
            )

    results = pd.DataFrame(
        all_results
    )

    print("\n" + "=" * 70)
    print("ABLATION RESULTS")
    print("=" * 70)

    print(
        results[
            [
                "experiment",
                "model",
                "macro_f1",
                "balanced_accuracy",
                "training_seconds",
            ]
        ].to_string(index=False)
    )

    output = (
        "models/ablation_results.csv"
    )

    results.to_csv(
        output,
        index=False,
    )

    print(
        "\nSaved:",
        output,
    )


if __name__ == "__main__":
    main()
