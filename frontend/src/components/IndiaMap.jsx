import {
    CircleMarker,
    MapContainer,
    Popup,
    TileLayer,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

function hotspotIdentity(hotspot) {
    return String(
        hotspot?.event_id ??
        hotspot?.grid_id ??
        hotspot?.id ??
        ""
    );
}

const CLASS_STYLE = {
    0: { label: "Vegetation / agricultural", color: "#22c55e" },
    1: { label: "Industrial-fire candidate", color: "#ef4444" },
    2: { label: "Persistent thermal source", color: "#f59e0b" },
    3: { label: "Other / ephemeral", color: "#38bdf8" },
};

function getHotspotStyle(hotspot) {
    const raw = hotspot?.target_multiclass;
    if (raw !== null && raw !== undefined && raw !== "") {
        const entry = CLASS_STYLE[Number(raw)];
        if (entry) return entry;
    }
    return { label: "Unclassified", color: "#94a3b8" };
}

function IndiaMap({
    hotspots = [],
    selectedHotspot,
    onSelectHotspot,
}) {
    const selectedIdentity = hotspotIdentity(selectedHotspot);

    return (
        <div className="india-map-wrapper">
            <MapContainer
                center={[22.5, 79]}
                zoom={5}
                minZoom={4}
                maxZoom={9}
                scrollWheelZoom={true}
                className="india-map"
            >
                <TileLayer
                    attribution="&copy; OpenStreetMap contributors"
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {hotspots.map((hotspot) => {
                    const latitude = Number(hotspot.latitude);
                    const longitude = Number(hotspot.longitude);

                    if (
                        !Number.isFinite(latitude) ||
                        !Number.isFinite(longitude)
                    ) {
                        return null;
                    }

                    const identity = hotspotIdentity(hotspot);
                    const selected =
                        identity !== "" &&
                        identity === selectedIdentity;
                    const classStyle = getHotspotStyle(hotspot);

                    return (
                        <CircleMarker
                            key={
                                identity ||
                                `${latitude}-${longitude}`
                            }
                            center={[latitude, longitude]}
                            radius={selected ? 11 : 7}
                            pathOptions={{
                                color: selected
                                    ? "#ffffff"
                                    : classStyle.color,
                                fillColor: classStyle.color,
                                fillOpacity:
                                    selected ? 0.95 : 0.75,
                                weight: selected ? 3 : 1.5,
                            }}
                            eventHandlers={{
                                click: () =>
                                    onSelectHotspot?.(hotspot),
                            }}
                        >
                            <Popup>
                                <strong>
                                    {identity ||
                                        "Thermal event"}
                                </strong>

                                <br />
                                {classStyle.label}

                                <br />

                                {latitude.toFixed(4)},{" "}
                                {longitude.toFixed(4)}

                                {hotspot.active_days != null && (
                                    <>
                                        <br />
                                        Active days:{" "}
                                        {hotspot.active_days}
                                    </>
                                )}

                                {hotspot.mean_frp != null && (
                                    <>
                                        <br />
                                        Mean FRP:{" "}
                                        {Number(
                                            hotspot.mean_frp
                                        ).toFixed(2)}
                                    </>
                                )}
                            </Popup>
                        </CircleMarker>
                    );
                })}
            </MapContainer>

            <div className="map-overlay">
                <div className="map-overlay-title">
                    INDIA / THERMAL ACTIVITY
                </div>

                <div className="map-overlay-subtitle">
                    Backend thermal-event layer
                </div>
            </div>

            <div className="map-legend">
                {Object.entries(CLASS_STYLE).map(([key, item]) => (
                    <div key={key}>
                        <span
                            className="legend-dot"
                            style={{ backgroundColor: item.color }}
                        />
                        {item.label}
                    </div>
                ))}

                <div>
                    <span className="legend-ring" />
                    Selected event
                </div>
            </div>
        </div>
    );
}

export default IndiaMap;