import { useMemo, useState } from "react";
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

const demoHotspots = [
    {
        id: "DEMO-001",
        latitude: 28.6139,
        longitude: 77.209,
        location: "Northern India",
        isMock: true,
    },
    {
        id: "DEMO-002",
        latitude: 19.076,
        longitude: 72.8777,
        location: "Western India",
        isMock: true,
    },
    {
        id: "DEMO-003",
        latitude: 22.5726,
        longitude: 88.3639,
        location: "Eastern India",
        isMock: true,
    },
    {
        id: "DEMO-004",
        latitude: 13.0827,
        longitude: 80.2707,
        location: "Southern India",
        isMock: true,
    },
    {
        id: "DEMO-005",
        latitude: 30.901,
        longitude: 75.8573,
        location: "North-West India",
        isMock: true,
    },
];

function ThermalMapPage() {
    const [selectedHotspot, setSelectedHotspot] = useState(null);
    const [search, setSearch] = useState("");
    const [showFilters, setShowFilters] = useState(true);
    const [confidence, setConfidence] = useState("all");
    const [classification, setClassification] = useState("all");

    const filteredHotspots = useMemo(() => {
        return demoHotspots.filter((hotspot) => {
            const matchesSearch =
                !search ||
                hotspot.id.toLowerCase().includes(search.toLowerCase()) ||
                hotspot.location.toLowerCase().includes(search.toLowerCase());

            return matchesSearch;
        });
    }, [search]);

    function handleSelectHotspot(hotspot) {
        setSelectedHotspot(hotspot);
    }

    function clearFilters() {
        setSearch("");
        setConfidence("all");
        setClassification("all");
    }

    return (
        <div className="thermal-map-page">

            {/* HEADER */}
            <section className="map-page-header">

                <div>
                    <div className="eyebrow">
                        <span className="eyebrow-dot" />
                        GEOSPATIAL INTELLIGENCE / 02
                    </div>

                    <h1>Thermal Map</h1>

                    <p>
                        Explore satellite-detected thermal observations across India,
                        inspect individual sources and prepare events for deeper
                        temporal and AI analysis.
                    </p>
                </div>

                <div className="map-live-status">
                    <span className="status-dot" />
                    MAP LAYER ONLINE
                </div>

            </section>

            {/* DEVELOPMENT NOTICE */}
            <div className="development-banner map-development-banner">
                <div>
                    <Target size={17} />
                    <strong>DEVELOPMENT DATA</strong>
                </div>

                <span>
                    Current markers are demonstration data for interface development.
                    Real FIRMS observations will be loaded through the backend API.
                </span>
            </div>

            {/* TOOLBAR */}
            <section className="map-toolbar">

                <div className="map-search">
                    <Search size={17} />

                    <input
                        type="text"
                        placeholder="Search hotspot ID or region..."
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />

                    {search && (
                        <button onClick={() => setSearch("")}>
                            <X size={15} />
                        </button>
                    )}
                </div>

                <button
                    className={`filter-toggle ${showFilters ? "active" : ""}`}
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <SlidersHorizontal size={16} />
                    Filters
                    <ChevronDown
                        size={14}
                        className={showFilters ? "rotate-chevron" : ""}
                    />
                </button>

                <div className="map-result-count">
                    <Flame size={15} />
                    <strong>{filteredHotspots.length}</strong>
                    <span>visible sources</span>
                </div>

            </section>

            {/* FILTERS */}
            {showFilters && (
                <section className="map-filter-panel">

                    <div className="filter-field">
                        <label>
                            <CalendarDays size={13} />
                            DATE RANGE
                        </label>

                        <select defaultValue="all">
                            <option value="all">All available dates</option>
                            <option value="today">Today</option>
                            <option value="week">Last 7 days</option>
                            <option value="month">Last 30 days</option>
                        </select>
                    </div>

                    <div className="filter-field">
                        <label>
                            <Activity size={13} />
                            CONFIDENCE
                        </label>

                        <select
                            value={confidence}
                            onChange={(event) => setConfidence(event.target.value)}
                        >
                            <option value="all">All confidence levels</option>
                            <option value="high">High</option>
                            <option value="nominal">Nominal</option>
                            <option value="low">Low</option>
                        </select>
                    </div>

                    <div className="filter-field">
                        <label>
                            <Target size={13} />
                            CLASSIFICATION
                        </label>

                        <select
                            value={classification}
                            onChange={(event) => setClassification(event.target.value)}
                        >
                            <option value="all">All classifications</option>
                            <option value="industrial">
                                Likely industrial
                            </option>
                            <option value="persistent">
                                Persistent source
                            </option>
                            <option value="other">
                                Other / uncertain
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

            {/* MAIN MAP AREA */}
            <section className="map-workspace">

                <div className="map-main-panel">

                    <IndiaMap
                        hotspots={filteredHotspots}
                        selectedHotspot={selectedHotspot}
                        onSelectHotspot={handleSelectHotspot}
                    />

                    <div className="map-coordinates">
                        <span>LAT 06°–37° N</span>
                        <span>LON 68°–98° E</span>
                    </div>

                </div>

                {/* SIDE PANEL */}
                <aside className="map-side-panel">

                    {!selectedHotspot ? (
                        <div className="map-empty-selection">

                            <div className="selection-icon">
                                <MapPin size={25} />
                            </div>

                            <span className="section-label">
                                HOTSPOT INSPECTOR
                            </span>

                            <h2>Select a thermal source</h2>

                            <p>
                                Click any thermal observation on the map or select one
                                from the source list below to inspect its available
                                information.
                            </p>

                            <div className="selection-instruction">
                                <span>01</span>
                                Select a marker
                            </div>

                            <div className="selection-instruction">
                                <span>02</span>
                                Inspect source details
                            </div>

                            <div className="selection-instruction">
                                <span>03</span>
                                Continue to AI analysis
                            </div>

                        </div>
                    ) : (
                        <div className="selected-source">

                            <div className="selected-source-header">

                                <div>
                                    <span className="section-label">
                                        SELECTED SOURCE
                                    </span>

                                    <h2>{selectedHotspot.id}</h2>
                                </div>

                                <button
                                    className="close-selection"
                                    onClick={() => setSelectedHotspot(null)}
                                >
                                    <X size={16} />
                                </button>

                            </div>

                            <div className="mock-tag">
                                DEVELOPMENT MOCK
                            </div>

                            <div className="source-location">
                                <MapPin size={16} />

                                <div>
                                    <span>REGION</span>
                                    <strong>{selectedHotspot.location}</strong>
                                </div>
                            </div>

                            <div className="coordinate-grid">

                                <div>
                                    <span>LATITUDE</span>
                                    <strong>
                                        {selectedHotspot.latitude.toFixed(5)}
                                    </strong>
                                </div>

                                <div>
                                    <span>LONGITUDE</span>
                                    <strong>
                                        {selectedHotspot.longitude.toFixed(5)}
                                    </strong>
                                </div>

                            </div>

                            <div className="source-information">

                                <div className="source-info-row">
                                    <span>Thermal intensity</span>
                                    <strong>Not available yet</strong>
                                </div>

                                <div className="source-info-row">
                                    <span>Detection time</span>
                                    <strong>Not available yet</strong>
                                </div>

                                <div className="source-info-row">
                                    <span>FIRMS confidence</span>
                                    <strong>Not available yet</strong>
                                </div>

                                <div className="source-info-row">
                                    <span>Persistence</span>
                                    <strong>Not available yet</strong>
                                </div>

                                <div className="source-info-row">
                                    <span>Classification</span>
                                    <strong>Not available yet</strong>
                                </div>

                            </div>

                            <div className="selection-actions">

                                <a
                                    href={`/analysis?hotspot=${selectedHotspot.id}`}
                                    className="primary-action full-width"
                                >
                                    <Activity size={16} />
                                    Analyze Source
                                </a>

                            </div>

                        </div>
                    )}

                </aside>

            </section>

            {/* SOURCE TABLE */}
            <section className="source-list-section">

                <div className="section-heading">

                    <div>
                        <span className="section-index">03</span>

                        <div>
                            <span className="section-label">
                                OBSERVATION INDEX
                            </span>

                            <h2>Thermal sources</h2>
                        </div>
                    </div>

                    <span className="source-count">
                        {filteredHotspots.length} RESULTS
                    </span>

                </div>

                <div className="source-table">

                    <div className="source-table-header">
                        <span>ID</span>
                        <span>LOCATION</span>
                        <span>LATITUDE</span>
                        <span>LONGITUDE</span>
                        <span>STATUS</span>
                    </div>

                    {filteredHotspots.length === 0 ? (
                        <div className="source-empty">
                            <Search size={20} />
                            <strong>No matching sources</strong>
                            <span>
                                Try changing your search or clearing the filters.
                            </span>
                        </div>
                    ) : (
                        filteredHotspots.map((hotspot) => (
                            <button
                                className={`source-table-row ${selectedHotspot?.id === hotspot.id
                                        ? "selected"
                                        : ""
                                    }`}
                                key={hotspot.id}
                                onClick={() => handleSelectHotspot(hotspot)}
                            >
                                <span className="source-id">
                                    <span className="thermal-pulse" />
                                    {hotspot.id}
                                </span>

                                <span>{hotspot.location}</span>

                                <span>
                                    {hotspot.latitude.toFixed(4)}
                                </span>

                                <span>
                                    {hotspot.longitude.toFixed(4)}
                                </span>

                                <span className="mock-status">
                                    DEVELOPMENT MOCK
                                </span>
                            </button>
                        ))
                    )}

                </div>

            </section>

        </div>
    );
}

export default ThermalMapPage;