-- SIH26162 Thermal Intelligence
-- PostgreSQL + PostGIS schema
-- Spatial reference system: WGS 84 (EPSG:4326)

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS thermal_events (
    id BIGSERIAL PRIMARY KEY,

    event_id VARCHAR(100) UNIQUE NOT NULL,
    grid_id VARCHAR(100) UNIQUE NOT NULL,

    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 4326) NOT NULL,

    observation_count INTEGER NOT NULL DEFAULT 0,
    active_days INTEGER NOT NULL DEFAULT 0,
    first_seen DATE,
    last_seen DATE,
    persistence_days INTEGER NOT NULL DEFAULT 0,

    recurrence_ratio DOUBLE PRECISION,
    obs_per_active_day DOUBLE PRECISION,
    day_observations INTEGER NOT NULL DEFAULT 0,
    night_observations INTEGER NOT NULL DEFAULT 0,
    night_ratio DOUBLE PRECISION,

    mean_frp DOUBLE PRECISION,
    max_frp DOUBLE PRECISION,
    std_frp DOUBLE PRECISION,
    mean_brightness DOUBLE PRECISION,
    max_brightness DOUBLE PRECISION,
    mean_bright_t31 DOUBLE PRECISION,
    max_bright_t31 DOUBLE PRECISION,
    mean_confidence_score DOUBLE PRECISION,

    type_2_count INTEGER,
    type_2_ratio DOUBLE PRECISION,

    -- Heuristic labels only; not verified ground truth.
    target_persistent_source SMALLINT,
    target_multiclass SMALLINT,

    -- OSM context provenance matters. Unqueried/unknown is not zero.
    osm_context_available BOOLEAN NOT NULL DEFAULT FALSE,
    osm_feature_count INTEGER,
    osm_industrial_count INTEGER,
    osm_power_count INTEGER,
    osm_manmade_count INTEGER,
    osm_min_distance_m DOUBLE PRECISION,

    CONSTRAINT thermal_events_latitude_check
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT thermal_events_longitude_check
        CHECK (longitude BETWEEN -180 AND 180),

    CONSTRAINT thermal_events_binary_label_check
        CHECK (
            target_persistent_source IS NULL
            OR target_persistent_source IN (0, 1)
        ),

    CONSTRAINT thermal_events_multiclass_label_check
        CHECK (
            target_multiclass IS NULL
            OR target_multiclass IN (0, 1, 2, 3)
        )
);

CREATE INDEX IF NOT EXISTS idx_thermal_events_geom
    ON thermal_events
    USING GIST (geom);

-- The nearby API uses geom::geography for meter-based distance.
CREATE INDEX IF NOT EXISTS idx_thermal_events_geography
    ON thermal_events
    USING GIST ((geom::geography));

CREATE INDEX IF NOT EXISTS idx_thermal_events_first_seen
    ON thermal_events (first_seen);

CREATE INDEX IF NOT EXISTS idx_thermal_events_last_seen
    ON thermal_events (last_seen);

CREATE INDEX IF NOT EXISTS idx_thermal_events_target
    ON thermal_events (target_persistent_source);

CREATE INDEX IF NOT EXISTS idx_thermal_events_target_multiclass
    ON thermal_events (target_multiclass);
