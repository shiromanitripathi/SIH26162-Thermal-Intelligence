from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Project root / import path
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.geospatial.osm_overpass import (
    DEFAULT_RADIUS_M,
    DEFAULT_TILE_SIZE_DEG,
    calculate_osm_context,
    fetch_tile,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FIRMS_GRID = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "firms_spatial_features.csv"
)

OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "osm_context_features_real.csv"
)

CACHE_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "osm_cache_real"
)

CONTEXT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "osm_context_tiles"
)

MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "osm_tile_manifest.csv"
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OSM_CONTEXT_COLUMNS = [
    "grid_id",
    "lat_grid",
    "lon_grid",
    "osm_feature_count",
    "osm_industrial_count",
    "osm_power_count",
    "osm_manmade_count",
    "osm_min_distance_m",
]



# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

MANIFEST_COLUMNS = [
    "tile_id",
    "south",
    "west",
    "north",
    "east",
    "status",
    "feature_count",
    "firms_cell_count",
    "endpoint",
    "timestamp",
    "error",
]


def ensure_manifest() -> None:
    MANIFEST.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if MANIFEST.exists():
        return

    with MANIFEST.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=MANIFEST_COLUMNS,
        )
        writer.writeheader()


def load_manifest() -> pd.DataFrame:
    ensure_manifest()

    manifest = pd.read_csv(MANIFEST)

    if manifest.empty:
        return pd.DataFrame(
            columns=MANIFEST_COLUMNS
        )

    manifest["tile_id"] = (
        manifest["tile_id"].astype(str)
    )

    return manifest


def record_manifest(
    *,
    tile_id: str,
    south: float,
    west: float,
    north: float,
    east: float,
    status: str,
    feature_count: int,
    firms_cell_count: int,
    endpoint: str,
    error: str = "",
) -> None:

    ensure_manifest()

    row = {
        "tile_id": tile_id,
        "south": south,
        "west": west,
        "north": north,
        "east": east,
        "status": status,
        "feature_count": feature_count,
        "firms_cell_count": firms_cell_count,
        "endpoint": endpoint,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "error": error,
    }

    with MANIFEST.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=MANIFEST_COLUMNS,
        )
        writer.writerow(row)


def get_latest_manifest_status(
    manifest: pd.DataFrame,
) -> dict[str, str]:

    if manifest.empty:
        return {}

    latest = (
        manifest
        .sort_values("timestamp")
        .drop_duplicates(
            subset="tile_id",
            keep="last",
        )
    )

    return dict(
        zip(
            latest["tile_id"].astype(str),
            latest["status"].astype(str),
        )
    )


# ---------------------------------------------------------------------------
# FIRMS
# ---------------------------------------------------------------------------

def load_firms_grid() -> pd.DataFrame:

    if not FIRMS_GRID.exists():
        raise FileNotFoundError(
            f"FIRMS grid not found: {FIRMS_GRID}"
        )

    grid = pd.read_csv(FIRMS_GRID)

    required = {
        "grid_id",
        "lat_grid",
        "lon_grid",
        "observation_count",
    }

    missing = required - set(grid.columns)

    if missing:
        raise ValueError(
            f"Missing FIRMS columns: {sorted(missing)}"
        )

    grid["grid_id"] = (
        grid["grid_id"].astype(str)
    )

    for column in [
        "lat_grid",
        "lon_grid",
        "observation_count",
    ]:
        grid[column] = pd.to_numeric(
            grid[column],
            errors="coerce",
        )

    if grid[
        ["grid_id", "lat_grid", "lon_grid"]
    ].isna().any().any():

        raise ValueError(
            "FIRMS grid contains invalid "
            "grid identifiers or coordinates."
        )

    if grid["grid_id"].duplicated().any():
        raise ValueError(
            "FIRMS grid contains duplicate grid_id values."
        )

    return grid


# ---------------------------------------------------------------------------
# Tile generation
# ---------------------------------------------------------------------------

def build_active_tiles(
    grid: pd.DataFrame,
    minimum_observations: int,
) -> pd.DataFrame:

    active = grid[
        grid["observation_count"]
        >= minimum_observations
    ].copy()

    if active.empty:
        raise ValueError(
            "No FIRMS cells satisfy "
            "the observation threshold."
        )

    tile_size = DEFAULT_TILE_SIZE_DEG

    active["tile_south"] = (
        active["lat_grid"]
        .floordiv(tile_size)
        * tile_size
    )

    active["tile_west"] = (
        active["lon_grid"]
        .floordiv(tile_size)
        * tile_size
    )

    tiles = (
        active[
            [
                "tile_south",
                "tile_west",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "tile_south",
                "tile_west",
            ]
        )
        .reset_index(drop=True)
    )

    tiles["tile_north"] = (
        tiles["tile_south"]
        + tile_size
    )

    tiles["tile_east"] = (
        tiles["tile_west"]
        + tile_size
    )

    tiles["tile_id"] = (
        tiles["tile_south"]
        .map(lambda x: f"{x:.6f}")
        + "_"
        + tiles["tile_west"]
        .map(lambda x: f"{x:.6f}")
    )

    return tiles[
        [
            "tile_id",
            "tile_south",
            "tile_west",
            "tile_north",
            "tile_east",
        ]
    ]


