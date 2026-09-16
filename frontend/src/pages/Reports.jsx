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

function Reports() {
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

    function handlePrint() {
        window.print();
    }

    return (
        <div className="reports-page">

            {/* SCREEN HEADER */}

            <section className="reports-header no-print">

                <div className="reports-eyebrow">
                    REPORTS / INVESTIGATION
                </div>

                <h1>Investigation Report</h1>

                <p>
                    Structured analyst report for a selected thermal event.
                </p>

                <div
                    id="export-print"
                    className="report-toolbar nav-section-target"
                >

                    <a
                        href={`/analysis?event=${event.id}`}
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

            {/* DEVELOPMENT NOTICE */}

            <div className="report-development no-print">

                <Radio size={18} />

                <div>
                    <strong>DEVELOPMENT MODE</strong>

                    <span>
                        This report contains only available data. Missing
                        observations, analytics and AI results are not
                        fabricated.
                    </span>
                </div>

            </div>

            {/* REPORT DOCUMENT */}

            <article
                id="investigation-report"
                className="investigation-report nav-section-target"
            >

                {/* REPORT TOP */}

                <header className="report-document-header">

                    <div className="report-brand">

                        <div className="report-brand-icon">
                            <Flame size={22} />
                        </div>

                        <div>
                            <strong>FIRMS</strong>
                            <span>THERMAL INTELLIGENCE</span>
                        </div>

                    </div>

                    <div className="report-document-type">
                        <span>INVESTIGATION REPORT</span>
                        <strong>{event.id}</strong>
                    </div>

                </header>

                {/* STATUS */}

                <div className="report-status-row">

                    <div className="report-status">
                        DEVELOPMENT MOCK
                    </div>

                    <div className="report-generated">
                        <CalendarDays size={15} />
                        Generated from available system data
                    </div>

                </div>

                {/* EXECUTIVE SUMMARY */}

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
                            This report documents the available information
                            associated with thermal event{" "}
                            <strong>{event.id}</strong>.
                        </p>

                        <p>
                            The current development dataset does not provide
                            validated event analytics or an AI assessment.
                            Therefore, no classification, confidence,
                            persistence or investigation score is asserted.
                        </p>

                    </div>

                </section>

                {/* LOCATION */}

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
                            <strong>{event.id}</strong>
                        </div>

                        <div className="report-info-item">
                            <span>REGION</span>
                            <strong>{event.region}</strong>
                        </div>

                        <div className="report-info-item">
                            <span>LATITUDE</span>
                            <strong>
                                {event.latitude ?? "Not available yet"}
                            </strong>
                        </div>

                        <div className="report-info-item">
                            <span>LONGITUDE</span>
                            <strong>
                                {event.longitude ?? "Not available yet"}
                            </strong>
                        </div>

                    </div>

                </section>

                {/* THERMAL DATA */}

                <section className="report-section">

                    <div className="report-section-title">

                        <Flame size={18} />

                        <div>
                            <span>03</span>
                            <h2>Thermal Observations</h2>
                        </div>

                    </div>

                    <div className="report-info-grid">

                        <div className="report-info-item">
                            <span>OBSERVATION PERIOD</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>OBSERVATION COUNT</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>THERMAL INTENSITY / FRP</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>FIRMS CONFIDENCE</span>
                            <strong>Not available yet</strong>
                        </div>

                    </div>

                </section>

                {/* TEMPORAL */}

                <section className="report-section">

                    <div className="report-section-title">

                        <Clock3 size={18} />

                        <div>
                            <span>04</span>
                            <h2>Persistence & Recurrence</h2>
                        </div>

                    </div>

                    <div className="report-info-grid">

                        <div className="report-info-item">
                            <span>PERSISTENCE</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>DURATION</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>RECURRENCE</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div className="report-info-item">
                            <span>TIME-OF-DAY PATTERN</span>
                            <strong>Not available yet</strong>
                        </div>

                    </div>

                </section>

                {/* CONTEXT */}

                <section className="report-section">

                    <div className="report-section-title">

                        <MapPin size={18} />

                        <div>
                            <span>05</span>
                            <h2>Geographic Context</h2>
                        </div>

                    </div>

                    <div className="report-context-box">

                        <div>
                            <span>INDUSTRIAL CONTEXT</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div>
                            <span>OSM / GEOGRAPHIC CONTEXT</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div>
                            <span>LAND / SATELLITE CONTEXT</span>
                            <strong>Not available yet</strong>
                        </div>

                    </div>

                    <p className="report-note">
                        Geographic proximity is contextual evidence and does
                        not by itself establish the cause or source of a
                        thermal observation.
                    </p>

                </section>

                {/* AI */}

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
                            <span>CLASSIFICATION</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div>
                            <span>CONFIDENCE / ASSESSMENT</span>
                            <strong>Not available yet</strong>
                        </div>

                        <div>
                            <span>INVESTIGATION PRIORITY</span>
                            <strong>Not available yet</strong>
                        </div>

                    </div>

                    <div className="report-evidence">

                        <span>SUPPORTING EVIDENCE</span>

                        <p>
                            AI-generated supporting evidence will appear here
                            after the prediction service provides a validated
                            assessment.
                        </p>

                    </div>

                </section>

                {/* PROVENANCE */}

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
                            <span>PRIMARY OBSERVATION SOURCE</span>
                            <strong>NASA FIRMS</strong>
                        </div>

                        <div>
                            <span>GEOGRAPHIC CONTEXT</span>
                            <strong>
                                OSM / validated geospatial data
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
                            <strong>Development report</strong>
                        </div>

                    </div>

                </section>

                {/* DISCLAIMER */}

                <footer className="report-footer">

                    <strong>
                        ANALYST DECISION SUPPORT
                    </strong>

                    <p>
                        Thermal observations are indicators requiring
                        contextual interpretation. This report does not by
                        itself establish the source or cause of a thermal
                        anomaly. Investigation conclusions should rely on
                        validated data and appropriate domain verification.
                    </p>

                    <div>
                        FIRMS THERMAL INTELLIGENCE • SIH26162 • NTRO
                    </div>

                </footer>

            </article>

        </div>
    );
}

export default Reports;