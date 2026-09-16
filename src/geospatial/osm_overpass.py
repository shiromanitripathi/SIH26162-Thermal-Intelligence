from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from pyproj import Transformer
from scipy.spatial import cKDTree


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_TILE_SIZE_DEG = 0.25
DEFAULT_RADIUS_M = 2000
REQUEST_TIMEOUT = 60
MAX_RETRIES = 2

OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

OSM_TAG_QUERY = """
[out:json][timeout:45];
(
  nwr["landuse"="industrial"]({south},{west},{north},{east});
  nwr["industrial"]({south},{west},{north},{east});
  nwr["power"]({south},{west},{north},{east});
  nwr["man_made"]({south},{west},{north},{east});
  nwr["building"~"^(industrial|warehouse)$"]({south},{west},{north},{east});
);
out center;
"""

WGS84_TO_WEB_MERCATOR = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:3857",
    always_xy=True,
)


# ---------------------------------------------------------------------------
# Tile utilities
# ---------------------------------------------------------------------------

def get_tile_id(
    latitude: float,
    longitude: float,
    tile_size_deg: float = DEFAULT_TILE_SIZE_DEG,
) -> str:
    """Return a deterministic tile ID for a latitude/longitude."""

    tile_lat = math.floor(latitude / tile_size_deg) * tile_size_deg
    tile_lon = math.floor(longitude / tile_size_deg) * tile_size_deg

    return f"{tile_lat:.6f}_{tile_lon:.6f}"


def get_tile_bounds(
    latitude: float,
    longitude: float,
    tile_size_deg: float = DEFAULT_TILE_SIZE_DEG,
) -> tuple[float, float, float, float]:
    """
    Return tile bounds as:

        south, west, north, east
    """

    south = math.floor(latitude / tile_size_deg) * tile_size_deg
    west = math.floor(longitude / tile_size_deg) * tile_size_deg

    north = south + tile_size_deg
    east = west + tile_size_deg

    return south, west, north, east


def expand_bbox_meters(
    south: float,
    west: float,
    north: float,
    east: float,
    radius_m: float = DEFAULT_RADIUS_M,
) -> tuple[float, float, float, float]:
    """
    Expand a WGS84 bounding box approximately by radius_m.

    This is sufficient for our small 0.25-degree tiles.
    """

    center_lat = (south + north) / 2.0

    lat_deg_per_meter = 1.0 / 111_320.0

    lon_deg_per_meter = 1.0 / (
        111_320.0 * math.cos(math.radians(center_lat))
    )

    lat_delta = radius_m * lat_deg_per_meter
    lon_delta = radius_m * lon_deg_per_meter

    return (
        south - lat_delta,
        west - lon_delta,
        north + lat_delta,
        east + lon_delta,
    )


# ---------------------------------------------------------------------------
# Overpass query
# ---------------------------------------------------------------------------

def build_overpass_query(
    south: float,
    west: float,
    north: float,
    east: float,
) -> str:
    """Build the direct Overpass query."""

    return OSM_TAG_QUERY.format(
        south=f"{south:.6f}",
        west=f"{west:.6f}",
        north=f"{north:.6f}",
        east=f"{east:.6f}",
    )


# ---------------------------------------------------------------------------
# Cache utilities
# ---------------------------------------------------------------------------

def cache_path(
    cache_dir: Path,
    tile_id: str,
) -> Path:
    """Return JSON cache path for a tile."""

    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir / f"tile_{tile_id}.json"


def load_cached_tile(
    cache_dir: Path,
    tile_id: str,
) -> dict[str, Any] | None:
    """Load cached Overpass response if it exists."""

    path = cache_path(cache_dir, tile_id)

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def save_cached_tile(
    cache_dir: Path,
    tile_id: str,
    data: dict[str, Any],
) -> Path:
    """Save an Overpass response."""

    path = cache_path(cache_dir, tile_id)

    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    temporary_path.replace(path)

    return path


# ---------------------------------------------------------------------------
# Overpass request
# ---------------------------------------------------------------------------

