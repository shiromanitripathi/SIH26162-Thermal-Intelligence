const API_BASE =
    import.meta.env.VITE_API_BASE_URL ||
    "http://localhost:8000";

export async function getHealth() {
    const response = await fetch(`${API_BASE}/api/health`);

    if (!response.ok) {
        throw new Error("Backend health check failed");
    }

    return response.json();
}

export async function getHotspots(params = {}) {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            query.append(key, value);
        }
    });

    const queryString = query.toString();

    const response = await fetch(
        `${API_BASE}/api/hotspots${queryString ? `?${queryString}` : ""
        }`
    );

    if (!response.ok) {
        throw new Error("Unable to retrieve hotspots");
    }

    return response.json();
}

export async function getHotspot(id) {
    const response = await fetch(
        `${API_BASE}/api/hotspots/${id}`
    );

    if (!response.ok) {
        throw new Error("Unable to retrieve hotspot");
    }

    return response.json();
}

export async function predictHotspot(payload) {
    const response = await fetch(
        `${API_BASE}/api/predict`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        }
    );

    if (!response.ok) {
        throw new Error("AI prediction request failed");
    }

    return response.json();
}