from pathlib import Path
import pandas as pd

from src.ml.config import SPATIAL_DATASET, TARGET, FIRMS_FEATURES, TARGET_COLUMNS


REQUIRED_COLUMNS = (
    ["grid_id", "lat_grid", "lon_grid"]
    + FIRMS_FEATURES
    + TARGET_COLUMNS
)


def load_dataset(path: Path = SPATIAL_DATASET) -> pd.DataFrame:
    """Load the FIRMS spatial feature dataset and validate its schema."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing)
        )

    return df


def validate_dataset(df: pd.DataFrame) -> dict:
    """Run structural and numerical quality checks."""

    report = {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_grid_ids": int(df["grid_id"].duplicated().sum()),
        "missing_values": int(df.isna().sum().sum()),
        "infinite_values": int(
            df.select_dtypes(include="number")
            .isin([float("inf"), float("-inf")])
            .sum()
            .sum()
        ),
        "target_distribution": df[TARGET].value_counts().sort_index().to_dict(),
    }

    return report


def get_features_and_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Return strictly separated model features and target."""

    X = df[FIRMS_FEATURES].copy()
    y = df[TARGET].copy()

    return X, y


if __name__ == "__main__":
    data = load_dataset()
    report = validate_dataset(data)

    print("=== DATASET VALIDATION ===")
    for key, value in report.items():
        print(f"{key}: {value}")

    X, y = get_features_and_target(data)

    print("\n=== MODEL DATA ===")
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("Features:", X.columns.tolist())
