MOCK_HOTSPOTS = [
    {
        "id": 1,
        "latitude": 31.2240,
        "longitude": 75.7700,
        "brightness": 320.5,
        "confidence": 0.87,
    },
    {
        "id": 2,
        "latitude": 31.2300,
        "longitude": 75.7800,
        "brightness": 341.2,
        "confidence": 0.92,
    },
]


def get_hotspots():
    return MOCK_HOTSPOTS
def get_hotspot(hotspot_id: int):
    for hotspot in MOCK_HOTSPOTS:
        if hotspot["id"] == hotspot_id:
            return hotspot

    return None