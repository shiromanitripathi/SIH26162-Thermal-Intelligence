from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Project root / import path
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from src.geospatial.osm_overpass import fetch_tile


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CACHE_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "osm_cache_real"
)

TEST_LATITUDE = 10.01
TEST_LONGITUDE = 76.74

TILE_SIZE_DEG = 0.25
RADIUS_M = 2000


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("SIH26162 REAL OSM OVERPASS PILOT")
    print("=" * 70)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Test latitude: {TEST_LATITUDE}")
    print(f"Test longitude: {TEST_LONGITUDE}")
    print(f"Tile size    : {TILE_SIZE_DEG} degrees")
    print(f"Search radius: {RADIUS_M} meters")
    print(f"Cache dir    : {CACHE_DIR}")

    print()
    print("-" * 70)
    print("Starting OSM request...")
    print("-" * 70)

    try:
        tile_id, osm_df, endpoint = fetch_tile(
            latitude=TEST_LATITUDE,
            longitude=TEST_LONGITUDE,
            cache_dir=CACHE_DIR,
            tile_size_deg=TILE_SIZE_DEG,
            radius_m=RADIUS_M,
        )

    except Exception as exc:
        print()
        print("=" * 70)
        print("OSM PILOT FAILED")
        print("=" * 70)
        print(f"Error type: {type(exc).__name__}")
        print(f"Error     : {exc}")
        print("=" * 70)

        raise SystemExit(1)

    # -----------------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------------

    print()
    print("=" * 70)
    print("OSM PILOT RESULT")
    print("=" * 70)

    print(f"Tile ID        : {tile_id}")
    print(f"Endpoint       : {endpoint}")
    print(f"OSM objects    : {len(osm_df):,}")

    if not osm_df.empty:

        print()
        print("Columns:")
        print(", ".join(osm_df.columns))

        print()
        print("First 10 OSM objects:")

        display_columns = [
            column
            for column in [
                "osm_id",
                "latitude",
                "longitude",
                "tags",
            ]
            if column in osm_df.columns
        ]

        print(
            osm_df[
                display_columns
            ]
            .head(10)
            .to_string(index=False)
        )

    else:
        print()
        print("No matching OSM objects were returned.")

    print()
    print(f"Cache directory:")
    print(CACHE_DIR)

    print()
    print("=" * 70)
    print("PILOT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()