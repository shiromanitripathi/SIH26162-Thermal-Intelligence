import { useState } from "react";
import {
    Activity,
    BarChart3,
    Clock3,
    Flame,
    MapPin,
    Radio,
    ShieldAlert,
    TrendingUp,
} from "lucide-react";

const demoRegions = [
    {
        id: "REGION-DEMO-001",
        name: "Northern India",
    },
    {
        id: "REGION-DEMO-002",
        name: "Western India",
    },
    {
        id: "REGION-DEMO-003",
        name: "Eastern India",
    },
    {
        id: "REGION-DEMO-004",
        name: "Southern India",
    },
];

function DistrictIntelligence() {
    const [selectedRegion, setSelectedRegion] = useState(
        demoRegions[0]
    );

    return (
        <div className="intelligence-page">

            {/* HEADER */}

            <section className="intelligence-header">

                <div className="intelligence-eyebrow">
                    INTELLIGENCE / REGIONAL
                </div>

                <h1>Regional Intelligence</h1>

                <p>
                    Compare thermal activity, temporal behavior and
                    investigation signals across geographic regions.
                </p>

                <div className="intelligence-notice">
                    REGIONAL DATA AWAITING BACKEND
                </div>

            </section>

            {/* DEVELOPMENT NOTICE */}

            <div className="intelligence-development">

                <Radio size={18} />

                <div>
                    <strong>DEVELOPMENT MODE</strong>

                    <span>
                        Regional and district statistics will appear only
                        when validated backend data is available.
                    </span>
                </div>

            </div>

            {/* KPI GRID */}

            <section className="regional-kpi-grid">

                <div className="regional-kpi-card">

                    <div className="regional-kpi-icon">
                        <Activity size={19} />
                    </div>

                    <span>THERMAL EVENTS</span>

                    <strong>—</strong>

                    <small>
                        Backend data required
                    </small>

                </div>

                <div className="regional-kpi-card">

                    <div className="regional-kpi-icon">
                        <Flame size={19} />
                    </div>

                    <span>PERSISTENT SOURCES</span>

                    <strong>—</strong>

                    <small>
                        Backend data required
                    </small>

                </div>

                <div className="regional-kpi-card">

                    <div className="regional-kpi-icon">
                        <TrendingUp size={19} />
                    </div>

                    <span>RECURRENT SOURCES</span>

                    <strong>—</strong>

                    <small>
                        Backend data required
                    </small>

                </div>

                <div className="regional-kpi-card">

                    <div className="regional-kpi-icon">
                        <ShieldAlert size={19} />
                    </div>

                    <span>PRIORITY SOURCES</span>

                    <strong>—</strong>

                    <small>
                        Backend data required
                    </small>

                </div>

            </section>

            {/* MAIN GRID */}

            <section
                id="district-intelligence"
                className="intelligence-main-grid nav-section-target"
            >

                {/* REGION SELECTOR */}

                <div className="region-selector-panel">

                    <div className="intelligence-panel-header">

                        <div>
                            <span className="intelligence-kicker">
                                REGIONAL VIEW
                            </span>

                            <h2>Geographic Regions</h2>
                        </div>

                        <MapPin size={19} />

                    </div>

                    <div className="region-list">

                        {demoRegions.map((region) => (

                            <button
                                key={region.id}
                                className={`region-item ${selectedRegion.id === region.id
                                    ? "active"
                                    : ""
                                    }`}
                                onClick={() => setSelectedRegion(region)}
                            >

                                <div className="region-marker">
                                    <MapPin size={16} />
                                </div>

                                <div>
                                    <strong>{region.name}</strong>

                                    <span>
                                        Development region
                                    </span>
                                </div>

                            </button>

                        ))}

                    </div>

                </div>

                {/* SELECTED REGION */}

                <div className="selected-region-panel">

                    <div className="intelligence-panel-header">

                        <div>
                            <span className="intelligence-kicker">
                                SELECTED REGION
                            </span>

                            <h2>{selectedRegion.name}</h2>
                        </div>

                        <span className="region-development-badge">
                            DEVELOPMENT MOCK
                        </span>

                    </div>

                    <div className="region-overview-grid">

                        <div>
                            <span>OBSERVATIONS</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>EVENTS</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>PERSISTENT SOURCES</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>RECURRENT SOURCES</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                    </div>

                    <div className="region-data-placeholder">

                        <BarChart3 size={25} />

                        <strong>
                            Regional analytics not available yet
                        </strong>

                        <span>
                            Validated FIRMS observations and backend
                            aggregation are required before regional
                            statistics can be displayed.
                        </span>

                    </div>

                </div>

            </section>

            {/* TEMPORAL TRENDS */}

            <section
                id="regional-trends"
                className="regional-trends-section nav-section-target"
            >

                <div className="intelligence-panel-header">

                    <div>
                        <span className="intelligence-kicker">
                            TEMPORAL INTELLIGENCE
                        </span>

                        <h2>Regional Thermal Trends</h2>
                    </div>

                    <Clock3 size={19} />

                </div>

                <div className="trend-placeholder">

                    <div className="trend-placeholder-icon">
                        <TrendingUp size={25} />
                    </div>

                    <div>
                        <strong>
                            Monthly and temporal trends not available yet
                        </strong>

                        <p>
                            This visualization will use validated observation
                            history to show changes in thermal activity over
                            time.
                        </p>
                    </div>

                </div>

            </section>

            {/* DISTRICT TABLE */}

            <section className="district-table-section">

                <div className="intelligence-panel-header">

                    <div>
                        <span className="intelligence-kicker">
                            DISTRICT INTELLIGENCE
                        </span>

                        <h2>District Overview</h2>
                    </div>

                    <span className="table-status">
                        BACKEND REQUIRED
                    </span>

                </div>

                <div className="district-table-wrapper">

                    <table className="district-table">

                        <thead>
                            <tr>
                                <th>DISTRICT / REGION</th>
                                <th>OBSERVATIONS</th>
                                <th>EVENTS</th>
                                <th>PERSISTENCE</th>
                                <th>RECURRENCE</th>
                                <th>PRIORITY</th>
                            </tr>
                        </thead>

                        <tbody>

                            <tr>
                                <td>
                                    <div className="district-name">
                                        <MapPin size={15} />
                                        Data pending
                                    </div>
                                </td>

                                <td>—</td>
                                <td>—</td>
                                <td>—</td>
                                <td>—</td>
                                <td>
                                    <span className="not-available">
                                        Not available
                                    </span>
                                </td>
                            </tr>

                        </tbody>

                    </table>

                </div>

            </section>

            {/* PRIORITY SOURCES */}

            <section
                id="priority-sources"
                className="priority-intelligence-section nav-section-target"
            >

                <div className="intelligence-panel-header">

                    <div>
                        <span className="intelligence-kicker">
                            INVESTIGATION SUPPORT
                        </span>

                        <h2>Priority Sources</h2>
                    </div>

                    <ShieldAlert size={19} />

                </div>

                <div className="priority-placeholder">

                    <ShieldAlert size={25} />

                    <strong>
                        Priority ranking not available yet
                    </strong>

                    <span>
                        Investigation priority will be shown only when
                        supported by backend-provided assessment signals.
                    </span>

                </div>

            </section>

        </div>
    );
}

export default DistrictIntelligence;