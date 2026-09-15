import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
    Activity,
    AlertTriangle,
    BrainCircuit,
    CheckCircle2,
    Clock3,
    Flame,
    MapPin,
    Radio,
    ShieldAlert,
    Target,
} from "lucide-react";

import { predictHotspot } from "../services/api";

const demoEvents = {
    "EVENT-DEMO-001": {
        id: "EVENT-DEMO-001",
        region: "Northern India",
        latitude: 28.6139,
        longitude: 77.209,
    },

    "EVENT-DEMO-002": {
        id: "EVENT-DEMO-002",
        region: "Western India",
        latitude: 19.076,
        longitude: 72.8777,
    },

    "EVENT-DEMO-003": {
        id: "EVENT-DEMO-003",
        region: "Eastern India",
        latitude: 22.5726,
        longitude: 88.3639,
    },

    "EVENT-DEMO-004": {
        id: "EVENT-DEMO-004",
        region: "Southern India",
        latitude: 13.0827,
        longitude: 80.2707,
    },
};

function Analysis() {
    const [searchParams] = useSearchParams();

    const eventId =
        searchParams.get("event") ||
        searchParams.get("hotspot") ||
        "EVENT-DEMO-001";

    const event =
        demoEvents[eventId] || {
            id: eventId,
            region: "Location not available",
            latitude: null,
            longitude: null,
        };

    const [analysisState, setAnalysisState] = useState("idle");
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState("");

    async function handleAnalyze() {
        setError("");
        setPrediction(null);
        setAnalysisState("loading");

        try {
            const payload = {
                event_id: event.id,
                latitude: event.latitude,
                longitude: event.longitude,
            };

            const result = await predictHotspot(payload);

            setPrediction(result);
            setAnalysisState("success");
        } catch (err) {
            console.error(err);

            setAnalysisState("error");
            setError(
                "AI analysis is not available yet. Connect the backend /api/predict endpoint to run the assessment."
            );
        }
    }

    return (
        <div className="analysis-page">

            {/* HEADER */}

            <section className="analysis-header">

                <div className="analysis-eyebrow">
                    ANALYSIS / AI ASSESSMENT
                </div>

                <h1>Thermal Intelligence</h1>

                <p>
                    Evaluate thermal observations using temporal,
                    spatial and contextual evidence.
                </p>

                <div className="analysis-event-badge">
                    <Radio size={15} />
                    SELECTED EVENT: {event.id}
                </div>

            </section>

            {/* DEVELOPMENT NOTICE */}

            <div className="analysis-notice">
                <AlertTriangle size={18} />

                <div>
                    <strong>DEVELOPMENT MODE</strong>

                    <span>
                        Scientific observations and AI assessment values will
                        appear only when supplied by the connected backend.
                    </span>
                </div>
            </div>

            {/* SELECTED SOURCE */}

            <section className="analysis-source-card">

                <div className="analysis-section-heading">

                    <div>
                        <span className="analysis-kicker">
                            SELECTED THERMAL EVENT
                        </span>

                        <h2>{event.id}</h2>
                    </div>

                    <div className="source-status">
                        DEVELOPMENT MOCK
                    </div>

                </div>

                <div className="analysis-location">

                    <MapPin size={20} />

                    <div>
                        <span>REGION</span>
                        <strong>{event.region}</strong>
                    </div>

                </div>

                <div className="analysis-coordinates">

                    <div>
                        <span>LATITUDE</span>
                        <strong>
                            {event.latitude ?? "Not available yet"}
                        </strong>
                    </div>

                    <div>
                        <span>LONGITUDE</span>
                        <strong>
                            {event.longitude ?? "Not available yet"}
                        </strong>
                    </div>

                </div>

            </section>

            {/* EVIDENCE GRID */}

            <section className="analysis-evidence-grid">

                {/* THERMAL */}

                <div className="evidence-card">

                    <div className="evidence-card-header">
                        <div className="evidence-icon">
                            <Flame size={19} />
                        </div>

                        <div>
                            <span>THERMAL EVIDENCE</span>
                            <h3>Thermal Signal</h3>
                        </div>
                    </div>

                    <div className="evidence-values">

                        <div>
                            <span>FRP / THERMAL INTENSITY</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>FIRMS CONFIDENCE</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>OBSERVATION COUNT</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                    </div>

                </div>

                {/* TEMPORAL */}

                <div className="evidence-card">

                    <div className="evidence-card-header">
                        <div className="evidence-icon">
                            <Clock3 size={19} />
                        </div>

                        <div>
                            <span>TEMPORAL EVIDENCE</span>
                            <h3>Thermal History</h3>
                        </div>
                    </div>

                    <div className="evidence-values">

                        <div>
                            <span>PERSISTENCE</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>RECURRENCE</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>DURATION</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                    </div>

                </div>

                {/* CONTEXT */}

                <div className="evidence-card">

                    <div className="evidence-card-header">
                        <div className="evidence-icon">
                            <Target size={19} />
                        </div>

                        <div>
                            <span>GEOGRAPHIC CONTEXT</span>
                            <h3>Context Intelligence</h3>
                        </div>
                    </div>

                    <div className="evidence-values">

                        <div>
                            <span>INDUSTRIAL PROXIMITY</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>OSM CONTEXT</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                        <div>
                            <span>LAND / GEOGRAPHIC CONTEXT</span>
                            <strong>—</strong>
                            <small>Not available yet</small>
                        </div>

                    </div>

                </div>

            </section>

            {/* ANALYZE */}

            <section className="ai-action-section">

                <div className="ai-action-content">

                    <div className="ai-action-icon">
                        <BrainCircuit size={27} />
                    </div>

                    <div>
                        <span className="analysis-kicker">
                            MACHINE LEARNING ASSESSMENT
                        </span>

                        <h2>Analyze this thermal event</h2>

                        <p>
                            Send validated event features to the AI assessment
                            service for classification and supporting evidence.
                        </p>
                    </div>

                </div>

                <button
                    className="analyze-ai-button"
                    onClick={handleAnalyze}
                    disabled={analysisState === "loading"}
                >
                    <BrainCircuit size={18} />

                    {analysisState === "loading"
                        ? "ANALYZING..."
                        : "ANALYZE WITH AI"}
                </button>

            </section>

            {/* ERROR */}

            {analysisState === "error" && (

                <div className="analysis-error">

                    <AlertTriangle size={19} />

                    <div>
                        <strong>AI SERVICE UNAVAILABLE</strong>

                        <p>{error}</p>
                    </div>

                </div>

            )}

            {/* RESULT */}

            <section className="ai-result-section">

                <div className="analysis-section-heading">

                    <div>
                        <span className="analysis-kicker">
                            AI ASSESSMENT RESULT
                        </span>

                        <h2>Classification & Evidence</h2>
                    </div>

                    {analysisState === "success" && (
                        <div className="result-available">
                            <CheckCircle2 size={16} />
                            RESULT AVAILABLE
                        </div>
                    )}

                </div>

                <div className="ai-result-grid">

                    <div className="ai-result-card primary">

                        <span>CLASSIFICATION</span>

                        <strong>
                            {prediction?.classification ||
                                prediction?.label ||
                                "Not available yet"}
                        </strong>

                        <small>
                            Backend-generated assessment
                        </small>

                    </div>

                    <div className="ai-result-card">

                        <span>CONFIDENCE</span>

                        <strong>
                            {prediction?.confidence ?? "—"}
                        </strong>

                        <small>
                            Backend-generated value
                        </small>

                    </div>

                    <div className="ai-result-card">

                        <span>INVESTIGATION PRIORITY</span>

                        <strong>
                            {prediction?.priority ||
                                prediction?.investigation_priority ||
                                "Not available yet"}
                        </strong>

                        <small>
                            Only shown when supplied by backend
                        </small>

                    </div>

                </div>

                <div className="evidence-result-box">

                    <div className="evidence-result-title">
                        <ShieldAlert size={18} />
                        SUPPORTING EVIDENCE
                    </div>

                    {prediction?.evidence ? (
                        <p>
                            {Array.isArray(prediction.evidence)
                                ? prediction.evidence.join(" • ")
                                : prediction.evidence}
                        </p>
                    ) : (
                        <p>
                            AI-generated supporting evidence will appear here
                            when the prediction service is connected.
                        </p>
                    )}

                </div>

            </section>

            {/* TIMELINE */}

            <section className="analysis-timeline-section">

                <div className="analysis-section-heading">

                    <div>
                        <span className="analysis-kicker">
                            TEMPORAL ANALYSIS
                        </span>

                        <h2>Observation Timeline</h2>
                    </div>

                </div>

                <div className="timeline-empty">

                    <Clock3 size={25} />

                    <strong>
                        Historical observations not available yet
                    </strong>

                    <span>
                        The timeline will be populated from backend FIRMS
                        observations after event aggregation is connected.
                    </span>

                </div>

            </section>

        </div>
    );
}

export default Analysis;