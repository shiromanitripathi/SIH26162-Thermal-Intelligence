from __future__ import annotations

import time
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import box


# Keep this focused. Do NOT query all buildings.
OSM_TAGS = {
    "landuse": ["industrial"],
    "industrial": True,
    "power": True,
    "man_made": True,
    "building": ["industrial", "warehouse"],
}


def configure_osmnx() -> None:
    ox.settings.use_cache = True
    ox.settings.log_console = True
    ox.settings.requests_timeout = 180


def load_firms_grid(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    required = {
        "grid_id",
        "lat_grid",
        "lon_grid",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Missing FIRMS columns: "
            + ", ".join(sorted(missing))
        )

    return df[
        ["grid_id", "lat_grid", "lon_grid"]
    ].drop_duplicates("grid_id")


def make_bbox(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
):
    return (
        float(min_lon),
        float(min_lat),
        float(max_lon),
        float(max_lat),
    )


def classify_feature(row: pd.Series) -> str:
    power = row.get("power")
    landuse = row.get("landuse")
    industrial = row.get("industrial")
    man_made = row.get("man_made")
    building = row.get("building")

    if pd.notna(power):
        return "power"

    if (
        landuse == "industrial"
        or pd.notna(industrial)
        or building in {"industrial", "warehouse"}
    ):
        return "industrial"

    if pd.notna(man_made):
        return "man_made"

    return "other"


def query_osm_bbox(
    bbox,
) -> gpd.GeoDataFrame:

    try:
        gdf = ox.features_from_bbox(
            bbox=bbox,
            tags=OSM_TAGS,
        )

        if gdf is None or len(gdf) == 0:
            return gpd.GeoDataFrame(
                geometry=[],
                crs="EPSG:4326",
            )

        gdf = gdf.reset_index()

        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")

        return gdf.to_crs("EPSG:4326")

    except Exception as exc:
        print(
            "OSM batch query failed:",
            repr(exc),
        )

        return gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326",
        )


def aggregate_osm_to_grid(
    grid: pd.DataFrame,
    osm: gpd.GeoDataFrame,
    radius_m: float = 2000,
) -> pd.DataFrame:

    result = grid.copy()

    result["osm_feature_count"] = 0
    result["osm_industrial_count"] = 0
    result["osm_power_count"] = 0
    result["osm_manmade_count"] = 0
    result["osm_min_distance_m"] = radius_m

    if osm.empty:
        return result

    # Work in a metric CRS for distance calculations.
    grid_gdf = gpd.GeoDataFrame(
        grid.copy(),
        geometry=gpd.points_from_xy(
            grid["lon_grid"],
            grid["lat_grid"],
        ),
        crs="EPSG:4326",
    ).to_crs("EPSG:3857")

    osm = osm.copy()

    osm["osm_category"] = osm.apply(
        classify_feature,
        axis=1,
    )

    # Use representative points for polygons/relations.
    osm["geometry"] = osm.geometry.representative_point()

    osm_metric = osm[
        ["geometry", "osm_category"]
    ].copy()

    osm_metric = gpd.GeoDataFrame(
        osm_metric,
        geometry="geometry",
        crs="EPSG:4326",
    ).to_crs("EPSG:3857")

    # Spatial join: only OSM objects within radius.
    joined = gpd.sjoin_nearest(
        grid_gdf,
        osm_metric,
        how="left",
        max_distance=radius_m,
        distance_col="distance_m",
    )

    # Count distinct OSM objects per grid cell.
    if not joined.empty:

        counts = (
            joined.dropna(
                subset=["index_right"]
            )
            .groupby("grid_id")
            .agg(
                osm_feature_count=(
                    "index_right",
                    "nunique",
                ),
                osm_min_distance_m=(
                    "distance_m",
                    "min",
                ),
            )
        )

        result = result.drop(
            columns=[
                "osm_feature_count",
                "osm_min_distance_m",
            ]
        ).merge(
            counts,
            on="grid_id",
            how="left",
        )

        result["osm_feature_count"] = (
            result["osm_feature_count"]
            .fillna(0)
            .astype(int)
        )

        result["osm_min_distance_m"] = (
            result["osm_min_distance_m"]
            .fillna(radius_m)
        )

        category_counts = (
            joined.dropna(
                subset=["osm_category"]
            )
            .pivot_table(
                index="grid_id",
                columns="osm_category",
                values="index_right",
                aggfunc="count",
                fill_value=0,
            )
        )

        for category in [
            "industrial",
            "power",
            "man_made",
        ]:
            if category in category_counts.columns:
                result[
                    f"osm_{category}_count"
                ] = (
                    result["grid_id"]
                    .map(
                        category_counts[category]
                    )
                    .fillna(0)
                    .astype(int)
                )

    return result


