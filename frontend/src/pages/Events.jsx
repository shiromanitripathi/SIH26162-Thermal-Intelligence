import {
    useEffect,
    useMemo,
    useState,
} from "react";
import {
    Activity,
    ArrowRight,
    Clock3,
    Flame,
    MapPin,
    Search,
} from "lucide-react";

import {
    getHotspot,
    getHotspots,
    getHotspotStats,
} from "../services/api";

function eventIdentity(event) {
    return String(
        event?.event_id ??
        event?.grid_id ??
        event?.id ??
        ""
    );
}

function formatInteger(value) {
    return Number.isFinite(Number(value))
        ? Number(value).toLocaleString()
        : "—";
}

function Events() {
    const [search, setSearch] = useState("");
    const [events, setEvents] = useState([]);
    const [
        selectedEvent,
        setSelectedEvent,
    ] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;

        async function load() {
            setLoading(true);

            try {
                const [eventResult, statsResult] =
                    await Promise.all([
                        getHotspots({ limit: 500 }),
                        getHotspotStats(),
                    ]);

                if (cancelled) {
                    return;
                }

                setEvents(eventResult);
                setStats(statsResult);
                setSelectedEvent(
                    eventResult[0] ?? null
                );
                setError("");
            } catch (err) {
                if (!cancelled) {
                    setError(err.message);
                    setEvents([]);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        load();

        return () => {
            cancelled = true;
        };
    }, []);

    const filteredEvents = useMemo(() => {
        const query = search
            .trim()
            .toLowerCase();

        if (!query) {
            return events;
        }

        return events.filter((event) =>
            [
                eventIdentity(event),
                event.grid_id,
                event.event_id,
                event.id,
            ]
                .filter(Boolean)
                .some((value) =>
                    String(value)
                        .toLowerCase()
                        .includes(query)
                )
        );
    }, [events, search]);

    async function selectEvent(event) {
        setSelectedEvent(event);

        try {
            const detail = await getHotspot(
                eventIdentity(event)
            );
            setSelectedEvent(detail);
        } catch {
            // Keep real list data if detail retrieval fails.
        }
    }

    return (
        <div className="events-page">
            <section className="events-header">
                <div className="events-eyebrow">
                    EXPLORE / EVENTS
                </div>

                <h1>Event Explorer</h1>

                <p>
                    Search and inspect thermal-event cells
                    loaded from PostgreSQL/PostGIS.
                </p>

                {error && (
                    <div className="events-backend-notice">
                        EVENT DATA UNAVAILABLE: {error}
                    </div>
                )}
            </section>

            <section className="event-summary-grid">
                <div className="event-summary-card">
                    <Activity size={20} />
                    <span>
                        THERMAL EVENT CELLS
                    </span>
                    <strong>
                        {formatInteger(
                            stats?.total_spatial_cells
                        )}
                    </strong>
                    <small>Stored spatial cells</small>
                </div>

                <div className="event-summary-card">
                    <Clock3 size={20} />
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

                <div className="event-summary-card">
                    <Flame size={20} />
                    <span>MAX ACTIVE DAYS</span>
                    <strong>
                        {formatInteger(
                            stats?.max_active_days
                        )}
                    </strong>
                    <small>
                        Maximum observed active days
                    </small>
                </div>

                <div className="event-summary-card">
                    <MapPin size={20} />
                    <span>OSM CONTEXT CELLS</span>
                    <strong>
                        {formatInteger(
                            stats?.osm_context_cells
                        )}
                    </strong>
                    <small>
                        Context explicitly available
                    </small>
                </div>
            </section>

            <section
                id="hotspot-search"
                className="events-controls nav-section-target"
            >
                <div className="event-search">
                    <Search size={18} />

                    <input
                        type="text"
                        placeholder="Search event_id, grid_id or database ID..."
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                    />
                </div>
            </section>

            <section
                id="event-explorer"
                className="events-workspace nav-section-target"
            >
                <div className="event-list-panel">
                    <div className="event-panel-header">
                        <div>
                            <span className="panel-kicker">
                                BACKEND EVENTS
                            </span>
                            <h2>Event Registry</h2>
                        </div>

                        <span className="event-count">
                            {loading
                                ? "loading"
                                : `${filteredEvents.length} events`}
                        </span>
                    </div>

                    <div className="event-list">
                        {filteredEvents.length ===
                        0 ? (
                            <div className="event-empty">
                                {loading
                                    ? "Loading events..."
                                    : "No matching events found."}
                            </div>
                        ) : (
                            filteredEvents.map(
                                (event) => (
                                    <button
                                        key={eventIdentity(
                                            event
                                        )}
                                        className={`event-row ${
                                            eventIdentity(
                                                selectedEvent
                                            ) ===
                                            eventIdentity(
                                                event
                                            )
                                                ? "selected"
                                                : ""
                                        }`}
                                        onClick={() =>
                                            selectEvent(
                                                event
                                            )
                                        }
                                    >
                                        <div className="event-row-icon">
                                            <Flame
                                                size={
                                                    18
                                                }
                                            />
                                        </div>

                                        <div className="event-row-content">
                                            <strong>
                                                {eventIdentity(
                                                    event
                                                )}
                                            </strong>
                                            <span>
                                                {Number(
                                                    event.latitude
                                                ).toFixed(
                                                    4
                                                )}
                                                ,{" "}
                                                {Number(
                                                    event.longitude
                                                ).toFixed(
                                                    4
                                                )}
                                            </span>
                                        </div>

                                        <ArrowRight
                                            size={17}
                                        />
                                    </button>
                                )
                            )
                        )}
                    </div>
                </div>

                <div className="event-inspector">
                    <div className="event-panel-header">
                        <div>
                            <span className="panel-kicker">
                                EVENT INSPECTOR
                            </span>

                            <h2>
                                {selectedEvent
                                    ? eventIdentity(
                                        selectedEvent
                                    )
                                    : "No Event Selected"}
                            </h2>
                        </div>
                    </div>

                    {selectedEvent && (
                        <>
                            <div className="event-location-block">
                                <MapPin size={19} />

                                <div>
                                    <span>
                                        COORDINATES
                                    </span>
                                    <strong>
                                        {Number(
                                            selectedEvent.latitude
                                        ).toFixed(5)}
                                        ,{" "}
                                        {Number(
                                            selectedEvent.longitude
                                        ).toFixed(5)}
                                    </strong>
                                </div>
                            </div>

                            <div className="event-detail-grid">
                                <div>
                                    <span>
                                        OBSERVATIONS
                                    </span>
                                    <strong>
                                        {selectedEvent.observation_count ??
                                            "—"}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        ACTIVE DAYS
                                    </span>
                                    <strong>
                                        {selectedEvent.active_days ??
                                            "—"}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        PERSISTENCE DAYS
                                    </span>
                                    <strong>
                                        {selectedEvent.persistence_days ??
                                            "—"}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        RECURRENCE RATIO
                                    </span>
                                    <strong>
                                        {selectedEvent.recurrence_ratio ==
                                        null
                                            ? "—"
                                            : Number(
                                                selectedEvent.recurrence_ratio
                                            ).toFixed(
                                                3
                                            )}
                                    </strong>
                                </div>

                                <div>
                                    <span>MEAN FRP</span>
                                    <strong>
                                        {selectedEvent.mean_frp ==
                                        null
                                            ? "—"
                                            : Number(
                                                selectedEvent.mean_frp
                                            ).toFixed(
                                                2
                                            )}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        FIRMS CONFIDENCE
                                    </span>
                                    <strong>
                                        {selectedEvent.confidence ==
                                        null
                                            ? "—"
                                            : Number(
                                                selectedEvent.confidence
                                            ).toFixed(
                                                2
                                            )}
                                    </strong>
                                </div>
                            </div>

                            <div className="event-history-box">
                                <div className="history-title">
                                    <Clock3 size={17} />
                                    OBSERVATION PERIOD
                                </div>

                                <p>
                                    {selectedEvent.first_seen &&
                                    selectedEvent.last_seen
                                        ? `${selectedEvent.first_seen} to ${selectedEvent.last_seen}`
                                        : "Observation dates are not available for this event."}
                                </p>
                            </div>

                            <a
                                href={`/analysis?event=${encodeURIComponent(
                                    eventIdentity(
                                        selectedEvent
                                    )
                                )}`}
                                className="event-analyze-button"
                            >
                                ANALYZE EVENT
                                <ArrowRight size={18} />
                            </a>
                        </>
                    )}
                </div>
            </section>
        </div>
    );
}

export default Events;