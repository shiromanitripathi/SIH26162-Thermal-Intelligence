import pandas as pd
from pathlib import Path

from src.ml.config import FIRMS_FEATURES, TARGET
from src.ml.splitting import spatial_train_val_test_split
from src.ml.train_models import build_models, train_and_evaluate


FIRMS_PATH = Path("data/processed/firms_spatial_features.csv")
OSM_DIR = Path("data/processed/osm_context_tiles")
OUTPUT_PATH = Path("data/processed/firms_vs_osm_comparison.csv")

OSM_FEATURES = [
    "osm_feature_count",
    "osm_industrial_count",
    "osm_power_count",
    "osm_manmade_count",
    "osm_min_distance_m",
]


def load_real_osm_context():
    """Load and validate all persisted real OSM context tiles."""

    required = [
        "grid_id",
        *OSM_FEATURES,
    ]

    files = sorted(OSM_DIR.glob("tile_*.csv"))

    if len(files) != 468:
        raise ValueError(
            f"Expected 468 persisted OSM tiles, found {len(files)}"
        )

    frames = []

    for path in files:
        df = pd.read_csv(path)

        if df.empty:
            raise ValueError(f"Empty OSM context file: {path}")

        missing = [col for col in required if col not in df.columns]

        if missing:
            raise ValueError(
                f"{path} is missing required columns: {missing}"
            )

        if not df["grid_id"].is_unique:
            raise ValueError(
                f"Duplicate grid IDs inside OSM file: {path}"
            )

        frames.append(df[required])

    osm = pd.concat(frames, ignore_index=True)

    if osm["grid_id"].duplicated().any():
        raise ValueError(
            "Duplicate grid IDs found across OSM context files."
        )

    return osm


def main():
    print("=" * 70)
    print("CONTROLLED FIRMS vs FIRMS + REAL OSM EXPERIMENT")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load FIRMS and persisted OSM context
    # ---------------------------------------------------------

    firms = pd.read_csv(FIRMS_PATH)
    osm = load_real_osm_context()

    firms["grid_id"] = firms["grid_id"].astype(str)
    osm["grid_id"] = osm["grid_id"].astype(str)

    covered_ids = set(osm["grid_id"])

    # ---------------------------------------------------------
    # 2. Create exact matched population
    # ---------------------------------------------------------

    covered = firms[
        firms["grid_id"].isin(covered_ids)
    ].copy()

    if len(covered) != len(osm):
        raise ValueError(
            f"Coverage mismatch: FIRMS={len(covered)}, OSM={len(osm)}"
        )

    data = covered.merge(
        osm,
        on="grid_id",
        how="inner",
        validate="one_to_one",
    )

    if len(data) != 67273:
        raise ValueError(
            f"Expected 67273 matched cells, got {len(data)}"
        )

    if data["grid_id"].duplicated().any():
        raise ValueError("Duplicate grid IDs after merge.")

    print(f"\nVerified matched cells: {len(data)}")

    # ---------------------------------------------------------
    # 3. Verify feature definitions
    # ---------------------------------------------------------

    print("\nFIRMS features:")
    print(f"Count: {len(FIRMS_FEATURES)}")
    print(FIRMS_FEATURES)

    print("\nOSM features:")
    print(f"Count: {len(OSM_FEATURES)}")
    print(OSM_FEATURES)

    if len(FIRMS_FEATURES) != 18:
        raise ValueError(
            f"Expected 18 FIRMS features, found {len(FIRMS_FEATURES)}"
        )

    if len(OSM_FEATURES) != 5:
        raise ValueError(
            f"Expected 5 OSM features, found {len(OSM_FEATURES)}"
        )

    # ---------------------------------------------------------
    # 4. Create ONE spatial split for BOTH experiments
    # ---------------------------------------------------------

    train, validation, test = spatial_train_val_test_split(
        data,
        random_state=42,
    )

    print("\nSpatial split:")
    print(f"Train:      {len(train)}")
    print(f"Validation: {len(validation)}")
    print(f"Test:       {len(test)}")

    # Verify no cell appears in multiple splits.
    train_ids = set(train["grid_id"])
    val_ids = set(validation["grid_id"])
    test_ids = set(test["grid_id"])

    if train_ids & val_ids:
        raise ValueError("Train/validation grid overlap detected.")

    if train_ids & test_ids:
        raise ValueError("Train/test grid overlap detected.")

    if val_ids & test_ids:
        raise ValueError("Validation/test grid overlap detected.")

    if len(train) + len(validation) + len(test) != len(data):
        raise ValueError(
            "Split does not preserve the complete population."
        )

    print("Cell separation: VERIFIED")

    # ---------------------------------------------------------
    # 5. Prepare SAME cells for both experiments
    # ---------------------------------------------------------

    X_train_firms = train[FIRMS_FEATURES]
    X_val_firms = validation[FIRMS_FEATURES]

    X_train_osm = train[FIRMS_FEATURES + OSM_FEATURES]
    X_val_osm = validation[FIRMS_FEATURES + OSM_FEATURES]

    y_train = train[TARGET]
    y_val = validation[TARGET]

    print("\nControlled comparison setup:")
    print(
        "FIRMS-only cells:     ",
        len(train) + len(validation) + len(test),
    )
    print(
        "FIRMS + OSM cells:    ",
        len(train) + len(validation) + len(test),
    )
    print("Same spatial split:    VERIFIED")
    print("Same target:           VERIFIED")
    print("FIRMS features:        18")
    print("OSM features added:    5")
    print("Combined features:     23")

    # ---------------------------------------------------------
    # 6. Train identical models
    # ---------------------------------------------------------

    results = []

    print("\n" + "=" * 70)
    print("EXPERIMENT A: FIRMS ONLY")
    print("=" * 70)

    for name, model in build_models().items():

        trained_model, result = train_and_evaluate(
            name,
            model,
            X_train_firms,
            y_train,
            X_val_firms,
            y_val,
        )

        result["experiment"] = "FIRMS_ONLY"
        results.append(result)

    print("\n" + "=" * 70)
    print("EXPERIMENT B: FIRMS + REAL OSM")
    print("=" * 70)

    for name, model in build_models().items():

        trained_model, result = train_and_evaluate(
            name,
            model,
            X_train_osm,
            y_train,
            X_val_osm,
            y_val,
        )

        result["experiment"] = "FIRMS_PLUS_OSM"
        results.append(result)

    # ---------------------------------------------------------
    # 7. Create comparison table
    # ---------------------------------------------------------

    results_df = pd.DataFrame(results)

    comparison = results_df.pivot(
        index="model",
        columns="experiment",
        values=[
            "macro_f1",
            "balanced_accuracy",
            "training_seconds",
        ],
    )

    comparison.columns = [
        "_".join(col).lower()
        for col in comparison.columns
    ]

    comparison = comparison.reset_index()

    comparison["macro_f1_delta"] = (
        comparison["macro_f1_firms_plus_osm"]
        - comparison["macro_f1_firms_only"]
    )

    comparison["balanced_accuracy_delta"] = (
        comparison["balanced_accuracy_firms_plus_osm"]
        - comparison["balanced_accuracy_firms_only"]
    )

    comparison["training_seconds_delta"] = (
        comparison["training_seconds_firms_plus_osm"]
        - comparison["training_seconds_firms_only"]
    )

    comparison.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ---------------------------------------------------------
    # 8. Print results
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    print(comparison.to_string(index=False))

    print(f"\nSaved comparison to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()