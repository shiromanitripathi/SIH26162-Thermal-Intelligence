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

function Overview() {
    return (
        <div className="overview-page">

            {/* HERO */}
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
                        Transforming satellite-detected thermal anomalies into
                        explainable intelligence through temporal behavior,
                        geospatial context and AI-assisted classification.
                    </p>

                    <div className="hero-actions">
                        <a href="/map" className="primary-action">
                            <MapPin size={17} />
                            Explore Thermal Map
                            <ArrowUpRight size={16} />
                        </a>

                        <a href="/analysis" className="secondary-action">
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

            {/* DEVELOPMENT NOTICE */}
            <div className="development-banner">
                <div>
                    <ShieldAlert size={17} />
                    <strong>DEVELOPMENT MODE</strong>
                </div>

                <span>
                    Map observations shown on this page are UI demonstration data.
                    Real FIRMS observations will replace them during backend integration.
                </span>
            </div>

            {/* KPI SECTION */}
            <section
                id="command-center"
                className="dashboard-section nav-section-target"
            >
                <div className="section-heading">
                    <div>
                        <span className="section-index">01</span>
                        <div>
                            <span className="section-label">COMMAND CENTER</span>
                            <h2>Thermal activity overview</h2>
                        </div>
                    </div>

                    <span className="section-status">
                        <span className="status-dot" />
                        DATA PIPELINE READY
                    </span>
                </div>

                <div className="stats-grid">
                    <StatCard
                        label="Thermal Observations"
                        value="—"
                        description="Awaiting validated FIRMS data"
                        type="thermal"
                    />

                    <StatCard
                        label="Persistent Sources"
                        value="—"
                        description="Historical analysis unavailable"
                        type="activity"
                    />

                    <StatCard
                        label="Industrial Candidates"
                        value="—"
                        description="AI classification pending"
                        type="satellite"
                    />

                    <StatCard
                        label="System Status"
                        value="ONLINE"
                        description="Frontend intelligence console"
                        type="system"
                    />
                </div>
            </section>

            {/* MAP */}
            <section className="dashboard-section map-section">
                <div className="section-heading">
                    <div>
                        <span className="section-index">02</span>
                        <div>
                            <span className="section-label">GEOSPATIAL LAYER</span>
                            <h2>India thermal activity</h2>
                        </div>
                    </div>

                    <a href="/map" className="section-link">
                        Open full map
                        <ArrowUpRight size={15} />
                    </a>
                </div>

                <div className="map-dashboard-card">
                    <IndiaMap hotspots={demoHotspots} />
                </div>
            </section>

            {/* INTELLIGENCE GRID */}
            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <span className="section-index">03</span>
                        <div>
                            <span className="section-label">THERMAL INTELLIGENCE</span>
                            <h2>From detection to understanding</h2>
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
                            <span className="pending-badge">PENDING</span>
                        </div>

                        <h3>
                            Explain what the thermal anomaly represents.
                        </h3>

                        <p>
                            The AI layer will combine thermal characteristics,
                            temporal persistence, spatial behavior and geographic
                            context before producing an evidence-based assessment.
                        </p>

                        <div className="intelligence-flow">
                            <span>THERMAL</span>
                            <i>→</i>
                            <span>TEMPORAL</span>
                            <i>→</i>
                            <span>SPATIAL</span>
                            <i>→</i>
                            <span>CONTEXT</span>
                            <i>→</i>
                            <strong>AI</strong>
                        </div>
                    </div>

                    <div className="intelligence-card">
                        <div className="card-icon orange">
                            <Flame size={21} />
                        </div>

                        <span className="card-label">THERMAL BEHAVIOR</span>

                        <div className="big-placeholder">—</div>

                        <p>
                            Persistence and thermal history will appear when
                            validated historical observations are available.
                        </p>
                    </div>

                    <div className="intelligence-card">
                        <div className="card-icon blue">
                            <TrendingUp size={21} />
                        </div>

                        <span className="card-label">RECURRENCE</span>

                        <div className="big-placeholder">—</div>

                        <p>
                            Repeated detections will be analyzed to identify
                            persistent or recurring thermal behavior.
                        </p>
                    </div>
                </div>
            </section>

            {/* ACTIVITY */}
            <section
                id="live-activity"
                className="dashboard-section nav-section-target"
            >
                <div className="section-heading">
                    <div>
                        <span className="section-index">04</span>
                        <div>
                            <span className="section-label">EVENT MONITOR</span>
                            <h2>Recent thermal observations</h2>
                        </div>
                    </div>

                    <a href="/events" className="section-link">
                        Event explorer
                        <ArrowUpRight size={15} />
                    </a>
                </div>

                <div className="activity-card">

                    {demoHotspots.map((hotspot, index) => (
                        <div className="activity-row" key={hotspot.id}>

                            <div className="activity-number">
                                0{index + 1}
                            </div>

                            <div className="activity-main">
                                <div className="activity-title">
                                    <span className="thermal-pulse" />
                                    {hotspot.id}
                                </div>

                                <span className="activity-location">
                                    <MapPin size={13} />
                                    {hotspot.location}
                                </span>
                            </div>

                            <div className="activity-property">
                                <span>LATITUDE</span>
                                {hotspot.latitude.toFixed(4)}
                            </div>

                            <div className="activity-property">
                                <span>LONGITUDE</span>
                                {hotspot.longitude.toFixed(4)}
                            </div>

                            <div className="activity-status">
                                DEVELOPMENT MOCK
                            </div>

                            <ArrowUpRight size={16} />
                        </div>
                    ))}

                </div>
            </section>

            {/* PRIORITY */}
            <section className="dashboard-section">
                <div className="priority-dashboard">

                    <div className="priority-copy">
                        <div className="card-icon warning">
                            <ShieldAlert size={21} />
                        </div>

                        <span className="section-label">
                            INVESTIGATION PRIORITY
                        </span>

                        <h2>
                            Focus analyst attention where it matters.
                        </h2>

                        <p>
                            Once the ML and historical pipeline is connected,
                            candidate sources can be ranked using backend-provided
                            evidence and priority scores.
                        </p>

                        <a href="/intelligence" className="section-link">
                            View intelligence
                            <ArrowUpRight size={15} />
                        </a>
                    </div>

                    <div className="priority-visual">
                        <div className="priority-circle">
                            <span>—</span>
                            <small>PRIORITY</small>
                        </div>

                        <div className="priority-lines">
                            <div />
                            <div />
                            <div />
                        </div>
                    </div>

                </div>
            </section>

            {/* SYSTEM FOOTER */}
            <section
                id="system-status"
                className="system-overview nav-section-target"
            >
                <div className="system-item">
                    <Activity size={17} />
                    <div>
                        <span>FRONTEND</span>
                        <strong>OPERATIONAL</strong>
                    </div>
                </div>

                <div className="system-item">
                    <Radio size={17} />
                    <div>
                        <span>FIRMS DATA</span>
                        <strong>AWAITING BACKEND</strong>
                    </div>
                </div>

                <div className="system-item">
                    <BrainCircuit size={17} />
                    <div>
                        <span>ML ENGINE</span>
                        <strong>AWAITING INTEGRATION</strong>
                    </div>
                </div>

                <div className="system-item">
                    <ShieldAlert size={17} />
                    <div>
                        <span>ANALYST CONSOLE</span>
                        <strong>READY</strong>
                    </div>
                </div>
            </section>

        </div>
    );
}

export default Overview;