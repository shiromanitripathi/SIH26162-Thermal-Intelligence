import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
    AlertTriangle,
    BrainCircuit,
    CheckCircle2,
    Clock3,
    Flame,
    MapPin,
    ShieldAlert,
    Target,
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

function displayValue(value, digits = null) {
    if (value === null || value === undefined) {
        return "\u2014";
    }

    if (
        digits !== null &&
        Number.isFinite(Number(value))
    ) {
        return Number(value).toFixed(digits);
    }

    return String(value);
}

function Analysis() {
    const [searchParams] = useSearchParams();

    const requestedId =
        searchParams.get("event") ||
        searchParams.get("hotspot") ||
        "";

    const [event, setEvent] = useState(null);
    const [eventState, setEventState] =
        useState(requestedId ? "loading" : "empty");
    const [analysisState, setAnalysisState] =
        useState("idle");
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!requestedId) {
            setEvent(null);
            setEventState("empty");
            return;
        }

        let cancelled = false;

        async function loadEvent() {
            setEventState("loading");
            setError("");

            try {
                const result = await getHotspot(
                    requestedId
                );

                if (!cancelled) {
                    setEvent(result);
                    setEventState("ready");
                }
            } catch (err) {
                if (!cancelled) {
                    setEvent(null);
                    setEventState("error");
                    setError(err.message);
                }
            }
        }

        loadEvent();

        return () => {
            cancelled = true;
        };
    }, [requestedId]);

    async function handleAnalyze() {
        if (!event) {
            return;
        }

        setError("");
        setPrediction(null);
        setAnalysisState("loading");

        try {
            const result =
                await getHotspotClassification(
                    eventIdentity(event)
                );

            setPrediction(result);

            if (
                result.is_mock === true ||
                result.classification ===
                    "MODEL_NOT_AVAILABLE"
            ) {
                setAnalysisState("unavailable");
            } else {
                setAnalysisState("success");
            }
        } catch (err) {
            setAnalysisState("error");
            setError(err.message);
        }
    }

    const osmAvailable =
        event?.osm_context_available === true;

    return (
        <div className="analysis-page">
            <section className="analysis-header">
                <div className="analysis-eyebrow">
                    ANALYSIS / AI ASSESSMENT
                </div>

                <h1>Thermal Intelligence</h1>

                <p>
                    Inspect authoritative event evidence and
                    request the backend model assessment for
                    the selected event.
                </p>

                <div className="analysis-event-badge">
                    <Target size={15} />
                    SELECTED EVENT:{" "}
                    {event
                        ? eventIdentity(event)
                        : requestedId || "NONE"}
                </div>
            </section>

            {eventState === "loading" && (
                <div className="analysis-notice">
                    <Target size={18} />

                    <div>
                        <strong>LOADING EVENT</strong>
                        <span>
                            Retrieving the authoritative
                            backend record.
                        </span>
                    </div>
                </div>
            )}

            {eventState === "empty" && (
                <div className="analysis-notice">
                    <AlertTriangle size={18} />

                    <div>
                        <strong>NO EVENT SELECTED</strong>
                        <span>
                            Select an event from the map or
                            event explorer.
                        </span>
                    </div>
                </div>
            )}

            {eventState === "error" && (
                <div className="analysis-error">
                    <AlertTriangle size={19} />

                    <div>
                        <strong>
                            EVENT DATA UNAVAILABLE
                        </strong>
                        <p>{error}</p>
                    </div>
                </div>
            )}

            {event && (
                <>
                    <section className="analysis-source-card">
                        <div className="analysis-section-heading">
                            <div>
                                <span className="analysis-kicker">
                                    SELECTED THERMAL EVENT
                                </span>
                                <h2>
                                    {eventIdentity(event)}
                                </h2>
                            </div>
                        </div>

                        <div className="analysis-location">
                            <MapPin size={20} />

                            <div>
                                <span>COORDINATES</span>
                                <strong>
                                    {displayValue(
                                        event.latitude,
                                        5
                                    )}
                                    ,{" "}
                                    {displayValue(
                                        event.longitude,
                                        5
                                    )}
                                </strong>
                            </div>
                        </div>

                        <div className="analysis-coordinates">
                            <div>
                                <span>FIRST SEEN</span>
                                <strong>
                                    {displayValue(
                                        event.first_seen
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>LAST SEEN</span>
                                <strong>
                                    {displayValue(
                                        event.last_seen
                                    )}
                                </strong>
                            </div>
                        </div>
                    </section>

                    <section className="analysis-evidence-grid">
                        <div className="evidence-card">
                            <div className="evidence-card-header">
                                <div className="evidence-icon">
                                    <Flame size={19} />
                                </div>

                                <div>
                                    <span>
                                        THERMAL EVIDENCE
                                    </span>
                                    <h3>Thermal Signal</h3>
                                </div>
                            </div>

                            <div className="evidence-values">
                                <div>
                                    <span>MEAN FRP</span>
                                    <strong>
                                        {displayValue(
                                            event.mean_frp,
                                            2
                                        )}
                                    </strong>
                                    <small>
                                        Backend event
                                        aggregation
                                    </small>
                                </div>

                                <div>
                                    <span>
                                        FIRMS CONFIDENCE
                                    </span>
                                    <strong>
                                        {displayValue(
                                            event.confidence,
                                            2
                                        )}
                                    </strong>
                                    <small>
                                        Observation confidence
                                    </small>
                                </div>

                                <div>
                                    <span>
                                        OBSERVATION COUNT
                                    </span>
                                    <strong>
                                        {displayValue(
                                            event.observation_count
                                        )}
                                    </strong>
                                    <small>
                                        Aggregated observations
                                    </small>
                                </div>
                            </div>
                        </div>

                        <div
                            id="persistence"
                            className="evidence-card nav-section-target"
                        >
                            <div className="evidence-card-header">
                                <div className="evidence-icon">
                                    <Clock3 size={19} />
                                </div>

                                <div>
                                    <span>
                                        TEMPORAL EVIDENCE
                                    </span>
                                    <h3>Thermal History</h3>
                                </div>
                            </div>

                            <div className="evidence-values">
                                <div>
                                    <span>
                                        PERSISTENCE DAYS
                                    </span>
                                    <strong>
                                        {displayValue(
                                            event.persistence_days
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        RECURRENCE RATIO
                                    </span>
                                    <strong>
                                        {displayValue(
                                            event.recurrence_ratio,
                                            3
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    <span>ACTIVE DAYS</span>
                                    <strong>
                                        {displayValue(
                                            event.active_days
                                        )}
                                    </strong>
                                </div>
                            </div>
                        </div>

                        <div
                            id="context-intelligence"
                            className="evidence-card nav-section-target"
                        >
                            <div className="evidence-card-header">
                                <div className="evidence-icon">
                                    <Target size={19} />
                                </div>

                                <div>
                                    <span>
                                        GEOGRAPHIC CONTEXT
                                    </span>
                                    <h3>OSM Context</h3>
                                </div>
                            </div>

                            <div className="evidence-values">
                                <div>
                                    <span>
                                        CONTEXT STATUS
                                    </span>
                                    <strong>
                                        {osmAvailable
                                            ? "Available"
                                            : "Unavailable / not queried"}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        INDUSTRIAL FEATURES
                                    </span>
                                    <strong>
                                        {osmAvailable
                                            ? displayValue(
                                                event.osm_industrial_count
                                            )
                                            : "\u2014"}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        NEAREST CONTEXT
                                        DISTANCE
                                    </span>
                                    <strong>
                                        {osmAvailable &&
                                        event.osm_min_distance_m !=
                                            null
                                            ? `${displayValue(
                                                event.osm_min_distance_m,
                                                1
                                            )} m`
                                            : "\u2014"}
                                    </strong>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section
                        id="ai-assessment"
                        className="ai-action-section nav-section-target"
                    >
                        <div className="ai-action-content">
                            <div className="ai-action-icon">
                                <BrainCircuit size={27} />
                            </div>

                            <div>
                                <span className="analysis-kicker">
                                    MACHINE LEARNING
                                    ASSESSMENT
                                </span>

                                <h2>
                                    Analyze this thermal event
                                </h2>

                                <p>
                                    The backend retrieves the
                                    authoritative event row before
                                    invoking the predictor.
                                </p>
                            </div>
                        </div>

                        <button
                            className="analyze-ai-button"
                            onClick={handleAnalyze}
                            disabled={
                                analysisState ===
                                "loading"
                            }
                        >
                            <BrainCircuit size={18} />

                            {analysisState === "loading"
                                ? "ANALYZING..."
                                : "ANALYZE WITH AI"}
                        </button>
                    </section>
                </>
            )}

            {analysisState === "error" && (
                <div className="analysis-error">
                    <AlertTriangle size={19} />

                    <div>
                        <strong>
                            AI REQUEST FAILED
                        </strong>
                        <p>{error}</p>
                    </div>
                </div>
            )}

            {analysisState === "unavailable" && (
                <div className="analysis-notice">
                    <AlertTriangle size={18} />

                    <div>
                        <strong>
                            MODEL UNAVAILABLE
                        </strong>
                        <span>
                            No final trained artifact is
                            loaded. No classification or model
                            score has been fabricated.
                        </span>
                    </div>
                </div>
            )}

            <section className="ai-result-section">
                <div className="analysis-section-heading">
                    <div>
                        <span className="analysis-kicker">
                            AI ASSESSMENT RESULT
                        </span>

                        <h2>
                            Classification & Evidence
                        </h2>
                    </div>

                    {analysisState === "success" && (
                        <div className="result-available">
                            <CheckCircle2 size={16} />
                            MODEL RESULT
                        </div>
                    )}
                </div>

                <div className="ai-result-grid">
                    <div className="ai-result-card primary">
                        <span>
                            MODEL CLASSIFICATION
                        </span>

                        <strong>
                            {analysisState ===
                            "unavailable"
                                ? "Model unavailable"
                                : prediction?.classification ??
                                  "\u2014"}
                        </strong>

                        <small>
                            Candidate class; not verified
                            ground truth
                        </small>
                    </div>

                    <div className="ai-result-card">
                        <span>MODEL SCORE</span>

                        <strong>
                            {prediction?.model_score ==
                            null
                                ? "\u2014"
                                : Number(
                                    prediction.model_score
                                ).toFixed(4)}
                        </strong>

                        <small>
                            Uncalibrated unless separately
                            validated
                        </small>
                    </div>

                    <div className="ai-result-card">
                        <span>MODEL VERSION</span>

                        <strong>
                            {prediction?.model_version ??
                                "\u2014"}
                        </strong>

                        <small>
                            Backend-provided artifact
                            identifier
                        </small>
                    </div>
                </div>

                <div className="evidence-result-box">
                    <div className="evidence-result-title">
                        <ShieldAlert size={18} />
                        SUPPORTING EVIDENCE
                    </div>

                    {prediction?.evidence?.length ? (
                        <p>
                            {prediction.evidence.join(
                                " \u2022 "
                            )}
                        </p>
                    ) : (
                        <p>
                            No model evidence is currently
                            available.
                        </p>
                    )}
                </div>
            </section>
        </div>
    );
}

export default Analysis;