def sample_tiles_geographically(
    tiles: pd.DataFrame,
    sample_size: int,
) -> pd.DataFrame:

    """
    Select approximately evenly distributed tiles across
    the complete geographic extent.

    Existing completed tiles are NOT removed here; the resume
    logic later skips them automatically.
    """

    if sample_size >= len(tiles):
        return tiles.copy()

    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than zero."
        )

    # -----------------------------------------------------------------------
    # We divide the ordered geographic tile list into approximately equal
    # intervals and select one tile from each interval.
    #
    # Because tiles are sorted by latitude then longitude, this spreads the
    # sample across the full geographic extent rather than taking only the
    # first N southern tiles.
    # -----------------------------------------------------------------------

    positions = (
        pd.Series(
            range(sample_size)
        )
        * (len(tiles) - 1)
        / (sample_size - 1)
        if sample_size > 1
        else pd.Series([0])
    )

    positions = (
        positions
        .round()
        .astype(int)
        .tolist()
    )

    sampled = (
        tiles
        .iloc[positions]
        .drop_duplicates(
            subset="tile_id"
        )
        .reset_index(drop=True)
    )

    return sampled


# ---------------------------------------------------------------------------
# Context tile storage
# ---------------------------------------------------------------------------

def context_path(tile_id: str) -> Path:

    CONTEXT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        CONTEXT_DIR
        / f"tile_{tile_id}.csv"
    )


def save_context_tile(
    tile_id: str,
    context: pd.DataFrame,
) -> None:

    path = context_path(tile_id)
    temporary = path.with_suffix(".tmp")

    context.to_csv(
        temporary,
        index=False,
    )

    temporary.replace(path)


def load_context_tile(
    tile_id: str,
) -> pd.DataFrame | None:

    path = context_path(tile_id)

    if not path.exists():
        return None

    try:
        context = pd.read_csv(path)

        if "grid_id" not in context.columns:
            return None

        return context

    except Exception:
        return None


# ---------------------------------------------------------------------------
# FIRMS cells in tile
# ---------------------------------------------------------------------------

def get_tile_grid(
    grid: pd.DataFrame,
    south: float,
    west: float,
    north: float,
    east: float,
) -> pd.DataFrame:

    return grid[
        (grid["lat_grid"] >= south)
        & (grid["lat_grid"] < north)
        & (grid["lon_grid"] >= west)
        & (grid["lon_grid"] < east)
    ][
        [
            "grid_id",
            "lat_grid",
            "lon_grid",
        ]
    ].copy()


# ---------------------------------------------------------------------------
# Final assembly
# ---------------------------------------------------------------------------

