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
                                    : "#ff7a2f",
                                fillColor: "#ff6b21",
                                fillOpacity:
                                    selected ? 0.95 : 0.7,
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
                <div>
                    <span className="legend-dot" />
                    Thermal event
                </div>

                <div>
                    <span className="legend-ring" />
                    Selected event
                </div>
            </div>
        </div>
    );
}

export default IndiaMap;