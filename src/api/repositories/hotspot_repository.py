from sqlalchemy import text

from src.utils.database import engine


def get_all_hotspots() -> list[dict]:
    query = text("""
        SELECT
            id,
            latitude,
            longitude,
            mean_brightness AS brightness,
            mean_confidence_score AS confidence
        FROM thermal_events
        ORDER BY id;
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        return [dict(row._mapping) for row in result]


def get_hotspot_by_id(hotspot_id: int) -> dict | None:
    query = text("""
        SELECT
            id,
            latitude,
            longitude,
            mean_brightness AS brightness,
            mean_confidence_score AS confidence
        FROM thermal_events
        WHERE id = :hotspot_id;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"hotspot_id": hotspot_id},
        ).mappings().first()

        return dict(result) if result else None

def get_hotspots_nearby(
    latitude: float,
    longitude: float,
    radius_meters: float = 2000,
) -> list[dict]:
    query = text("""
        SELECT
            id,
            event_id,
            grid_id,
            latitude,
            longitude,
            mean_brightness AS brightness,
            mean_confidence_score AS confidence,
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
        ORDER BY distance_m;
    """)

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