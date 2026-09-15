import { useState } from "react";
import {
    Search,
    MapPin,
    Clock3,
    Flame,
    Activity,
    ArrowRight,
} from "lucide-react";

const demoEvents = [
    {
        id: "EVENT-DEMO-001",
        region: "Northern India",
        latitude: 28.6139,
        longitude: 77.209,
    },
    {
        id: "EVENT-DEMO-002",
        region: "Western India",
        latitude: 19.076,
        longitude: 72.8777,
    },
    {
        id: "EVENT-DEMO-003",
        region: "Eastern India",
        latitude: 22.5726,
        longitude: 88.3639,
    },
    {
        id: "EVENT-DEMO-004",
        region: "Southern India",
        latitude: 13.0827,
        longitude: 80.2707,
    },
];

function Events() {
    const [search, setSearch] = useState("");
    const [selectedEvent, setSelectedEvent] = useState(demoEvents[0]);

    const filteredEvents = demoEvents.filter(
        (event) =>
            event.id.toLowerCase().includes(search.toLowerCase()) ||
            event.region.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="events-page">

            <section className="events-header">
                <div className="events-eyebrow">
                    EXPLORE / EVENTS
                </div>

                <h1>Event Explorer</h1>

                <p>
                    Search, filter and inspect detected thermal observations.
                </p>

                <div className="events-backend-notice">
                    EVENT DATA AWAITING BACKEND
                </div>
            </section>

            <section className="event-summary-grid">

                <div className="event-summary-card">
                    <Activity size={20} />
                    <span>THERMAL EVENTS</span>
                    <strong>—</strong>
                    <small>Not available yet</small>
                </div>

                <div className="event-summary-card">
                    <Clock3 size={20} />
                    <span>PERSISTENT EVENTS</span>
                    <strong>—</strong>
                    <small>Not available yet</small>
                </div>

                <div className="event-summary-card">
                    <Flame size={20} />
                    <span>RECURRENT SOURCES</span>
                    <strong>—</strong>
                    <small>Not available yet</small>
                </div>

                <div className="event-summary-card">
                    <MapPin size={20} />
                    <span>PRIORITY EVENTS</span>
                    <strong>—</strong>
                    <small>Not available yet</small>
                </div>

            </section>

            <section className="events-controls">

                <div className="event-search">
                    <Search size={18} />

                    <input
                        type="text"
                        placeholder="Search event ID or region..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                <select>
                    <option>All Event Types</option>
                    <option>Thermal Event</option>
                    <option>Persistent Source</option>
                    <option>Recurring Source</option>
                </select>

                <select>
                    <option>Latest First</option>
                    <option>Oldest First</option>
                </select>

            </section>

            <section className="events-workspace">

                <div className="event-list-panel">

                    <div className="event-panel-header">
                        <div>
                            <span className="panel-kicker">
                                DETECTED EVENTS
                            </span>

                            <h2>Event Registry</h2>
                        </div>

                        <span className="event-count">
                            {filteredEvents.length} development events
                        </span>
                    </div>

                    <div className="event-list">

                        {filteredEvents.length === 0 ? (
                            <div className="event-empty">
                                No matching events found.
                            </div>
                        ) : (
                            filteredEvents.map((event) => (
                                <button
                                    key={event.id}
                                    className={`event-row ${selectedEvent?.id === event.id
                                            ? "selected"
                                            : ""
                                        }`}
                                    onClick={() => setSelectedEvent(event)}
                                >

                                    <div className="event-row-icon">
                                        <Flame size={18} />
                                    </div>

                                    <div className="event-row-content">
                                        <strong>{event.id}</strong>
                                        <span>{event.region}</span>
                                    </div>

                                    <ArrowRight size={17} />

                                </button>
                            ))
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
                                    ? selectedEvent.id
                                    : "No Event Selected"}
                            </h2>
                        </div>

                    </div>

                    {selectedEvent && (
                        <>
                            <div className="event-status-badge">
                                DEVELOPMENT MOCK
                            </div>

                            <div className="event-location-block">

                                <MapPin size={19} />

                                <div>
                                    <span>REGION</span>
                                    <strong>{selectedEvent.region}</strong>
                                </div>

                            </div>

                            <div className="event-detail-grid">

                                <div>
                                    <span>LATITUDE</span>
                                    <strong>{selectedEvent.latitude}</strong>
                                </div>

                                <div>
                                    <span>LONGITUDE</span>
                                    <strong>{selectedEvent.longitude}</strong>
                                </div>

                                <div>
                                    <span>OBSERVATIONS</span>
                                    <strong>—</strong>
                                </div>

                                <div>
                                    <span>DURATION</span>
                                    <strong>—</strong>
                                </div>

                                <div>
                                    <span>RECURRENCE</span>
                                    <strong>—</strong>
                                </div>

                                <div>
                                    <span>THERMAL INTENSITY</span>
                                    <strong>—</strong>
                                </div>

                            </div>

                            <div className="event-history-box">

                                <div className="history-title">
                                    <Clock3 size={17} />
                                    TEMPORAL HISTORY
                                </div>

                                <p>
                                    Historical observation data will appear here
                                    when the backend event aggregation is connected.
                                </p>

                            </div>

                            <a
                                href={`/analysis?event=${selectedEvent.id}`}
                                className="event-analyze-button"
                            >
                                ANALYZE EVENT
                                <ArrowRight size={18} />
                            </a>

                        </>
                    )}

                </div>

            </section>

            <section className="event-concept">

                <span className="panel-kicker">
                    EVENT FORMATION
                </span>

                <h2>
                    From observations to thermal events
                </h2>

                <p>
                    Individual FIRMS observations can be grouped using
                    spatial and temporal behavior. The resulting event can
                    then be evaluated using persistence, recurrence,
                    thermal history and geographic context.
                </p>

                <div className="concept-flow">
                    <span>FIRMS OBSERVATION</span>
                    <ArrowRight size={18} />
                    <span>SPATIAL / TEMPORAL GROUPING</span>
                    <ArrowRight size={18} />
                    <span>EVENT</span>
                    <ArrowRight size={18} />
                    <span>INVESTIGATION</span>
                </div>

            </section>

        </div>
    );
}

export default Events;