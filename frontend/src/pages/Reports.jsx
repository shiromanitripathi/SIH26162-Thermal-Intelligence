import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
    ArrowLeft,
    CalendarDays,
    Clock3,
    FileText,
    Flame,
    MapPin,
    Printer,
    Radio,
    ShieldAlert,
} from "lucide-react";

import {
    getHotspot,
    getHotspotClassification,
} from "../services/api";

function eventIdentity(event) {
    return String(
        event?.event_id ??
        event?.grid_id ??
        event?.id ??
        ""
    );
}

function Reports() {
    const [searchParams] = useSearchParams();

    const requestedId =
        searchParams.get("event") ||
        searchParams.get("hotspot") ||
        "";

    const [event, setEvent] = useState(null);
    const [prediction, setPrediction] =
        useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!requestedId) {
            setEvent(null);
            setPrediction(null);
            return;
        }

        let cancelled = false;

        async function load() {
            try {
                const eventResult =
                    await getHotspot(requestedId);

                if (cancelled) {
                    return;
                }

                setEvent(eventResult);
                setError("");

                try {
                    const predictionResult =
                        await getHotspotClassification(
                            eventIdentity(
                                eventResult
                            )
                        );

                    if (!cancelled) {
                        setPrediction(
                            predictionResult
                        );
                    }
                } catch {
                    if (!cancelled) {
                        setPrediction(null);
                    }
                }
            } catch (err) {
                if (!cancelled) {
                    setEvent(null);
                    setPrediction(null);
                    setError(err.message);
                }
            }
        }

        load();

        return () => {
            cancelled = true;
        };
    }, [requestedId]);

    function handlePrint() {
        window.print();
    }

    const modelUnavailable =
        prediction?.is_mock === true ||
        prediction?.classification ===
            "MODEL_NOT_AVAILABLE";

    return (
        <div className="reports-page">
            <section className="reports-header no-print">
                <div className="reports-eyebrow">
                    REPORTS / INVESTIGATION
                </div>

                <h1>Investigation Report</h1>

                <p>
                    Structured report generated only from
                    available backend evidence.
                </p>

                <div
                    id="export-print"
                    className="report-toolbar nav-section-target"
                >
                    <a
                        href={
                            event
                                ? `/analysis?event=${encodeURIComponent(
                                    eventIdentity(event)
                                )}`
                                : "/analysis"
                        }
                        className="report-back-button"
                    >
                        <ArrowLeft size={17} />
                        BACK TO ANALYSIS
                    </a>

                    <button
                        className="report-print-button"
                        onClick={handlePrint}
                    >
                        <Printer size={17} />
                        PRINT / EXPORT
                    </button>
                </div>
            </section>

            {error && (
                <div className="report-development no-print">
                    <Radio size={18} />

                    <div>
                        <strong>
                            REPORT DATA UNAVAILABLE
                        </strong>
                        <span>{error}</span>
                    </div>
                </div>
            )}

            {!requestedId && (
                <div className="report-development no-print">
                    <Radio size={18} />

                    <div>
                        <strong>
                            NO EVENT SELECTED
                        </strong>
                        <span>
                            Open a report from a selected
                            event or analysis page.
                        </span>
                    </div>
                </div>
            )}

            <article
                id="investigation-report"
                className="investigation-report nav-section-target"
            >
                <header className="report-document-header">
                    <div className="report-brand">
                        <div className="report-brand-icon">
                            <Flame size={22} />
                        </div>

                        <div>
                            <strong>FIRMS</strong>
                            <span>
                                THERMAL INTELLIGENCE
                            </span>
                        </div>
                    </div>

                    <div className="report-document-type">
                        <span>
                            INVESTIGATION REPORT
                        </span>
                        <strong>
                            {event
                                ? eventIdentity(event)
                                : "NO EVENT"}
                        </strong>
                    </div>
                </header>

                <div className="report-status-row">
                    <div className="report-status">
                        BACKEND DATA ONLY
                    </div>

                    <div className="report-generated">
                        <CalendarDays size={15} />
                        Missing values are displayed as
                        unavailable
                    </div>
                </div>

                <section className="report-section">
                    <div className="report-section-title">
                        <FileText size={18} />

                        <div>
                            <span>01</span>
                            <h2>Executive Summary</h2>
                        </div>
                    </div>

                    <div className="report-summary">
                        <p>
                            This report documents the
                            backend-provided information
                            associated with{" "}
                            <strong>
                                {event
                                    ? eventIdentity(
                                        event
                                    )
                                    : "the selected event"}
                            </strong>
                            .
                        </p>

                        <p>
                            Model output is treated as a
                            candidate classification, not
                            verified ground truth. Missing
                            model or OSM information is not
                            converted into synthetic values.
                        </p>
                    </div>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <MapPin size={18} />

                        <div>
                            <span>02</span>
                            <h2>Event Location</h2>
                        </div>
                    </div>

                    <div className="report-info-grid">
                        <div className="report-info-item">
                            <span>EVENT ID</span>
                            <strong>
                                {event
                                    ? eventIdentity(
                                        event
                                    )
                                    : "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>GRID ID</span>
                            <strong>
                                {event?.grid_id ?? "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>LATITUDE</span>
                            <strong>
                                {event?.latitude ?? "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>LONGITUDE</span>
                            <strong>
                                {event?.longitude ?? "â€”"}
                            </strong>
                        </div>
                    </div>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <Flame size={18} />

                        <div>
                            <span>03</span>
                            <h2>
                                Thermal Observations
                            </h2>
                        </div>
                    </div>

                    <div className="report-info-grid">
                        <div className="report-info-item">
                            <span>
                                OBSERVATION PERIOD
                            </span>
                            <strong>
                                {event?.first_seen &&
                                event?.last_seen
                                    ? `${event.first_seen} to ${event.last_seen}`
                                    : "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>
                                OBSERVATION COUNT
                            </span>
                            <strong>
                                {event?.observation_count ??
                                    "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>MEAN FRP</span>
                            <strong>
                                {event?.mean_frp == null
                                    ? "â€”"
                                    : Number(
                                        event.mean_frp
                                    ).toFixed(2)}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>
                                FIRMS CONFIDENCE
                            </span>
                            <strong>
                                {event?.confidence == null
                                    ? "â€”"
                                    : Number(
                                        event.confidence
                                    ).toFixed(2)}
                            </strong>
                        </div>
                    </div>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <Clock3 size={18} />

                        <div>
                            <span>04</span>
                            <h2>
                                Persistence & Recurrence
                            </h2>
                        </div>
                    </div>

                    <div className="report-info-grid">
                        <div className="report-info-item">
                            <span>
                                PERSISTENCE DAYS
                            </span>
                            <strong>
                                {event?.persistence_days ??
                                    "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>ACTIVE DAYS</span>
                            <strong>
                                {event?.active_days ?? "â€”"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>
                                RECURRENCE RATIO
                            </span>
                            <strong>
                                {event?.recurrence_ratio ==
                                null
                                    ? "â€”"
                                    : Number(
                                        event.recurrence_ratio
                                    ).toFixed(3)}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>NIGHT RATIO</span>
                            <strong>
                                {event?.night_ratio == null
                                    ? "â€”"
                                    : Number(
                                        event.night_ratio
                                    ).toFixed(3)}
                            </strong>
                        </div>
                    </div>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <MapPin size={18} />

                        <div>
                            <span>05</span>
                            <h2>
                                Geographic Context
                            </h2>
                        </div>
                    </div>

                    <div className="report-context-box">
                        <div>
                            <span>
                                OSM CONTEXT STATUS
                            </span>
                            <strong>
                                {event?.osm_context_available ===
                                true
                                    ? "Available"
                                    : "Unavailable / not queried"}
                            </strong>
                        </div>

                        <div>
                            <span>
                                INDUSTRIAL FEATURES
                            </span>
                            <strong>
                                {event?.osm_context_available ===
                                true
                                    ? event?.osm_industrial_count ??
                                      "â€”"
                                    : "â€”"}
                            </strong>
                        </div>

                        <div>
                            <span>
                                NEAREST CONTEXT DISTANCE
                            </span>
                            <strong>
                                {event?.osm_context_available ===
                                    true &&
                                event?.osm_min_distance_m !=
                                    null
                                    ? `${Number(
                                        event.osm_min_distance_m
                                    ).toFixed(1)} m`
                                    : "â€”"}
                            </strong>
                        </div>
                    </div>

                    <p className="report-note">
                        Geographic proximity is contextual
                        evidence and does not establish the
                        cause or source of a thermal event.
                    </p>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <ShieldAlert size={18} />

                        <div>
                            <span>06</span>
                            <h2>AI Assessment</h2>
                        </div>
                    </div>

                    <div className="ai-report-result">
                        <div>
                            <span>
                                MODEL CLASSIFICATION
                            </span>
                            <strong>
                                {modelUnavailable
                                    ? "Model unavailable"
                                    : prediction?.classification ??
                                      "â€”"}
                            </strong>
                        </div>

                        <div>
                            <span>MODEL SCORE</span>
                            <strong>
                                {prediction?.model_score ==
                                null
                                    ? "â€”"
                                    : Number(
                                        prediction.model_score
                                    ).toFixed(4)}
                            </strong>
                        </div>

                        <div>
                            <span>MODEL VERSION</span>
                            <strong>
                                {prediction?.model_version ??
                                    "â€”"}
                            </strong>
                        </div>
                    </div>

                    <div className="report-evidence">
                        <span>
                            SUPPORTING EVIDENCE
                        </span>

                        <p>
                            {prediction?.evidence?.length
                                ? prediction.evidence.join(
                                    " â€¢ "
                                )
                                : "No model evidence is available."}
                        </p>
                    </div>
                </section>

                <section className="report-section">
                    <div className="report-section-title">
                        <Radio size={18} />

                        <div>
                            <span>07</span>
                            <h2>Data Provenance</h2>
                        </div>
                    </div>

                    <div className="provenance-box">
                        <div>
                            <span>
                                PRIMARY OBSERVATION SOURCE
                            </span>
                            <strong>NASA FIRMS</strong>
                        </div>

                        <div>
                            <span>
                                GEOGRAPHIC CONTEXT
                            </span>
                            <strong>
                                OSM context when explicitly
                                available
                            </strong>
                        </div>

                        <div>
                            <span>AI ASSESSMENT</span>
                            <strong>
                                Backend prediction service
                            </strong>
                        </div>

                        <div>
                            <span>REPORT STATUS</span>
                            <strong>
                                Analyst decision-support
                                report
                            </strong>
                        </div>
                    </div>
                </section>

                <footer className="report-footer">
                    <strong>
                        ANALYST DECISION SUPPORT
                    </strong>

                    <p>
                        Thermal observations are indicators
                        requiring contextual interpretation.
                        Model outputs and heuristic labels are
                        not independently verified source
                        attribution.
                    </p>

                    <div>
                        FIRMS THERMAL INTELLIGENCE â€¢ SIH26162
                    </div>
                </footer>
            </article>
        </div>
    );
}

export default Reports;