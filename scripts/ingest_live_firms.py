from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import text

PROJECT_ROOT = Path(r"C:\SIH26162")
ENV_PATH = PROJECT_ROOT / ".env"

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "FIRMS"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"

BOUNDARY_PATH = DATA_EXTERNAL_DIR / "countries.geojson"
BOUNDARY_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/"
    "master/data/countries.geojson"
)

NASA_BASE = "https://firms.modaps.eosdis.nasa.gov/api"
SOURCES = ("VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT")

# Coarse India-area request box. Exact filtering is done locally with a
# country polygon after download.
AREA_BBOX = "68,6,98,38.5"
GRID_SIZE = 0.01
MAX_DAYS_PER_REQUEST = 5

# This numerical mapping already exists in the repository feature pipeline.
# It is an observation-quality score mapping, NOT a model confidence.
CONFIDENCE_MAP = {"l": 30.0, "n": 50.0, "h": 80.0}


def die(message: str) -> None:
    raise SystemExit(message)


def request_with_retry(
    session: requests.Session,
    url: str,
    *,
    timeout: int = 90,
    attempts: int = 3,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after {attempts} attempts: {last_error}")


def parse_csv_response(response: requests.Response) -> pd.DataFrame:
    body = response.text.strip()
    if not body:
        return pd.DataFrame()

    # FIRMS may occasionally return a plain-text informational/error body.
    first_line = body.splitlines()[0].lower()
    if "," not in first_line:
        raise RuntimeError(f"Unexpected FIRMS response: {body[:300]}")

    try:
        return pd.read_csv(StringIO(body))
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def get_common_availability(
    session: requests.Session,
    key: str,
) -> tuple[date, date]:
    url = f"{NASA_BASE}/data_availability/csv/{key}/ALL"
    response = request_with_retry(session, url, timeout=60)
    availability = parse_csv_response(response)

    required = {"data_id", "min_date", "max_date"}
    if not required.issubset(availability.columns):
        die(
            "NASA availability response is missing columns: "
            + ", ".join(sorted(required - set(availability.columns)))
        )

    rows = availability[availability["data_id"].isin(SOURCES)].copy()
    if set(rows["data_id"]) != set(SOURCES):
        die(
            "One or more required VIIRS sources are unavailable: "
            + ", ".join(SOURCES)
        )

    rows["min_date"] = pd.to_datetime(rows["min_date"]).dt.date
    rows["max_date"] = pd.to_datetime(rows["max_date"]).dt.date

    # Use the shared date window so both sensors contribute over the same
    # observation period.
    start = max(rows["min_date"])
    end = min(rows["max_date"])

    if start > end:
        die("The selected VIIRS sources have no overlapping date range.")

    return start, end


def download_boundary(session: requests.Session) -> None:
    DATA_EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    if BOUNDARY_PATH.exists() and BOUNDARY_PATH.stat().st_size > 1000:
        return

    print("Downloading public country boundary dataset...")
    response = request_with_retry(session, BOUNDARY_URL, timeout=120)
    BOUNDARY_PATH.write_bytes(response.content)


def find_india_geometry() -> dict:
    payload = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))

    for feature in payload.get("features", []):
        props = feature.get("properties", {}) or {}

        code_values = [
            props.get("ISO_A3"),
            props.get("iso_a3"),
            props.get("ADM0_A3"),
            props.get("adm0_a3"),
        ]
        name_values = [
            props.get("ADMIN"),
            props.get("admin"),
            props.get("NAME"),
            props.get("name"),
        ]

        codes = {str(v).upper() for v in code_values if v is not None}
        names = {str(v).strip().lower() for v in name_values if v is not None}

        if "IND" in codes or "india" in names:
            geometry = feature.get("geometry")
            if geometry:
                return geometry

    die("Could not locate India in the boundary dataset.")


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    j = len(ring) - 1

    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]

        intersects = ((yi > y) != (yj > y)) and (
            x
            < (xj - xi) * (y - yi) / ((yj - yi) if (yj - yi) != 0 else 1e-15)
            + xi
        )

        if intersects:
            inside = not inside

        j = i

    return inside


