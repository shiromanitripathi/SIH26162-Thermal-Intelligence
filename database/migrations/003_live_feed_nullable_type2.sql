-- Live NOAA-20/NOAA-21 FIRMS API rows do not expose the
-- historical `type` field. Unknown type_2_count must therefore
-- remain NULL rather than being represented as zero.

ALTER TABLE thermal_events
    ALTER COLUMN type_2_count DROP NOT NULL,
    ALTER COLUMN type_2_count DROP DEFAULT;