def query_overpass(
    query: str,
    max_retries: int = MAX_RETRIES,
    timeout: int = REQUEST_TIMEOUT,
) -> tuple[dict[str, Any], str]:
    """
    Query Overpass with endpoint rotation and limited retries.

    Returns:
        response_json, endpoint_used
    """

    headers = {
        "User-Agent": (
            "SIH26162-Thermal-Intelligence/1.0 "
            "(research project; OpenStreetMap context extraction)"
        )
    }

    last_error: Exception | None = None

    for endpoint in OVERPASS_ENDPOINTS:
        for attempt in range(max_retries + 1):

            try:
                print(
                    f"  Overpass request: "
                    f"{endpoint} "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )

                response = requests.post(
                    endpoint,
                    data=query,
                    headers=headers,
                    timeout=timeout,
                )

                if response.status_code == 200:
                    return response.json(), endpoint

                if response.status_code in {
                    429,
                    502,
                    503,
                    504,
                }:
                    print(
                        f"  HTTP {response.status_code}; "
                        f"retrying..."
                    )
                    time.sleep(3)
                    continue

                response.raise_for_status()

            except (
                requests.Timeout,
                requests.ConnectionError,
                requests.RequestException,
            ) as exc:
                last_error = exc

                print(
                    f"  Request failed: {type(exc).__name__}"
                )

                if attempt < max_retries:
                    time.sleep(3)

    raise RuntimeError(
        f"All Overpass endpoints failed. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# OSM parsing
# ---------------------------------------------------------------------------

def element_to_record(
    element: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Convert one Overpass element to a compact point representation.

    'out center' provides center coordinates for ways/relations.
    """

    element_type = element.get("type")
    element_id = element.get("id")

    if element_type is None or element_id is None:
        return None

    tags = element.get("tags") or {}

    if element_type == "node":
        lat = element.get("lat")
        lon = element.get("lon")
    else:
        center = element.get("center") or {}

        lat = center.get("lat")
        lon = center.get("lon")

    if lat is None or lon is None:
        return None

    return {
        "osm_id": f"{element_type}:{element_id}",
        "latitude": float(lat),
        "longitude": float(lon),
        "tags": tags,
    }


def parse_overpass_elements(
    data: dict[str, Any],
) -> pd.DataFrame:
    """Convert Overpass JSON into a compact dataframe."""

    records: list[dict[str, Any]] = []

    for element in data.get("elements", []):
        record = element_to_record(element)

        if record is not None:
            records.append(record)

    if not records:
        return pd.DataFrame(
            columns=[
                "osm_id",
                "latitude",
                "longitude",
                "tags",
            ]
        )

    df = pd.DataFrame(records)

    # Defensive deduplication.
    df = df.drop_duplicates(subset="osm_id")

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_osm_feature(
    tags: dict[str, Any],
) -> dict[str, bool]:
    """
    Determine category membership.

    Categories are intentionally NOT mutually exclusive.
    """

    building = str(
        tags.get("building", "")
    ).lower()

    industrial = (
        str(tags.get("landuse", "")).lower() == "industrial"
        or "industrial" in tags
        or building in {"industrial", "warehouse"}
    )

    power = "power" in tags

    manmade = "man_made" in tags

    return {
        "industrial": industrial,
        "power": power,
        "manmade": manmade,
    }


def add_osm_categories(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add independent OSM category flags."""

    if df.empty:
        df["industrial"] = pd.Series(dtype=bool)
        df["power"] = pd.Series(dtype=bool)
        df["manmade"] = pd.Series(dtype=bool)

        return df

    categories = df["tags"].apply(
        classify_osm_feature
    )

    category_df = pd.DataFrame(
        categories.tolist(),
        index=df.index,
    )

    return pd.concat(
        [df, category_df],
        axis=1,
    )


# ---------------------------------------------------------------------------
# Distance calculations
# ---------------------------------------------------------------------------

def add_projected_coordinates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add Web Mercator coordinates for distance calculations."""

    if df.empty:
        df["x"] = pd.Series(dtype=float)
        df["y"] = pd.Series(dtype=float)

        return df

    x, y = WGS84_TO_WEB_MERCATOR.transform(
        df["longitude"].to_numpy(),
        df["latitude"].to_numpy(),
    )

    result = df.copy()

    result["x"] = x
    result["y"] = y

    return result


def calculate_osm_context(
    grid_df: pd.DataFrame,
    osm_df: pd.DataFrame,
    radius_m: float = DEFAULT_RADIUS_M,
) -> pd.DataFrame:
    """
    Calculate OSM context for FIRMS grid cells using a spatial KD-tree.

    Required grid columns:
        grid_id
        lat_grid
        lon_grid

    OSM context is calculated within radius_m of each FIRMS grid cell.
    """

    required = {
        "grid_id",
        "lat_grid",
        "lon_grid",
    }

    missing = required - set(grid_df.columns)

    if missing:
        raise ValueError(
            f"Missing grid columns: {sorted(missing)}"
        )

    output_columns = [
        "grid_id",
        "lat_grid",
        "lon_grid",
        "osm_feature_count",
        "osm_industrial_count",
        "osm_power_count",
        "osm_manmade_count",
        "osm_min_distance_m",
    ]

    if grid_df.empty:
        return pd.DataFrame(
            columns=output_columns
        )

    result = grid_df[
        ["grid_id", "lat_grid", "lon_grid"]
    ].copy()

    result["osm_feature_count"] = 0
    result["osm_industrial_count"] = 0
    result["osm_power_count"] = 0
    result["osm_manmade_count"] = 0
    result["osm_min_distance_m"] = float(radius_m)

    if osm_df.empty:
        return result[output_columns]

    # ------------------------------------------------------------------
    # Prepare OSM features
    # ------------------------------------------------------------------

    osm_work = add_osm_categories(osm_df)
    osm_work = add_projected_coordinates(osm_work)

    # ------------------------------------------------------------------
    # Prepare FIRMS grid coordinates
    # ------------------------------------------------------------------

    grid_work = grid_df[
        ["grid_id", "lat_grid", "lon_grid"]
    ].copy()

    grid_work = add_projected_coordinates(
        grid_work.rename(
            columns={
                "lat_grid": "latitude",
                "lon_grid": "longitude",
            }
        )
    )

    # ------------------------------------------------------------------
    # Build spatial index once.
    # ------------------------------------------------------------------

    osm_coordinates = osm_work[
        ["x", "y"]
    ].to_numpy(dtype=float)

    osm_tree = cKDTree(
        osm_coordinates
    )

    grid_coordinates = grid_work[
        ["x", "y"]
    ].to_numpy(dtype=float)

    # ------------------------------------------------------------------
    # Find all OSM objects within radius for every FIRMS cell.
    # ------------------------------------------------------------------

    nearby_indices = osm_tree.query_ball_point(
        grid_coordinates,
        r=radius_m,
    )

    # ------------------------------------------------------------------
    # Aggregate context.
    # ------------------------------------------------------------------

    for result_position, osm_indices in enumerate(
        nearby_indices
    ):

        if not osm_indices:
            continue

        nearby = osm_work.iloc[
            osm_indices
        ]

        result.iloc[
            result_position,
            result.columns.get_loc(
                "osm_feature_count"
            ),
        ] = int(len(osm_indices))

        result.iloc[
            result_position,
            result.columns.get_loc(
                "osm_industrial_count"
            ),
        ] = int(
            nearby["industrial"].sum()
        )

        result.iloc[
            result_position,
            result.columns.get_loc(
                "osm_power_count"
            ),
        ] = int(
            nearby["power"].sum()
        )

        result.iloc[
            result_position,
            result.columns.get_loc(
                "osm_manmade_count"
            ),
        ] = int(
            nearby["manmade"].sum()
        )

        # --------------------------------------------------------------
        # Nearest OSM distance.
        # --------------------------------------------------------------

        grid_x, grid_y = grid_coordinates[
            result_position
        ]

        osm_x = nearby["x"].to_numpy(
            dtype=float
        )

        osm_y = nearby["y"].to_numpy(
            dtype=float
        )

        distances = (
            (osm_x - grid_x) ** 2
            + (osm_y - grid_y) ** 2
        ) ** 0.5

        result.iloc[
            result_position,
            result.columns.get_loc(
                "osm_min_distance_m"
            ),
        ] = float(
            distances.min()
        )

    return result[output_columns]


# ---------------------------------------------------------------------------
# High-level tile extraction
# ---------------------------------------------------------------------------

def fetch_tile(
    latitude: float,
    longitude: float,
    cache_dir: Path,
    tile_size_deg: float = DEFAULT_TILE_SIZE_DEG,
    radius_m: float = DEFAULT_RADIUS_M,
) -> tuple[str, pd.DataFrame, str | None]:
    """
    Fetch one geographic tile.

    Returns:
        tile_id
        parsed OSM dataframe
        endpoint used
    """

    tile_id = get_tile_id(
        latitude,
        longitude,
        tile_size_deg,
    )

    cached = load_cached_tile(
        cache_dir,
        tile_id,
    )

    if cached is not None:
        print(
            f"  Cache hit: {tile_id}"
        )

        return (
            tile_id,
            parse_overpass_elements(cached),
            "cache",
        )

    south, west, north, east = get_tile_bounds(
        latitude,
        longitude,
        tile_size_deg,
    )

    (
        query_south,
        query_west,
        query_north,
        query_east,
    ) = expand_bbox_meters(
        south,
        west,
        north,
        east,
        radius_m,
    )

    query = build_overpass_query(
        query_south,
        query_west,
        query_north,
        query_east,
    )

    print(
        f"  Tile: {tile_id} | "
        f"bbox={query_south:.4f},"
        f"{query_west:.4f},"
        f"{query_north:.4f},"
        f"{query_east:.4f}"
    )

    data, endpoint = query_overpass(
        query
    )

    save_cached_tile(
        cache_dir,
        tile_id,
        data,
    )

    parsed = parse_overpass_elements(
        data
    )

    print(
        f"  Success: {len(parsed)} unique OSM objects"
    )

    return (
        tile_id,
        parsed,
        endpoint,
    )