def build_batched_osm_features(
    grid: pd.DataFrame,
    output_path: Path,
    tile_size_deg: float = 2.0,
    radius_m: float = 2000,
) -> pd.DataFrame:

    configure_osmnx()

    min_lat = grid["lat_grid"].min()
    max_lat = grid["lat_grid"].max()
    min_lon = grid["lon_grid"].min()
    max_lon = grid["lon_grid"].max()

    print(
        f"FIRMS extent:"
        f"\n  latitude: {min_lat:.4f} -> {max_lat:.4f}"
        f"\n  longitude: {min_lon:.4f} -> {max_lon:.4f}"
    )

    results = []

    lat = min_lat

    tile_number = 0

    while lat < max_lat:

        lon = min_lon

        while lon < max_lon:

            tile_number += 1

            tile_min_lat = lat
            tile_max_lat = min(
                lat + tile_size_deg,
                max_lat,
            )

            tile_min_lon = lon
            tile_max_lon = min(
                lon + tile_size_deg,
                max_lon,
            )

            tile_grid = grid[
                (grid["lat_grid"] >= tile_min_lat)
                & (grid["lat_grid"] <= tile_max_lat)
                & (grid["lon_grid"] >= tile_min_lon)
                & (grid["lon_grid"] <= tile_max_lon)
            ].copy()

            if tile_grid.empty:
                lon += tile_size_deg
                continue

            # Expand tile slightly so grid points near
            # tile boundaries can still find nearby OSM objects.
            lat_buffer = radius_m / 111_000
            lon_buffer = radius_m / (
                111_000
                * max(
                    0.1,
                    abs(
                        __import__("math").cos(
                            __import__("math").radians(
                                (tile_min_lat + tile_max_lat) / 2
                            )
                        )
                    ),
                )
            )

            bbox = make_bbox(
                tile_min_lon - lon_buffer,
                tile_min_lat - lat_buffer,
                tile_max_lon + lon_buffer,
                tile_max_lat + lat_buffer,
            )

            print(
                f"\nTile {tile_number}:"
                f" {bbox}"
                f"\nFIRMS cells: {len(tile_grid):,}"
            )

            osm = query_osm_bbox(bbox)

            print(
                f"OSM features returned: {len(osm):,}"
            )

            tile_result = aggregate_osm_to_grid(
                tile_grid,
                osm,
                radius_m=radius_m,
            )

            results.append(tile_result)

            print(
                "Cells with OSM context:",
                int(
                    (
                        tile_result[
                            "osm_feature_count"
                        ] > 0
                    ).sum()
                ),
            )

            # Give Overpass some breathing room.
            time.sleep(2)

            lon += tile_size_deg

        lat += tile_size_deg

    if not results:
        raise RuntimeError(
            "No OSM tiles were successfully processed."
        )

    result = pd.concat(
        results,
        ignore_index=True,
    )

    # A grid cell can occur in two adjacent tiles because
    # of the radius buffer. Keep the strongest context.
    result = (
        result.sort_values(
            [
                "grid_id",
                "osm_feature_count",
            ]
        )
        .drop_duplicates(
            "grid_id",
            keep="last",
        )
        .reset_index(drop=True)
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved {len(result):,} rows to:"
        f"\n{output_path}"
    )

    return result
