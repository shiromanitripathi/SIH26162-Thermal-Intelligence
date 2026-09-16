from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OSM_TILE_DIR = PROCESSED_DIR / "osm_context_tiles"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


REQUIRED_COLUMNS = [
    "grid_id",
    "osm_feature_count",
    "osm_industrial_count",
    "osm_power_count",
    "osm_manmade_count",
    "osm_min_distance_m",
]


def latest_live_file() -> Path:
    files = sorted(
        PROCESSED_DIR.glob(
            "firms_live_spatial_features_*.csv"
        )
    )

    if not files:
        raise FileNotFoundError(
            "Live FIRMS spatial dataset not found. "
            "Run scripts/ingest_live_firms.py first."
        )

    return files[-1]


def load_verified_osm(
    live_grid_ids: set[str],
) -> pd.DataFrame:

    tile_files = sorted(
        OSM_TILE_DIR.glob("tile_*.csv")
    )

    if not tile_files:
        raise FileNotFoundError(
            "No persisted real OSM context tiles found."
        )

    frames = []

    for path in tile_files:
        try:
            frame = pd.read_csv(path)
        except Exception as exc:
            print(
                f"Skipping unreadable tile "
                f"{path.name}: {exc}"
            )
            continue

        if not set(REQUIRED_COLUMNS).issubset(
            frame.columns
        ):
            continue

        frames.append(
            frame[REQUIRED_COLUMNS]
        )

    if not frames:
        raise RuntimeError(
            "No valid persisted OSM context rows found."
        )

    osm = pd.concat(
        frames,
        ignore_index=True,
    )

    osm["grid_id"] = (
        osm["grid_id"].astype(str)
    )

    osm = osm.drop_duplicates(
        "grid_id",
        keep="last",
    )

    return osm[
        osm["grid_id"].isin(live_grid_ids)
    ].copy()


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    from src.utils.database import engine

    live_path = latest_live_file()

    live = pd.read_csv(live_path)
    live["grid_id"] = live["grid_id"].astype(str)

    live_ids = set(live["grid_id"])

    verified = load_verified_osm(
        live_ids
    )

    records = []

    for row in verified.to_dict(
        orient="records"
    ):
        records.append(
            {
                "grid_id": str(row["grid_id"]),
                "osm_feature_count": int(
                    row["osm_feature_count"]
                ),
                "osm_industrial_count": int(
                    row["osm_industrial_count"]
                ),
                "osm_power_count": int(
                    row["osm_power_count"]
                ),
                "osm_manmade_count": int(
                    row["osm_manmade_count"]
                ),
                "osm_min_distance_m": float(
                    row["osm_min_distance_m"]
                ),
            }
        )

    reset_sql = text(
        """
        UPDATE thermal_events
        SET
            osm_context_available = FALSE,
            osm_feature_count = NULL,
            osm_industrial_count = NULL,
            osm_power_count = NULL,
            osm_manmade_count = NULL,
            osm_min_distance_m = NULL
        WHERE event_id LIKE 'firms-%';
        """
    )

    update_sql = text(
        """
        UPDATE thermal_events
        SET
            osm_context_available = TRUE,
            osm_feature_count = :osm_feature_count,
            osm_industrial_count = :osm_industrial_count,
            osm_power_count = :osm_power_count,
            osm_manmade_count = :osm_manmade_count,
            osm_min_distance_m = :osm_min_distance_m
        WHERE event_id LIKE 'firms-%'
          AND grid_id = :grid_id;
        """
    )

    verification_sql = text(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE event_id LIKE 'firms-%'
            ) AS live_total,

            COUNT(*) FILTER (
                WHERE event_id LIKE 'firms-%'
                  AND osm_context_available = TRUE
            ) AS verified_osm,

            COUNT(*) FILTER (
                WHERE event_id LIKE 'firms-%'
                  AND osm_context_available = FALSE
            ) AS osm_unavailable,

            COUNT(*) FILTER (
                WHERE event_id LIKE 'firms-%'
                  AND osm_context_available = FALSE
                  AND (
                      osm_feature_count IS NOT NULL
                      OR osm_industrial_count IS NOT NULL
                      OR osm_power_count IS NOT NULL
                      OR osm_manmade_count IS NOT NULL
                      OR osm_min_distance_m IS NOT NULL
                  )
            ) AS invalid_unknown_values

        FROM thermal_events;
        """
    )

    with engine.begin() as conn:
        conn.execute(reset_sql)

        if records:
            conn.execute(
                update_sql,
                records,
            )

        result = conn.execute(
            verification_sql
        ).mappings().one()

    print(
        "LIVE_GRID_CELLS=",
        len(live),
    )
    print(
        "VERIFIED_OSM_OVERLAP=",
        len(verified),
    )
    print(
        "OVERLAP_PERCENT=",
        round(
            len(verified)
            / len(live)
            * 100,
            2,
        ),
    )

    print(
        "DATABASE_OSM_PROVENANCE=",
        dict(result),
    )

    assert (
        result["verified_osm"]
        == len(verified)
    )

    assert (
        result["invalid_unknown_values"]
        == 0
    )

    print("OSM_PROVENANCE=PASS")


if __name__ == "__main__":
    main()