def assemble_final_output(
    grid: pd.DataFrame | None = None,
) -> None:

    print()
    print("=" * 70)
    print("ASSEMBLING FINAL OSM DATASET")
    print("=" * 70)

    if grid is None:
        grid = load_firms_grid()

    files = sorted(
        CONTEXT_DIR.glob("tile_*.csv")
    )

    print(
        f"Context tile files found: "
        f"{len(files):,}"
    )

    frames = []

    for path in files:

        try:
            frame = pd.read_csv(path)

            if frame.empty:
                continue

            missing = (
                set(OSM_CONTEXT_COLUMNS)
                - set(frame.columns)
            )

            if missing:
                print(
                    f"Skipping {path.name}: "
                    f"missing {sorted(missing)}"
                )
                continue

            frames.append(
                frame[OSM_CONTEXT_COLUMNS]
            )

        except Exception as exc:

            print(
                f"Skipping corrupt file "
                f"{path.name}: {exc}"
            )

    if frames:

        osm_context = pd.concat(
            frames,
            ignore_index=True,
        )

        osm_context = (
            osm_context
            .drop_duplicates(
                subset="grid_id",
                keep="last",
            )
        )

    else:

        osm_context = pd.DataFrame(
            columns=OSM_CONTEXT_COLUMNS
        )

    osm_context["grid_id"] = (
        osm_context["grid_id"].astype(str)
    )

    # -----------------------------------------------------------------------
    # CRITICAL:
    # Start from the complete FIRMS grid.
    # -----------------------------------------------------------------------

    result = grid[
        [
            "grid_id",
            "lat_grid",
            "lon_grid",
        ]
    ].copy()

    result["grid_id"] = (
        result["grid_id"].astype(str)
    )

    result = result.merge(
        osm_context[
            [
                "grid_id",
                "osm_feature_count",
                "osm_industrial_count",
                "osm_power_count",
                "osm_manmade_count",
                "osm_min_distance_m",
            ]
        ],
        on="grid_id",
        how="left",
        validate="one_to_one",
        indicator="_osm_merge",
    )

    result["osm_context_available"] = result["_osm_merge"].eq("both")
    result = result.drop(columns=["_osm_merge"])

    count_columns = [
        "osm_feature_count",
        "osm_industrial_count",
        "osm_power_count",
        "osm_manmade_count",
    ]

    for column in count_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        ).astype("Int64")

    result["osm_min_distance_m"] = pd.to_numeric(
        result["osm_min_distance_m"],
        errors="coerce",
    )

    result = (
        result
        .sort_values("grid_id")
        .reset_index(drop=True)
    )

    # -----------------------------------------------------------------------
    # Integrity checks
    # -----------------------------------------------------------------------

    if len(result) != len(grid):
        raise RuntimeError(
            "Final OSM dataset row count does not "
            "match the FIRMS grid."
        )

    if result["grid_id"].duplicated().any():
        raise RuntimeError(
            "Final OSM dataset contains duplicate grid_id values."
        )

    osm_value_columns = [
        "osm_feature_count",
        "osm_industrial_count",
        "osm_power_count",
        "osm_manmade_count",
        "osm_min_distance_m",
    ]

    available = result["osm_context_available"]

    if result.loc[available, osm_value_columns].isna().any().any():
        raise RuntimeError(
            "Queried OSM context rows contain missing values."
        )

    if result.loc[~available, osm_value_columns].notna().any().any():
        raise RuntimeError(
            "Unqueried OSM rows contain fabricated context values."
        )

    # -----------------------------------------------------------------------
    # Atomic save
    # -----------------------------------------------------------------------

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = OUTPUT.with_suffix(".tmp")

    result.to_csv(
        temporary,
        index=False,
    )

    temporary.replace(OUTPUT)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print()
    print(
        f"FIRMS cells: "
        f"{len(grid):,}"
    )

    print(
        f"Final rows: "
        f"{len(result):,}"
    )

    print(
        f"Queried OSM context cells: "
        f"{int(result.osm_context_available.sum()):,}"
    )

    print(
        f"Industrial: "
        f"{int((result['osm_industrial_count'] > 0).sum()):,}"
    )

    print(
        f"Power: "
        f"{int((result['osm_power_count'] > 0).sum()):,}"
    )

    print(
        f"Man-made: "
        f"{int((result['osm_manmade_count'] > 0).sum()):,}"
    )

    print(
        f"Unqueried OSM context cells: "
        f"{int((~result.osm_context_available).sum()):,}"
    )

    print()
    print(f"Saved: {OUTPUT}")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def run(
    minimum_observations: int,
    max_tiles: int | None,
    sample_tiles: int | None,
) -> None:

    print("=" * 70)
    print("SIH26162 REAL OSM EXTRACTION")
    print("=" * 70)

    print(
        f"Minimum observations: "
        f"{minimum_observations}"
    )

    print(
        f"Tile size: "
        f"{DEFAULT_TILE_SIZE_DEG}°"
    )

    print(
        f"Radius: "
        f"{DEFAULT_RADIUS_M} m"
    )

    print()
    print("Loading FIRMS grid...")

    grid = load_firms_grid()

    print(
        f"Total FIRMS cells: "
        f"{len(grid):,}"
    )

    print()
    print("Building active tile index...")

    tiles = build_active_tiles(
        grid,
        minimum_observations,
    )

    print(
        f"Active tiles: "
        f"{len(tiles):,}"
    )

    # -----------------------------------------------------------------------
    # Geographic sampling
    # -----------------------------------------------------------------------

    if sample_tiles is not None:

        original_count = len(tiles)

        tiles = sample_tiles_geographically(
            tiles,
            sample_tiles,
        )

        print(
            f"Geographic sample: "
            f"{len(tiles):,} / "
            f"{original_count:,} tiles"
        )

    elif max_tiles is not None:

        tiles = (
            tiles
            .head(max_tiles)
            .copy()
        )

        print(
            f"Test limit: "
            f"{len(tiles):,} tiles"
        )

    manifest = load_manifest()

    latest_status = (
        get_latest_manifest_status(
            manifest
        )
    )

    successful = {
        tile_id
        for tile_id, status
        in latest_status.items()
        if status == "success"
    }

    print(
        f"Previously successful: "
        f"{len(successful):,}"
    )

    # -----------------------------------------------------------------------
    # Process tiles
    # -----------------------------------------------------------------------

    for position, row in enumerate(
        tiles.itertuples(index=False),
        start=1,
    ):

        tile_id = row.tile_id

        print()
        print("=" * 70)
        print(
            f"TILE {position}/{len(tiles)}: "
            f"{tile_id}"
        )
        print("=" * 70)

        # ---------------------------------------------------------------
        # Already completed
        # ---------------------------------------------------------------

        existing_context = (
            load_context_tile(tile_id)
        )

        if (
            tile_id in successful
            and existing_context is not None
        ):

            print(
                "Context already saved. "
                "Skipping tile."
            )

            continue

        if tile_id in successful:

            print(
                "Manifest says success but "
                "context file is missing/invalid."
            )

        # ---------------------------------------------------------------
        # FIRMS cells
        # ---------------------------------------------------------------

        tile_grid = get_tile_grid(
            grid,
            row.tile_south,
            row.tile_west,
            row.tile_north,
            row.tile_east,
        )

        if tile_grid.empty:

            print(
                "No FIRMS cells in tile. "
                "Skipping."
            )

            continue

        center_lat = (
            row.tile_south
            + row.tile_north
        ) / 2

        center_lon = (
            row.tile_west
            + row.tile_east
        ) / 2

        # ---------------------------------------------------------------
        # Fetch OSM
        # ---------------------------------------------------------------

        try:

            (
                fetched_tile_id,
                osm_df,
                endpoint,
            ) = fetch_tile(
                latitude=center_lat,
                longitude=center_lon,
                cache_dir=CACHE_DIR,
                tile_size_deg=DEFAULT_TILE_SIZE_DEG,
                radius_m=DEFAULT_RADIUS_M,
            )

            if fetched_tile_id != tile_id:
                raise RuntimeError(
                    f"Tile ID mismatch: "
                    f"{fetched_tile_id} != {tile_id}"
                )

            # -----------------------------------------------------------
            # Calculate context
            # -----------------------------------------------------------

            context = calculate_osm_context(
                tile_grid,
                osm_df,
                radius_m=DEFAULT_RADIUS_M,
            )

            # -----------------------------------------------------------
            # Save immediately
            # -----------------------------------------------------------

            save_context_tile(
                tile_id,
                context,
            )

            record_manifest(
                tile_id=tile_id,
                south=row.tile_south,
                west=row.tile_west,
                north=row.tile_north,
                east=row.tile_east,
                status="success",
                feature_count=len(osm_df),
                firms_cell_count=len(tile_grid),
                endpoint=endpoint,
            )

            successful.add(tile_id)

            print(
                f"FIRMS cells: "
                f"{len(tile_grid):,}"
            )

            print(
                f"OSM objects: "
                f"{len(osm_df):,}"
            )

            print(
                "Context saved immediately."
            )

        except KeyboardInterrupt:

            print()
            print(
                "Extraction interrupted."
            )

            print(
                "Completed tiles are preserved."
            )

            break

        except Exception as exc:

            print()
            print(
                f"TILE FAILED: {exc}"
            )

            record_manifest(
                tile_id=tile_id,
                south=row.tile_south,
                west=row.tile_west,
                north=row.tile_north,
                east=row.tile_east,
                status="failed",
                feature_count=0,
                firms_cell_count=len(tile_grid),
                endpoint="",
                error=str(exc),
            )

            print(
                "Continuing to next tile..."
            )

    # -----------------------------------------------------------------------
    # Always assemble current context
    # -----------------------------------------------------------------------

    assemble_final_output(grid)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Extract real OSM context "
            "for SIH26162 FIRMS cells."
        )
    )

    parser.add_argument(
        "--min-observations",
        type=int,
        default=2,
        help=(
            "Only create OSM tiles containing "
            "FIRMS cells with at least this many observations."
        ),
    )

    parser.add_argument(
        "--max-tiles",
        type=int,
        default=None,
        help=(
            "Process only the first N geographically "
            "sorted tiles. Useful for small tests."
        ),
    )

    parser.add_argument(
        "--sample-tiles",
        type=int,
        default=None,
        help=(
            "Select N geographically distributed tiles "
            "across the complete active tile set."
        ),
    )

    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help=(
            "Only assemble existing context "
            "tile files into the final CSV."
        ),
    )

    args = parser.parse_args()

    if (
        args.max_tiles is not None
        and args.sample_tiles is not None
    ):
        parser.error(
            "Use either --max-tiles or "
            "--sample-tiles, not both."
        )

    if args.assemble_only:

        assemble_final_output()

        return

    run(
        minimum_observations=args.min_observations,
        max_tiles=args.max_tiles,
        sample_tiles=args.sample_tiles,
    )


if __name__ == "__main__":
    main()