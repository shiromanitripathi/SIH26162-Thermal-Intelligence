import { useEffect, useState } from "react";
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

import { getHotspotStats } from "../services/api";

function formatInteger(value) {
    return Number.isFinite(Number(value))
        ? Number(value).toLocaleString()
        : "â€”";
}

function DistrictIntelligence() {
    const [stats, setStats] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;

        getHotspotStats()
            .then((result) => {
                if (!cancelled) {
                    setStats(result);
                    setError("");
                }
            })
            .catch((err) => {
                if (!cancelled) {
                    setError(err.message);
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div className="intelligence-page">
            <section className="intelligence-header">
                <div className="intelligence-eyebrow">
                    INTELLIGENCE / REGIONAL
                </div>

                <h1>Regional Intelligence</h1>

                <p>
                    National event summaries are available
                    now. District-level attribution requires a
                    validated administrative-boundary join and
                    is not fabricated by the frontend.
                </p>

                {error && (
                    <div className="intelligence-notice">
                        BACKEND DATA UNAVAILABLE: {error}
                    </div>
                )}
            </section>

            <div className="intelligence-development">
                <Radio size={18} />

                <div>
                    <strong>
                        DISTRICT BREAKDOWN NOT YET AVAILABLE
                    </strong>

                    <span>
                        The current API does not expose
                        validated district or state
                        attribution. National aggregates below
                        are real backend values.
                    </span>
                </div>
            </div>

            <section className="regional-kpi-grid">
                <div className="regional-kpi-card">
                    <div className="regional-kpi-icon">
                        <Activity size={19} />
                    </div>

                    <span>THERMAL EVENT CELLS</span>

                    <strong>
                        {formatInteger(
                            stats?.total_spatial_cells
                        )}
                    </strong>

                    <small>
                        National stored cells
                    </small>
                </div>

                <div className="regional-kpi-card">
                    <div className="regional-kpi-icon">
                        <Flame size={19} />
                    </div>

                    <span>
                        UNCLASSIFIED CELLS
                    </span>

                    <strong>
                        {formatInteger(
                            stats?.unclassified_candidate_cells
                        )}
                    </strong>

                    <small>
                        No heuristic candidate label
                    </small>
                </div>

                <div className="regional-kpi-card">
                    <div className="regional-kpi-icon">
                        <TrendingUp size={19} />
                    </div>

                    <span>MAX ACTIVE DAYS</span>

                    <strong>
                        {formatInteger(
                            stats?.max_active_days
                        )}
                    </strong>

                    <small>National maximum</small>
                </div>

                <div className="regional-kpi-card">
                    <div className="regional-kpi-icon">
                        <ShieldAlert size={19} />
                    </div>

                    <span>OSM CONTEXT CELLS</span>

                    <strong>
                        {formatInteger(
                            stats?.osm_context_cells
                        )}
                    </strong>

                    <small>
                        Explicit context coverage
                    </small>
                </div>
            </section>

            <section
                id="district-intelligence"
                className="intelligence-main-grid nav-section-target"
            >
                <div className="region-selector-panel">
                    <div className="intelligence-panel-header">
                        <div>
                            <span className="intelligence-kicker">
                                CURRENT SCOPE
                            </span>
                            <h2>India-wide dataset</h2>
                        </div>

                        <MapPin size={19} />
                    </div>

                    <div className="region-data-placeholder">
                        <BarChart3 size={25} />

                        <strong>
                            Administrative boundary
                            attribution required
                        </strong>

                        <span>
                            District rankings will be enabled
                            only after event coordinates are
                            joined to a validated boundary
                            dataset.
                        </span>
                    </div>
                </div>

                <div className="selected-region-panel">
                    <div className="intelligence-panel-header">
                        <div>
                            <span className="intelligence-kicker">
                                NATIONAL SUMMARY
                            </span>
                            <h2>
                                Backend event statistics
                            </h2>
                        </div>
                    </div>

                    <div className="region-overview-grid">
                        <div>
                            <span>OBSERVATIONS</span>
                            <strong>
                                {formatInteger(
                                    stats?.total_raw_observations
                                )}
                            </strong>
                        </div>

                        <div>
                            <span>EVENT CELLS</span>
                            <strong>
                                {formatInteger(
                                    stats?.total_spatial_cells
                                )}
                            </strong>
                        </div>

                        <div>
                            <span>
                                UNCLASSIFIED CELLS
                            </span>
                            <strong>
                                {formatInteger(
                                    stats?.unclassified_candidate_cells
                                )}
                            </strong>
                        </div>

                        <div>
                            <span>
                                MAX PERSISTENCE DAYS
                            </span>
                            <strong>
                                {formatInteger(
                                    stats?.max_persistence_days
                                )}
                            </strong>
                        </div>
                    </div>
                </div>
            </section>

            <section
                id="regional-trends"
                className="regional-trends-section nav-section-target"
            >
                <div className="intelligence-panel-header">
                    <div>
                        <span className="intelligence-kicker">
                            TEMPORAL INTELLIGENCE
                        </span>
                        <h2>
                            Regional Thermal Trends
                        </h2>
                    </div>

                    <Clock3 size={19} />
                </div>

                <div className="trend-placeholder">
                    <div className="trend-placeholder-icon">
                        <TrendingUp size={25} />
                    </div>

                    <div>
                        <strong>
                            Regional time-series endpoint
                            not available
                        </strong>

                        <p>
                            No trend values are synthesized
                            by the frontend.
                        </p>
                    </div>
                </div>
            </section>

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
                        No backend priority score is defined
                    </strong>

                    <span>
                        The frontend does not invent
                        investigation rankings.
                    </span>
                </div>
            </section>
        </div>
    );
}

export default DistrictIntelligence;