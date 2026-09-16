from __future__ import annotations

from sqlalchemy import text

from src.utils.database import engine


_BASE_COLUMNS = """
    id,
    event_id,
    grid_id,
    latitude,
    longitude,
    observation_count,
    active_days,
    persistence_days,
    recurrence_ratio,
    obs_per_active_day,
    day_observations,
    night_observations,
    night_ratio,
    mean_frp,
    max_frp,
    std_frp,
    mean_brightness AS brightness,
    max_brightness,
    mean_bright_t31,
    max_bright_t31,
    mean_confidence_score AS confidence,
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
"""


def get_all_hotspots(
    min_active_days: int = 1,
    persistent_only: bool = False,
    limit: int = 1500,
) -> list[dict]:
    query = text(
        f"""
        SELECT {_BASE_COLUMNS}
        FROM thermal_events
        WHERE active_days >= :min_active_days
          AND (
              :persistent_only = FALSE
              OR target_persistent_source = 1
          )
        ORDER BY
            COALESCE(target_persistent_source, 0) DESC,
            active_days DESC,
            observation_count DESC
        LIMIT :limit;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "min_active_days": min_active_days,
                "persistent_only": persistent_only,
                "limit": limit,
            },
        )
        return [dict(row._mapping) for row in result]


def get_hotspot_by_id(hotspot_id: str | int) -> dict | None:
    query = text(
        f"""
        SELECT {_BASE_COLUMNS}
        FROM thermal_events
        WHERE CAST(id AS TEXT) = :hotspot_id
           OR event_id = :hotspot_id
           OR grid_id = :hotspot_id
        LIMIT 1;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"hotspot_id": str(hotspot_id)},
        ).mappings().first()

        return dict(result) if result else None


def get_hotspots_nearby(
    latitude: float,
    longitude: float,
    radius_meters: float = 2000,
) -> list[dict]:
    query = text(
        f"""
        SELECT
            {_BASE_COLUMNS},
            ST_Distance(
                geom::geography,
                ST_SetSRID(
                    ST_MakePoint(:longitude, :latitude),
                    4326
                )::geography
            ) AS distance_m
        FROM thermal_events
        WHERE ST_DWithin(
            geom::geography,
            ST_SetSRID(
                ST_MakePoint(:longitude, :latitude),
                4326
            )::geography,
            :radius_meters
        )
        ORDER BY distance_m
        LIMIT 500;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "latitude": latitude,
                "longitude": longitude,
                "radius_meters": radius_meters,
            },
        )
        return [dict(row._mapping) for row in result]


def get_hotspot_stats() -> dict:
    query = text(
        """
        SELECT
            COUNT(*) AS total_spatial_cells,
            COALESCE(SUM(observation_count), 0) AS total_raw_observations,
            COUNT(*) FILTER (
                WHERE target_persistent_source = 1
            ) AS persistent_candidate_cells,
            COUNT(*) FILTER (
                WHERE target_persistent_source = 0
            ) AS ephemeral_candidate_cells,
            MAX(active_days) AS max_active_days,
            MAX(persistence_days) AS max_persistence_days,
            AVG(night_ratio) AS mean_night_ratio,
            COUNT(*) FILTER (
                WHERE osm_context_available = TRUE
            ) AS osm_context_cells
        FROM thermal_events;
        """
    )

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    return dict(row) if row else {}
