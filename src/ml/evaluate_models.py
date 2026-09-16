from __future__ import annotations

import json

import joblib
import pandas as pd

from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from src.ml.config import MODELS_DIR
from src.ml.data_loader import load_dataset
from src.ml.feature_engineering import build_features
from src.ml.splitting import spatial_train_val_test_split


CLASS_NAMES = {
    0: "vegetation_agricultural",
    1: "industrial_fire_candidate",
    2: "persistent_thermal_source",
    3: "other_ephemeral",
}


MODEL_NAMES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "hist_gradient_boosting",
    "xgboost",
]


def evaluate_model(
    name: str,
    model,
    X: pd.DataFrame,
    y: pd.Series,
) -> dict:
    """Evaluate a trained model."""

    predictions = model.predict(X)

    macro_f1 = f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    balanced_accuracy = (
        balanced_accuracy_score(
            y,
            predictions,
        )
    )

    report = classification_report(
        y,
        predictions,
        labels=[0, 1, 2, 3],
        target_names=[
            CLASS_NAMES[0],
            CLASS_NAMES[1],
            CLASS_NAMES[2],
            CLASS_NAMES[3],
        ],
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y,
        predictions,
        labels=[0, 1, 2, 3],
    )

    return {
        "model": name,
        "macro_f1": float(macro_f1),
        "balanced_accuracy": float(
            balanced_accuracy
        ),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }


def main():

    print("Loading dataset...")

    df = load_dataset()

    X, y = build_features(df)

    data = df.copy()

    data["_row_index"] = range(
        len(data)
    )

    _, validation_df, _ = (
        spatial_train_val_test_split(data)
    )

    validation_indices = (
        validation_df["_row_index"]
    )

    X_val = X.loc[
        validation_indices
    ]

    y_val = y.loc[
        validation_indices
    ]

    all_results = {}

    for name in MODEL_NAMES:

        model_path = (
            MODELS_DIR
            / f"{name}_baseline.joblib"
        )

        print("\n" + "=" * 70)
        print(
            f"EVALUATING: {name}"
        )
        print("=" * 70)

        if not model_path.exists():

            print(
                "WARNING: Model not found:",
                model_path,
            )

            continue

        model = joblib.load(
            model_path
        )

        result = evaluate_model(
            name,
            model,
            X_val,
            y_val,
        )

        all_results[name] = result

        print(
            f"Macro F1: "
            f"{result['macro_f1']:.4f}"
        )

        print(
            f"Balanced Accuracy: "
            f"{result['balanced_accuracy']:.4f}"
        )

        print(
            "\nPer-class results:"
        )

        report = result[
            "classification_report"
        ]

        for class_id, class_name in (
            CLASS_NAMES.items()
        ):

            metrics = report[
                class_name
            ]

            print(
                f"  {class_name}: "
                f"precision="
                f"{metrics['precision']:.4f}, "
                f"recall="
                f"{metrics['recall']:.4f}, "
                f"F1="
                f"{metrics['f1-score']:.4f}, "
                f"support="
                f"{int(metrics['support'])}"
            )

        print(
            "\nConfusion Matrix:"
        )

        matrix_df = pd.DataFrame(
            result[
                "confusion_matrix"
            ],
            index=[
                CLASS_NAMES[i]
                for i in range(4)
            ],
            columns=[
                CLASS_NAMES[i]
                for i in range(4)
            ],
        )

        print(matrix_df)

    output_path = (
        MODELS_DIR
        / "detailed_validation_results.json"
    )

    output_path.write_text(
        json.dumps(
            all_results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "\nDetailed results saved:",
        output_path,
    )


if __name__ == "__main__":
    main()
