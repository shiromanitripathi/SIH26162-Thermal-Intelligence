-- Align an existing Day-2 thermal_events table with the final integration
-- contract. Run once on databases created from the earlier schema.

ALTER TABLE thermal_events
    ADD COLUMN IF NOT EXISTS target_multiclass SMALLINT;

ALTER TABLE thermal_events
    ADD COLUMN IF NOT EXISTS osm_context_available BOOLEAN
    NOT NULL DEFAULT FALSE;

ALTER TABLE thermal_events
    ALTER COLUMN osm_feature_count DROP NOT NULL,
    ALTER COLUMN osm_feature_count DROP DEFAULT,
    ALTER COLUMN osm_industrial_count DROP NOT NULL,
    ALTER COLUMN osm_industrial_count DROP DEFAULT,
    ALTER COLUMN osm_power_count DROP NOT NULL,
    ALTER COLUMN osm_power_count DROP DEFAULT,
    ALTER COLUMN osm_manmade_count DROP NOT NULL,
    ALTER COLUMN osm_manmade_count DROP DEFAULT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'thermal_events_multiclass_label_check'
    ) THEN
        ALTER TABLE thermal_events
            ADD CONSTRAINT thermal_events_multiclass_label_check
            CHECK (
                target_multiclass IS NULL
                OR target_multiclass IN (0, 1, 2, 3)
            );
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_thermal_events_geography
    ON thermal_events
    USING GIST ((geom::geography));

CREATE INDEX IF NOT EXISTS idx_thermal_events_target_multiclass
    ON thermal_events (target_multiclass);
