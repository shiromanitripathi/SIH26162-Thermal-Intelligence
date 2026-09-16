import {
    useEffect,
    useMemo,
    useState,
} from "react";
import {
    Activity,
    CalendarDays,
    ChevronDown,
    Flame,
    MapPin,
    Search,
    SlidersHorizontal,
    Target,
    X,
} from "lucide-react";

import IndiaMap from "../components/IndiaMap";
import {
    getHotspot,
    getHotspots,
} from "../services/api";

function hotspotIdentity(hotspot) {
    return String(
        hotspot?.event_id ??
        hotspot?.grid_id ??
        hotspot?.id ??
        ""
    );
}

function classificationText(value) {
    switch (Number(value)) {
        case 0:
            return "Vegetation/agricultural candidate";
        case 1:
            return "Industrial-fire candidate";
        case 2:
            return "Persistent thermal-source candidate";
        case 3:
            return "Other / ephemeral candidate";
        default:
            return "Not classified";
    }
}

function formatNumber(value, digits = 2) {
    return Number.isFinite(Number(value))
        ? Number(value).toFixed(digits)
        : "â€”";
}

function ThermalMapPage() {
    const [hotspots, setHotspots] = useState([]);
    const [
        selectedHotspot,
        setSelectedHotspot,
    ] = useState(null);
    const [search, setSearch] = useState("");
    const [showFilters, setShowFilters] = useState(true);
    const [minActiveDays, setMinActiveDays] =
        useState("1");
    const [classification, setClassification] =
        useState("all");
    const [loading, setLoading] = useState(true);
    const [detailLoading, setDetailLoading] =
        useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;

        async function loadHotspots() {
            setLoading(true);
            setError("");

            try {
                const result = await getHotspots({
                    min_active_days:
                        Number(minActiveDays),
                    limit: 1500,
                });

                if (!cancelled) {
                    setHotspots(result);
                }
            } catch (err) {
                if (!cancelled) {
                    setHotspots([]);
                    setError(err.message);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        loadHotspots();

        return () => {
            cancelled = true;
        };
    }, [minActiveDays]);

    const filteredHotspots = useMemo(() => {
        const query = search.trim().toLowerCase();

        return hotspots.filter((hotspot) => {
            const matchesSearch =
                !query ||
                hotspotIdentity(hotspot)
                    .toLowerCase()
                    .includes(query) ||
                String(hotspot.id ?? "")
                    .toLowerCase()
                    .includes(query) ||
                String(hotspot.grid_id ?? "")
                    .toLowerCase()
                    .includes(query);

            const matchesClassification =
                classification === "all" ||
                String(hotspot.target_multiclass) ===
                    classification;

            return (
                matchesSearch &&
                matchesClassification
            );
        });
    }, [hotspots, search, classification]);

    async function handleSelectHotspot(hotspot) {
        setSelectedHotspot(hotspot);
        setDetailLoading(true);

        try {
            const detail = await getHotspot(
                hotspotIdentity(hotspot)
            );
            setSelectedHotspot(detail);
        } catch {
            // Keep real list data if detail retrieval fails.
        } finally {
            setDetailLoading(false);
        }
    }

    function clearFilters() {
        setSearch("");
        setMinActiveDays("1");
        setClassification("all");
    }

    return (
        <div className="thermal-map-page">
            <section className="map-page-header">
                <div>
                    <div className="eyebrow">
                        <span className="eyebrow-dot" />
                        GEOSPATIAL INTELLIGENCE / 02
                    </div>

                    <h1>Thermal Map</h1>

                    <p>
                        Explore backend-provided thermal-event
                        cells across India and inspect their
                        observed temporal and contextual
                        attributes.
                    </p>
                </div>

                <div className="map-live-status">
                    <span className="status-dot" />
                    {loading
                        ? "LOADING DATA"
                        : "BACKEND EVENT LAYER"}
                </div>
            </section>

            {error && (
                <div className="development-banner map-development-banner">
                    <div>
                        <Target size={17} />
                        <strong>
                            EVENT DATA UNAVAILABLE
                        </strong>
                    </div>

                    <span>{error}</span>
                </div>
            )}

            <section
                id="hotspot-search"
                className="map-toolbar nav-section-target"
            >
                <div className="map-search">
                    <Search size={17} />

                    <input
                        type="text"
                        placeholder="Search event_id, grid_id or database ID..."
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />

                    {search && (
                        <button
                            onClick={() => setSearch("")}
                        >
                            <X size={15} />
                        </button>
                    )}
                </div>

                <button
                    className={`filter-toggle ${
                        showFilters ? "active" : ""
                    }`}
                    onClick={() =>
                        setShowFilters(!showFilters)
                    }
                >
                    <SlidersHorizontal size={16} />
                    Filters
                    <ChevronDown
                        size={14}
                        className={
                            showFilters
                                ? "rotate-chevron"
                                : ""
                        }
                    />
                </button>

                <div className="map-result-count">
                    <Flame size={15} />
                    <strong>
                        {filteredHotspots.length}
                    </strong>
                    <span>visible event cells</span>
                </div>
            </section>

            {showFilters && (
                <section className="map-filter-panel">
                    <div className="filter-field">
                        <label>
                            <CalendarDays size={13} />
                            MINIMUM ACTIVE DAYS
                        </label>

                        <select
                            value={minActiveDays}
                            onChange={(event) =>
                                setMinActiveDays(
                                    event.target.value
                                )
                            }
                        >
                            <option value="1">
                                1+ active day
                            </option>
                            <option value="3">
                                3+ active days
                            </option>
                            <option value="5">
                                5+ active days
                            </option>
                            <option value="10">
                                10+ active days
                            </option>
                        </select>
                    </div>

                    <div className="filter-field">
                        <label>
                            <Activity size={13} />
                            CLASSIFICATION
                        </label>

                        <select
                            value={classification}
                            onChange={(event) =>
                                setClassification(
                                    event.target.value
                                )
                            }
                        >
                            <option value="all">
                                All heuristic classes
                            </option>
                            <option value="0">
                                Vegetation/agricultural
                                candidate
                            </option>
                            <option value="1">
                                Industrial-fire candidate
                            </option>
                            <option value="2">
                                Persistent thermal-source
                                candidate
                            </option>
                            <option value="3">
                                Other / ephemeral candidate
                            </option>
                        </select>
                    </div>

                    <div className="filter-field">
                        <label>
                            <Target size={13} />
                            LABEL STATUS
                        </label>

                        <select
                            value="weak"
                            disabled
                            readOnly
                        >
                            <option value="weak">
                                Heuristic / weak labels
                            </option>
                        </select>
                    </div>

                    <button
                        className="clear-filter-button"
                        onClick={clearFilters}
                    >
                        Clear filters
                    </button>
                </section>
            )}

            <section
                id="thermal-map"
                className="map-workspace nav-section-target"
            >
                <div className="map-main-panel">
                    <IndiaMap
                        hotspots={filteredHotspots}
                        selectedHotspot={
                            selectedHotspot
                        }
                        onSelectHotspot={
                            handleSelectHotspot
                        }
                    />

                    <div className="map-coordinates">
                        <span>LAT 06Â°â€“37Â° N</span>
                        <span>LON 68Â°â€“98Â° E</span>
                    </div>
                </div>

                <aside className="map-side-panel">
                    {!selectedHotspot ? (
                        <div className="map-empty-selection">
                            <div className="selection-icon">
                                <MapPin size={25} />
                            </div>

                            <span className="section-label">
                                EVENT INSPECTOR
                            </span>

                            <h2>
                                Select a thermal event
                            </h2>

                            <p>
                                Click a backend-provided event
                                cell to inspect observed values.
                                Missing values remain missing.
                            </p>
                        </div>
                    ) : (
                        <div className="selected-source">
                            <div className="selected-source-header">
                                <div>
                                    <span className="section-label">
                                        SELECTED EVENT
                                    </span>

                                    <h2>
                                        {hotspotIdentity(
                                            selectedHotspot
                                        )}
                                    </h2>
                                </div>

                                <button
                                    className="close-selection"
                                    onClick={() =>
                                        setSelectedHotspot(
                                            null
                                        )
                                    }
                                >
                                    <X size={16} />
                                </button>
                            </div>

                            {detailLoading && (
                                <div className="mock-tag">
                                    LOADING DETAIL
                                </div>
                            )}

                            <div className="source-location">
                                <MapPin size={16} />

                                <div>
                                    <span>COORDINATES</span>
                                    <strong>
                                        {formatNumber(
                                            selectedHotspot.latitude,
                                            5
                                        )}
                                        ,{" "}
                                        {formatNumber(
                                            selectedHotspot.longitude,
                                            5
                                        )}
                                    </strong>
                                </div>
                            </div>

                            <div className="coordinate-grid">
                                <div>
                                    <span>ACTIVE DAYS</span>
                                    <strong>
                                        {selectedHotspot.active_days ??
                                            "â€”"}
                                    </strong>
                                </div>

                                <div>
                                    <span>OBSERVATIONS</span>
                                    <strong>
                                        {selectedHotspot.observation_count ??
                                            "â€”"}
                                    </strong>
                                </div>
                            </div>

                            <div className="source-information">
                                <div className="source-info-row">
                                    <span>Mean FRP</span>
                                    <strong>
                                        {selectedHotspot.mean_frp ==
                                        null
                                            ? "â€”"
                                            : formatNumber(
                                                selectedHotspot.mean_frp
                                            )}
                                    </strong>
                                </div>

                                <div className="source-info-row">
                                    <span>
                                        FIRMS confidence
                                    </span>
                                    <strong>
                                        {selectedHotspot.confidence ==
                                        null
                                            ? "â€”"
                                            : formatNumber(
                                                selectedHotspot.confidence
                                            )}
                                    </strong>
                                </div>

                                <div className="source-info-row">
                                    <span>
                                        Persistence days
                                    </span>
                                    <strong>
                                        {selectedHotspot.persistence_days ??
                                            "â€”"}
                                    </strong>
                                </div>

                                <div className="source-info-row">
                                    <span>
                                        Heuristic class
                                    </span>
                                    <strong>
                                        {classificationText(
                                            selectedHotspot.target_multiclass
                                        )}
                                    </strong>
                                </div>

                                <div className="source-info-row">
                                    <span>OSM context</span>
                                    <strong>
                                        {selectedHotspot.osm_context_available ===
                                        true
                                            ? "Available"
                                            : "Unavailable / not queried"}
                                    </strong>
                                </div>
                            </div>

                            <div className="selection-actions">
                                <a
                                    href={`/analysis?hotspot=${encodeURIComponent(
                                        hotspotIdentity(
                                            selectedHotspot
                                        )
                                    )}`}
                                    className="primary-action full-width"
                                >
                                    <Activity size={16} />
                                    Analyze Event
                                </a>
                            </div>
                        </div>
                    )}
                </aside>
            </section>

            <section
                id="persistent-sources"
                className="source-list-section nav-section-target"
            >
                <div className="section-heading">
                    <div>
                        <span className="section-index">
                            03
                        </span>

                        <div>
                            <span className="section-label">
                                EVENT INDEX
                            </span>
                            <h2>
                                Thermal-event cells
                            </h2>
                        </div>
                    </div>

                    <span className="source-count">
                        {filteredHotspots.length} RESULTS
                    </span>
                </div>

                <div className="source-table">
                    <div className="source-table-header">
                        <span>ID</span>
                        <span>CLASS</span>
                        <span>ACTIVE DAYS</span>
                        <span>OBSERVATIONS</span>
                        <span>OSM</span>
                    </div>

                    {loading ? (
                        <div className="source-empty">
                            <Activity size={20} />
                            <strong>
                                Loading events
                            </strong>
                        </div>
                    ) : filteredHotspots.length === 0 ? (
                        <div className="source-empty">
                            <Search size={20} />
                            <strong>
                                No matching event cells
                            </strong>
                            <span>
                                Change the filters or verify
                                backend data.
                            </span>
                        </div>
                    ) : (
                        filteredHotspots.map(
                            (hotspot) => (
                                <button
                                    className={`source-table-row ${
                                        hotspotIdentity(
                                            selectedHotspot
                                        ) ===
                                        hotspotIdentity(
                                            hotspot
                                        )
                                            ? "selected"
                                            : ""
                                    }`}
                                    key={hotspotIdentity(
                                        hotspot
                                    )}
                                    onClick={() =>
                                        handleSelectHotspot(
                                            hotspot
                                        )
                                    }
                                >
                                    <span className="source-id">
                                        <span className="thermal-pulse" />
                                        {hotspotIdentity(
                                            hotspot
                                        )}
                                    </span>

                                    <span>
                                        {classificationText(
                                            hotspot.target_multiclass
                                        )}
                                    </span>

                                    <span>
                                        {hotspot.active_days ??
                                            "â€”"}
                                    </span>

                                    <span>
                                        {hotspot.observation_count ??
                                            "â€”"}
                                    </span>

                                    <span>
                                        {hotspot.osm_context_available ===
                                        true
                                            ? "AVAILABLE"
                                            : "UNAVAILABLE"}
                                    </span>
                                </button>
                            )
                        )
                    )}
                </div>
            </section>
        </div>
    );
}

export default ThermalMapPage;