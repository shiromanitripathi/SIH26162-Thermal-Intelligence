from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from src.ml.config import (
    RANDOM_STATE,
    SPATIAL_BLOCK_SIZE,
    TARGET,
)


def create_spatial_blocks(df: pd.DataFrame) -> pd.Series:
    """Assign each FIRMS grid cell to a macro spatial block."""

    lat_block = np.floor(
        df["lat_grid"] / SPATIAL_BLOCK_SIZE
    ).astype(int)

    lon_block = np.floor(
        df["lon_grid"] / SPATIAL_BLOCK_SIZE
    ).astype(int)

    return (
        lat_block.astype(str)
        + "_"
        + lon_block.astype(str)
    )


def spatial_train_val_test_split(
    df: pd.DataFrame,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create leakage-resistant spatial train/validation/test splits."""

    data = df.copy()
    data["_spatial_block"] = create_spatial_blocks(data)

    groups = data["_spatial_block"].values

    # First split: 80% development, 20% final test
    splitter_test = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=random_state,
    )

    train_val_idx, test_idx = next(
        splitter_test.split(data, groups=groups)
    )

    train_val = data.iloc[train_val_idx].copy()
    test = data.iloc[test_idx].copy()

    # Second split: 75% of development = 60% total train,
    # 25% of development = 20% total validation.
    splitter_val = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=random_state,
    )

    train_idx, val_idx = next(
        splitter_val.split(
            train_val,
            groups=train_val["_spatial_block"].values,
        )
    )

    train = train_val.iloc[train_idx].copy()
    validation = train_val.iloc[val_idx].copy()

    train = train.drop(columns="_spatial_block")
    validation = validation.drop(columns="_spatial_block")
    test = test.drop(columns="_spatial_block")

    return train, validation, test


def summarize_split(
    name: str,
    df: pd.DataFrame,
) -> None:
    """Print split size, class distribution and geographic extent."""

    counts = df[TARGET].value_counts().sort_index()
    proportions = (
        df[TARGET]
        .value_counts(normalize=True)
        .sort_index()
    )

    print(f"\n=== {name.upper()} ===")
    print("Rows:", len(df))
    print("Latitude range:", (
        round(df["lat_grid"].min(), 4),
        round(df["lat_grid"].max(), 4),
    ))
    print("Longitude range:", (
        round(df["lon_grid"].min(), 4),
        round(df["lon_grid"].max(), 4),
    ))

    print("Class distribution:")
    for class_id in counts.index:
        print(
            f"  Class {class_id}: "
            f"{counts[class_id]:,} "
            f"({proportions[class_id] * 100:.2f}%)"
        )


def verify_spatial_separation(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> None:
    """Verify that no macro spatial block crosses dataset splits."""

    train_blocks = set(create_spatial_blocks(train))
    validation_blocks = set(create_spatial_blocks(validation))
    test_blocks = set(create_spatial_blocks(test))

    train_val_overlap = train_blocks & validation_blocks
    train_test_overlap = train_blocks & test_blocks
    val_test_overlap = validation_blocks & test_blocks

    print("\n=== SPATIAL SEPARATION AUDIT ===")
    print("Train/Validation overlapping blocks:", len(train_val_overlap))
    print("Train/Test overlapping blocks:", len(train_test_overlap))
    print("Validation/Test overlapping blocks:", len(val_test_overlap))

    if (
        train_val_overlap
        or train_test_overlap
        or val_test_overlap
    ):
        raise RuntimeError(
            "Spatial leakage detected: at least one spatial block "
            "appears in multiple splits."
        )

    print("Spatial separation: PASS")


if __name__ == "__main__":
    from src.ml.data_loader import load_dataset

    df = load_dataset()

    print("Creating spatial train/validation/test split...")
    train, validation, test = spatial_train_val_test_split(df)

    summarize_split("Train", train)
    summarize_split("Validation", validation)
    summarize_split("Test", test)

    verify_spatial_separation(
        train,
        validation,
        test,
    )

    print("\n=== SPLIT RATIOS ===")
    total = len(df)

    print(f"Train:      {len(train):,} ({len(train) / total:.2%})")
    print(f"Validation: {len(validation):,} ({len(validation) / total:.2%})")
    print(f"Test:       {len(test):,} ({len(test) / total:.2%})")
    print(f"Total:      {len(train) + len(validation) + len(test):,}")
