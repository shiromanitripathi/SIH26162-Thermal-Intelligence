import {
    MapContainer,
    TileLayer,
    CircleMarker,
    Popup,
    useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

function MapController() {
    const map = useMap();

    return null;
}

function IndiaMap({
    hotspots = [],
    selectedHotspot,
    onSelectHotspot,
}) {
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
                    attribution='&copy; OpenStreetMap contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapController />

                {hotspots.map((hotspot) => {
                    const latitude =
                        Number(hotspot.latitude);

                    const longitude =
                        Number(hotspot.longitude);

                    if (
                        !Number.isFinite(latitude) ||
                        !Number.isFinite(longitude)
                    ) {
                        return null;
                    }

                    const selected =
                        selectedHotspot?.id === hotspot.id;

                    return (
                        <CircleMarker
                            key={hotspot.id}
                            center={[
                                latitude,
                                longitude,
                            ]}
                            radius={selected ? 11 : 7}
                            pathOptions={{
                                color: selected
                                    ? "#ffffff"
                                    : "#ff7a2f",

                                fillColor: "#ff6b21",

                                fillOpacity:
                                    selected ? 0.95 : 0.7,

                                weight:
                                    selected ? 3 : 1.5,
                            }}
                            eventHandlers={{
                                click: () =>
                                    onSelectHotspot?.(
                                        hotspot
                                    ),
                            }}
                        >
                            <Popup>
                                <strong>
                                    {hotspot.id ||
                                        "Thermal Observation"}
                                </strong>

                                <br />

                                {hotspot.location ||
                                    "Location not available"}

                                <br />

                                {hotspot.isMock
                                    ? "DEVELOPMENT MOCK"
                                    : "FIRMS observation"}
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
                    FIRMS observation layer
                </div>
            </div>

            <div className="map-legend">
                <div>
                    <span className="legend-dot" />
                    Thermal observation
                </div>

                <div>
                    <span className="legend-ring" />
                    Selected source
                </div>
            </div>

        </div>
    );
}

export default IndiaMap;