def point_in_polygon(
    x: float,
    y: float,
    polygon: list[list[list[float]]],
) -> bool:
    if not polygon:
        return False

    if not point_in_ring(x, y, polygon[0]):
        return False

    # Holes remove points from the polygon.
    for hole in polygon[1:]:
        if point_in_ring(x, y, hole):
            return False

    return True


def point_in_geometry(x: float, y: float, geometry: dict) -> bool:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        return point_in_polygon(x, y, coords)

    if geom_type == "MultiPolygon":
        return any(point_in_polygon(x, y, poly) for poly in coords)

    raise RuntimeError(f"Unsupported boundary geometry type: {geom_type}")


def fetch_source(
    session: requests.Session,
    key: str,
    source: str,
    start: date,
    end: date,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    cursor = start

    while cursor <= end:
        remaining = (end - cursor).days + 1
        day_range = min(MAX_DAYS_PER_REQUEST, remaining)

        url = (
            f"{NASA_BASE}/area/csv/{key}/{source}/"
            f"{AREA_BBOX}/{day_range}/{cursor.isoformat()}"
        )

        print(
            f"  {source}: {cursor.isoformat()} "
            f"for {day_range} day(s)..."
        )

        response = request_with_retry(session, url)
        frame = parse_csv_response(response)

        if not frame.empty:
            frame["source_dataset"] = source
            frames.append(frame)

        cursor += timedelta(days=day_range)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def normalize_viirs(raw: pd.DataFrame) -> pd.DataFrame:
    required = {
        "latitude",
        "longitude",
        "bright_ti4",
        "bright_ti5",
        "acq_date",
        "acq_time",
        "satellite",
        "confidence",
        "frp",
        "daynight",
        "source_dataset",
    }

    missing = required - set(raw.columns)
    if missing:
        die(
            "VIIRS data is missing required columns: "
            + ", ".join(sorted(missing))
        )

    df = raw.copy()

    for col in (
        "latitude",
        "longitude",
        "bright_ti4",
        "bright_ti5",
        "frp",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["acq_date"] = pd.to_datetime(df["acq_date"], errors="coerce")

    conf_raw = df["confidence"].astype(str).str.strip().str.lower()
    conf_numeric = pd.to_numeric(df["confidence"], errors="coerce")
    df["confidence_score"] = conf_raw.map(CONFIDENCE_MAP)
    df["confidence_score"] = df["confidence_score"].fillna(conf_numeric)

    df["is_day"] = (df["daynight"].astype(str).str.upper() == "D").astype(int)
    df["is_night"] = (df["daynight"].astype(str).str.upper() == "N").astype(int)

    df = df.dropna(
        subset=[
            "latitude",
            "longitude",
            "bright_ti4",
            "bright_ti5",
            "frp",
            "acq_date",
            "confidence_score",
        ]
    ).copy()

    # Normalize current VIIRS API names to the repository's thermal feature
    # names. This does not fabricate a "type" field, which current API rows
    # do not provide.
    df["brightness"] = df["bright_ti4"]
    df["bright_t31"] = df["bright_ti5"]

    dedupe_cols = [
        "latitude",
        "longitude",
        "acq_date",
        "acq_time",
        "satellite",
        "frp",
        "source_dataset",
    ]
    df = df.drop_duplicates(subset=dedupe_cols).reset_index(drop=True)

    return df


def clip_to_india(
    df: pd.DataFrame,
    geometry: dict,
) -> pd.DataFrame:
    mask = [
        point_in_geometry(float(lon), float(lat), geometry)
        for lat, lon in zip(df["latitude"], df["longitude"])
    ]
    return df.loc[mask].copy().reset_index(drop=True)


def make_grid_id(lat: pd.Series, lon: pd.Series) -> pd.Series:
    # Match the existing repository convention: rounded grid values converted
    # to strings without forcing trailing zeroes.
    return (
        lat.round(4).astype(str)
        + "_"
        + lon.round(4).astype(str)
    )


def aggregate_spatial(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()

    work["lat_grid"] = (
        (work["latitude"] / GRID_SIZE).round() * GRID_SIZE
    ).round(4)
    work["lon_grid"] = (
        (work["longitude"] / GRID_SIZE).round() * GRID_SIZE
    ).round(4)
    work["grid_id"] = make_grid_id(work["lat_grid"], work["lon_grid"])

    grouped = (
        work.groupby("grid_id", as_index=False)
        .agg(
            lat_grid=("lat_grid", "first"),
            lon_grid=("lon_grid", "first"),
            observation_count=("latitude", "size"),
            first_seen=("acq_date", "min"),
            last_seen=("acq_date", "max"),
            active_days=("acq_date", "nunique"),
            day_observations=("is_day", "sum"),
            night_observations=("is_night", "sum"),
            mean_frp=("frp", "mean"),
            max_frp=("frp", "max"),
            std_frp=("frp", lambda s: float(s.std(ddof=0))),
            mean_brightness=("brightness", "mean"),
            max_brightness=("brightness", "max"),
            mean_bright_t31=("bright_t31", "mean"),
            max_bright_t31=("bright_t31", "max"),
            mean_confidence_score=("confidence_score", "mean"),
        )
    )

    grouped["persistence_days"] = (
        (grouped["last_seen"] - grouped["first_seen"]).dt.days + 1
    )
    grouped["recurrence_ratio"] = (
        grouped["active_days"] / grouped["persistence_days"]
    )
    grouped["obs_per_active_day"] = (
        grouped["observation_count"] / grouped["active_days"]
    )
    grouped["night_ratio"] = (
        grouped["night_observations"] / grouped["observation_count"]
    )

    # Current FIRMS web-service rows used here do not expose the old "type"
    # field. Leave these unknown instead of inventing zeros.
    grouped["type_2_count"] = pd.NA
    grouped["type_2_ratio"] = pd.NA

    # Live observations are not ground-truth labels. Keep heuristic targets
    # unset; classification is handled separately by the model layer.
    grouped["target_persistent_source"] = pd.NA
    grouped["target_multiclass"] = pd.NA

    return grouped


def scalar_or_none(value):
    if value is None or value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def make_db_records(spatial: pd.DataFrame) -> list[dict]:
    records: list[dict] = []

    for row in spatial.to_dict(orient="records"):
        first_seen = pd.Timestamp(row["first_seen"]).date()
        last_seen = pd.Timestamp(row["last_seen"]).date()

        record = {
            "event_id": f"firms-{row['grid_id']}",
            "grid_id": str(row["grid_id"]),
            "latitude": float(row["lat_grid"]),
            "longitude": float(row["lon_grid"]),
            "observation_count": int(row["observation_count"]),
            "active_days": int(row["active_days"]),
            "first_seen": first_seen,
            "last_seen": last_seen,
            "persistence_days": int(row["persistence_days"]),
            "recurrence_ratio": float(row["recurrence_ratio"]),
            "obs_per_active_day": float(row["obs_per_active_day"]),
            "day_observations": int(row["day_observations"]),
            "night_observations": int(row["night_observations"]),
            "night_ratio": float(row["night_ratio"]),
            "mean_frp": float(row["mean_frp"]),
            "max_frp": float(row["max_frp"]),
            "std_frp": float(row["std_frp"]),
            "mean_brightness": float(row["mean_brightness"]),
            "max_brightness": float(row["max_brightness"]),
            "mean_bright_t31": float(row["mean_bright_t31"]),
            "max_bright_t31": float(row["max_bright_t31"]),
            "mean_confidence_score": float(row["mean_confidence_score"]),
            "type_2_count": None,
            "type_2_ratio": None,
            "target_persistent_source": None,
            "target_multiclass": None,
            "osm_context_available": False,
            "osm_feature_count": None,
            "osm_industrial_count": None,
            "osm_power_count": None,
            "osm_manmade_count": None,
            "osm_min_distance_m": None,
        }

        records.append(record)

    return records


def load_database(spatial: pd.DataFrame) -> int:
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.utils.database import engine

    upsert = text(
        """
        INSERT INTO thermal_events (
            event_id,
            grid_id,
            latitude,
            longitude,
            geom,
            observation_count,
            active_days,
            first_seen,
            last_seen,
            persistence_days,
            recurrence_ratio,
            obs_per_active_day,
            day_observations,
            night_observations,
            night_ratio,
            mean_frp,
            max_frp,
            std_frp,
            mean_brightness,
            max_brightness,
            mean_bright_t31,
            max_bright_t31,
            mean_confidence_score,
            type_2_count,
            type_2_ratio,
            target_persistent_source,
            target_multiclass,
            osm_context_available,
            osm_feature_count,
            osm_industrial_count,
            osm_power_count,
            osm_manmade_count,
            osm_min_distance_m
        )
        VALUES (
            :event_id,
            :grid_id,
            :latitude,
            :longitude,
            ST_SetSRID(
                ST_MakePoint(:longitude, :latitude),
                4326
            ),
            :observation_count,
            :active_days,
            :first_seen,
            :last_seen,
            :persistence_days,
            :recurrence_ratio,
            :obs_per_active_day,
            :day_observations,
            :night_observations,
            :night_ratio,
            :mean_frp,
            :max_frp,
            :std_frp,
            :mean_brightness,
            :max_brightness,
            :mean_bright_t31,
            :max_bright_t31,
            :mean_confidence_score,
            :type_2_count,
            :type_2_ratio,
            :target_persistent_source,
            :target_multiclass,
            :osm_context_available,
            :osm_feature_count,
            :osm_industrial_count,
            :osm_power_count,
            :osm_manmade_count,
            :osm_min_distance_m
        )
        ON CONFLICT (grid_id)
        DO UPDATE SET
            event_id = EXCLUDED.event_id,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            geom = EXCLUDED.geom,
            observation_count = EXCLUDED.observation_count,
            active_days = EXCLUDED.active_days,
            first_seen = EXCLUDED.first_seen,
            last_seen = EXCLUDED.last_seen,
            persistence_days = EXCLUDED.persistence_days,
            recurrence_ratio = EXCLUDED.recurrence_ratio,
            obs_per_active_day = EXCLUDED.obs_per_active_day,
            day_observations = EXCLUDED.day_observations,
            night_observations = EXCLUDED.night_observations,
            night_ratio = EXCLUDED.night_ratio,
            mean_frp = EXCLUDED.mean_frp,
            max_frp = EXCLUDED.max_frp,
            std_frp = EXCLUDED.std_frp,
            mean_brightness = EXCLUDED.mean_brightness,
            max_brightness = EXCLUDED.max_brightness,
            mean_bright_t31 = EXCLUDED.mean_bright_t31,
            max_bright_t31 = EXCLUDED.max_bright_t31,
            mean_confidence_score = EXCLUDED.mean_confidence_score,
            type_2_count = EXCLUDED.type_2_count,
            type_2_ratio = EXCLUDED.type_2_ratio,
            target_persistent_source = EXCLUDED.target_persistent_source,
            target_multiclass = EXCLUDED.target_multiclass,
            osm_context_available = EXCLUDED.osm_context_available,
            osm_feature_count = EXCLUDED.osm_feature_count,
            osm_industrial_count = EXCLUDED.osm_industrial_count,
            osm_power_count = EXCLUDED.osm_power_count,
            osm_manmade_count = EXCLUDED.osm_manmade_count,
            osm_min_distance_m = EXCLUDED.osm_min_distance_m;
        """
    )

    records = make_db_records(spatial)

    with engine.begin() as conn:
        # Replace the previous live-feed snapshot atomically.
        # If the transaction fails, PostgreSQL rolls this deletion back.
        conn.execute(
            text(
                "DELETE FROM thermal_events "
                "WHERE event_id LIKE 'firms-%'"
            )
        )

        chunk_size = 1000
        for start in range(0, len(records), chunk_size):
            chunk = records[start : start + chunk_size]
            conn.execute(upsert, chunk)
            print(
                f"  DB rows processed: "
                f"{min(start + chunk_size, len(records)):,}/{len(records):,}"
            )

        count = conn.execute(
            text("SELECT COUNT(*) FROM thermal_events WHERE event_id LIKE 'firms-%'")
        ).scalar_one()

    return int(count)


def verify_api() -> None:
    sys.path.insert(0, str(PROJECT_ROOT))
    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)

    print("\n=== FastAPI verification ===")

    for path in (
        "/api/health",
        "/api/hotspots/stats",
        "/api/hotspots?limit=3",
    ):
        response = client.get(path)
        print(path, "->", response.status_code)
        print(response.json())
        if response.status_code != 200:
            die(f"API verification failed for {path}")

    hotspot_response = client.get("/api/hotspots?limit=1")
    hotspots = hotspot_response.json()

    if hotspots:
        hotspot_id = hotspots[0]["id"]
        response = client.get(
            f"/api/hotspots/{hotspot_id}/classify"
        )
        print(
            f"/api/hotspots/{hotspot_id}/classify",
            "->",
            response.status_code,
        )
        print(response.json())

        if response.status_code != 200:
            die("Classification endpoint verification failed.")


def main() -> None:
    print("=== SIH26162 real FIRMS ingest ===")

    if not ENV_PATH.exists():
        die(f"Missing {ENV_PATH}")

    load_dotenv(dotenv_path=ENV_PATH)

    key = os.getenv("FIRMS_MAP_KEY")
    if not key:
        die("FIRMS_MAP_KEY is missing from .env")

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DATA_EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "SIH26162-Thermal-Intelligence/"
                "real-firms-ingest"
            )
        }
    )

    start, end = get_common_availability(session, key)

    print(
        "Common NOAA-20/NOAA-21 NRT window:",
        start.isoformat(),
        "to",
        end.isoformat(),
    )

    frames = []

    for source in SOURCES:
        frame = fetch_source(
            session,
            key,
            source,
            start,
            end,
        )
        print(f"  {source} downloaded rows: {len(frame):,}")
        if not frame.empty:
            frames.append(frame)

    if not frames:
        die("NASA returned no VIIRS observations.")

    raw = pd.concat(frames, ignore_index=True)
    normalized = normalize_viirs(raw)

    print(f"Combined normalized rows: {len(normalized):,}")

    download_boundary(session)
    india_geometry = find_india_geometry()

    india = clip_to_india(normalized, india_geometry)
    print(f"Rows after India polygon filter: {len(india):,}")

    if india.empty:
        die("No observations remained after India boundary filtering.")

    raw_path = (
        DATA_RAW_DIR
        / (
            "viirs_noaa20_noaa21_nrt_india_"
            f"{start.isoformat()}_{end.isoformat()}.csv"
        )
    )
    india.to_csv(raw_path, index=False)

    spatial = aggregate_spatial(india)

    processed_path = (
        DATA_PROCESSED_DIR
        / (
            "firms_live_spatial_features_"
            f"{start.isoformat()}_{end.isoformat()}.csv"
        )
    )
    spatial.to_csv(processed_path, index=False)

    print(f"Spatial grid cells: {len(spatial):,}")
    print(f"Saved raw FIRMS observations: {raw_path}")
    print(f"Saved live spatial features: {processed_path}")
    print(
        "Training path data/processed/firms_spatial_features.csv "
        "was intentionally NOT created."
    )
    print(
        "Reason: this live NRT dataset should not silently become the "
        "training dataset."
    )

    total_db_rows = load_database(spatial)

    print(f"\nTHERMAL_EVENTS_DB_ROWS={total_db_rows:,}")

    verify_api()

    print("\n=== INGEST COMPLETE ===")
    print("Real NASA FIRMS observations: LOADED")
    print("India polygon filtering: APPLIED")
    print("Synthetic OSM values: NOT USED")
    print("OSM availability in inserted rows: FALSE / unknown")
    print("Weak-label targets in inserted rows: NULL")
    print("Model artifact: unchanged")


if __name__ == "__main__":
    main()
