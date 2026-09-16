import { useEffect, useState } from "react";
import {
    Activity,
    ArrowUpRight,
    BrainCircuit,
    Flame,
    MapPin,
    Radio,
    ShieldAlert,
    TrendingUp,
} from "lucide-react";

import IndiaMap from "../components/IndiaMap";
import StatCard from "../components/StatCard";
import {
    getHealth,
    getHotspots,
    getHotspotStats,
} from "../services/api";

function hotspotIdentity(hotspot) {
    return (
        hotspot?.event_id ||
        hotspot?.grid_id ||
        String(hotspot?.id ?? "Unknown event")
    );
}

function formatInteger(value) {
    return Number.isFinite(Number(value))
        ? Number(value).toLocaleString()
        : "—";
}

function Overview() {
    const [health, setHealth] = useState("checking");
    const [stats, setStats] = useState(null);
    const [hotspots, setHotspots] = useState([]);
    const [dataError, setDataError] = useState("");

    useEffect(() => {
        let cancelled = false;

        async function loadOverview() {
            const healthPromise = getHealth()
                .then(() => {
                    if (!cancelled) {
                        setHealth("online");
                    }
                })
                .catch(() => {
                    if (!cancelled) {
                        setHealth("offline");
                    }
                });

            const dataPromise = Promise.all([
                getHotspotStats(),
                getHotspots({ limit: 5 }),
            ])
                .then(([statsResult, hotspotResult]) => {
                    if (cancelled) {
                        return;
                    }

                    setStats(statsResult);
                    setHotspots(hotspotResult);
                    setDataError("");
                })
                .catch((error) => {
                    if (!cancelled) {
                        setDataError(error.message);
                    }
                });

            await Promise.allSettled([
                healthPromise,
                dataPromise,
            ]);
        }

        loadOverview();

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div className="overview-page">
            <section className="overview-hero">
                <div className="hero-copy">
                    <div className="eyebrow">
                        <span className="eyebrow-dot" />
                        SATELLITE THERMAL INTELLIGENCE / SIH26162
                    </div>

                    <h1>
                        Understanding
                        <span> the heat.</span>
                    </h1>

                    <p>
                        Transforming satellite-detected thermal
                        anomalies into explainable intelligence
                        through temporal behavior, geospatial context
                        and AI-assisted classification.
                    </p>

                    <div className="hero-actions">
                        <a
                            href="/map"
                            className="primary-action"
                        >
                            <MapPin size={17} />
                            Explore Thermal Map
                            <ArrowUpRight size={16} />
                        </a>

                        <a
                            href="/analysis"
                            className="secondary-action"
                        >
                            <BrainCircuit size={17} />
                            AI Assessment
                        </a>
                    </div>
                </div>

                <div className="hero-visual">
                    <div className="orbital-core">
                        <div className="core-ring ring-a" />
                        <div className="core-ring ring-b" />
                        <div className="core-ring ring-c" />

                        <div className="core-center">
                            <Radio size={28} />
                            <span>FIRMS</span>
                            <small>THERMAL FEED</small>
                        </div>

                        <div className="orbit-dot dot-one" />
                        <div className="orbit-dot dot-two" />
                        <div className="orbit-dot dot-three" />
                    </div>
                </div>
            </section>

            {dataError && (
                <div className="development-banner">
                    <div>
                        <ShieldAlert size={17} />
                        <strong>DATA UNAVAILABLE</strong>
                    </div>

                    <span>{dataError}</span>
                </div>
            )}

            <section
                id="command-center"
                className="dashboard-section nav-section-target"
            >
                <div className="section-heading">
                    <div>
                        <span className="section-index">01</span>

                        <div>
                            <span className="section-label">
                                COMMAND CENTER
                            </span>
                            <h2>
                                Thermal activity overview
                            </h2>
                        </div>
                    </div>

                    <span className="section-status">
                        <span className="status-dot" />
                        {health === "online"
                            ? "API ONLINE"
                            : health === "offline"
                                ? "API OFFLINE"
                                : "CHECKING API"}
                    </span>
                </div>

                <div className="stats-grid">
                    <StatCard
                        label="Thermal Observations"
                        value={formatInteger(
                            stats?.total_raw_observations
                        )}
                        description="Aggregated FIRMS observations"
                        type="thermal"
                    />

                    <StatCard
                        label="Unclassified Cells"
                        value={formatInteger(
                            stats?.unclassified_candidate_cells
                        )}
                        description="Cells without heuristic candidate labels"
                        type="activity"
                    />

                    <StatCard
                        label="OSM Context Cells"
                        value={formatInteger(
                            stats?.osm_context_cells
                        )}
                        description="Cells with available OSM context"
                        type="satellite"
                    />

                    <StatCard
                        label="API Status"
                        value={
                            health === "online"
                                ? "ONLINE"
                                : health === "offline"
                                    ? "OFFLINE"
                                    : "CHECKING"
                        }
                        description="FastAPI health endpoint"
                        type="system"
                    />
                </div>
            </section>

            <section className="dashboard-section map-section">
                <div className="section-heading">
                    <div>
                        <span className="section-index">02</span>

                        <div>
                            <span className="section-label">
                                GEOSPATIAL LAYER
                            </span>
                            <h2>India thermal activity</h2>
                        </div>
                    </div>

                    <a
                        href="/map"
                        className="section-link"
                    >
                        Open full map
                        <ArrowUpRight size={15} />
                    </a>
                </div>

                <div className="map-dashboard-card">
                    <IndiaMap hotspots={hotspots} />
                </div>
            </section>

            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <span className="section-index">03</span>

                        <div>
                            <span className="section-label">
                                THERMAL INTELLIGENCE
                            </span>
                            <h2>
                                From detection to understanding
                            </h2>
                        </div>
                    </div>
                </div>

                <div className="intelligence-grid">
                    <div className="intelligence-card large">
                        <div className="card-icon">
                            <BrainCircuit size={21} />
                        </div>

                        <div className="card-topline">
                            <span>AI CLASSIFICATION</span>
                            <span className="pending-badge">
                                ARTIFACT-DEPENDENT
                            </span>
                        </div>

                        <h3>
                            Classify candidate thermal behavior
                            without inventing missing evidence.
                        </h3>

                        <p>
                            The backend retrieves authoritative
                            event features and returns either a real
                            model assessment or an explicit
                            model-unavailable state.
                        </p>

                        <div className="intelligence-flow">
                            <span>THERMAL</span>
                            <i>→</i>
                            <span>TEMPORAL</span>
                            <i>→</i>
                            <span>CONTEXT</span>
                            <i>→</i>
                            <strong>MODEL</strong>
                        </div>
                    </div>

                    <div className="intelligence-card">
                        <div className="card-icon orange">
                            <Flame size={21} />
                        </div>

                        <span className="card-label">
                            MAX ACTIVE DAYS
                        </span>

                        <div className="big-placeholder">
                            {formatInteger(
                                stats?.max_active_days
                            )}
                        </div>

                        <p>
                            Maximum observed active-day count
                            among stored thermal-event cells.
                        </p>
                    </div>

                    <div className="intelligence-card">
                        <div className="card-icon blue">
                            <TrendingUp size={21} />
                        </div>

                        <span className="card-label">
                            MAX PERSISTENCE DAYS
                        </span>

                        <div className="big-placeholder">
                            {formatInteger(
                                stats?.max_persistence_days
                            )}
                        </div>

                        <p>
                            Maximum stored persistence duration
                            across event cells.
                        </p>
                    </div>
                </div>
            </section>

            <section
                id="live-activity"
                className="dashboard-section nav-section-target"
            >
                <div className="section-heading">
                    <div>
                        <span className="section-index">04</span>

                        <div>
                            <span className="section-label">
                                EVENT MONITOR
                            </span>
                            <h2>
                                Priority thermal-event cells
                            </h2>
                        </div>
                    </div>

                    <a
                        href="/events"
                        className="section-link"
                    >
                        Event explorer
                        <ArrowUpRight size={15} />
                    </a>
                </div>

                <div className="activity-card">
                    {hotspots.length === 0 ? (
                        <div className="source-empty">
                            <Activity size={20} />
                            <strong>
                                No event data available
                            </strong>
                            <span>
                                Connect and populate PostgreSQL
                                to display thermal events.
                            </span>
                        </div>
                    ) : (
                        hotspots.map((hotspot, index) => (
                            <div
                                className="activity-row"
                                key={hotspotIdentity(hotspot)}
                            >
                                <div className="activity-number">
                                    {String(index + 1).padStart(
                                        2,
                                        "0"
                                    )}
                                </div>

                                <div className="activity-main">
                                    <div className="activity-title">
                                        <span className="thermal-pulse" />
                                        {hotspotIdentity(hotspot)}
                                    </div>

                                    <span className="activity-location">
                                        <MapPin size={13} />
                                        {Number(
                                            hotspot.latitude
                                        ).toFixed(4)}
                                        ,{" "}
                                        {Number(
                                            hotspot.longitude
                                        ).toFixed(4)}
                                    </span>
                                </div>

                                <div className="activity-property">
                                    <span>ACTIVE DAYS</span>
                                    {hotspot.active_days ?? "—"}
                                </div>

                                <div className="activity-property">
                                    <span>OBSERVATIONS</span>
                                    {hotspot.observation_count ??
                                        "—"}
                                </div>

                                <div className="activity-status">
                                    {hotspot.target_persistent_source ===
                                    1
                                        ? "PERSISTENT CANDIDATE"
                                        : "THERMAL EVENT"}
                                </div>

                                <ArrowUpRight size={16} />
                            </div>
                        ))
                    )}
                </div>
            </section>

            <section
                id="system-status"
                className="system-overview nav-section-target"
            >
                <div className="system-item">
                    <Activity size={17} />
                    <div>
                        <span>FASTAPI</span>
                        <strong>
                            {health === "online"
                                ? "REACHABLE"
                                : health === "offline"
                                    ? "UNREACHABLE"
                                    : "CHECKING"}
                        </strong>
                    </div>
                </div>

                <div className="system-item">
                    <Radio size={17} />
                    <div>
                        <span>EVENT DATA</span>
                        <strong>
                            {stats
                                ? "AVAILABLE"
                                : "UNAVAILABLE"}
                        </strong>
                    </div>
                </div>

                <div className="system-item">
                    <BrainCircuit size={17} />
                    <div>
                        <span>ML ENGINE</span>
                        <strong>CHECK PER EVENT</strong>
                    </div>
                </div>

                <div className="system-item">
                    <ShieldAlert size={17} />
                    <div>
                        <span>SCIENTIFIC FALLBACKS</span>
                        <strong>DISABLED</strong>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Overview;