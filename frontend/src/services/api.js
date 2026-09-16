const API_BASE =
    import.meta.env.VITE_API_BASE_URL ||
    "http://localhost:8000";

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            ...(options.body
                ? { "Content-Type": "application/json" }
                : {}),
            ...(options.headers || {}),
        },
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const detail =
            typeof data?.detail === "string"
                ? data.detail
                : `Request failed with status ${response.status}`;

        const error = new Error(detail);
        error.status = response.status;
        error.data = data;

        throw error;
    }

    return data;
}

function buildQuery(params = {}) {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            query.set(key, String(value));
        }
    });

    const value = query.toString();

    return value ? `?${value}` : "";
}

function encodeId(id) {
    if (
        id === undefined ||
        id === null ||
        String(id).trim() === ""
    ) {
        throw new Error("A hotspot ID is required");
    }

    return encodeURIComponent(String(id));
}

export function getHealth() {
    return apiRequest("/api/health");
}

export function getHotspots(params = {}) {
    return apiRequest(
        `/api/hotspots${buildQuery(params)}`
    );
}

export function getHotspot(id) {
    return apiRequest(
        `/api/hotspots/${encodeId(id)}`
    );
}

export function getHotspotStats() {
    return apiRequest("/api/hotspots/stats");
}

export function getNearbyHotspots({
    latitude,
    longitude,
    radius_meters = 2000,
}) {
    return apiRequest(
        `/api/hotspots/nearby${buildQuery({
            latitude,
            longitude,
            radius_meters,
        })}`
    );
}

export function getHotspotClassification(id) {
    return apiRequest(
        `/api/hotspots/${encodeId(id)}/classify`
    );
}

export function classifyHotspot(payload) {
    return apiRequest("/api/hotspots/classify", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

// Explicit/manual model-input endpoint.
// Normal hotspot classification should use getHotspotClassification(id).
export function predictHotspot(payload) {
    return apiRequest("/api/predict", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export { API_BASE };