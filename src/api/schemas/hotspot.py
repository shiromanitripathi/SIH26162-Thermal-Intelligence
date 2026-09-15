from pydantic import BaseModel


class Hotspot(BaseModel):
    id: int
    latitude: float
    longitude: float
    brightness: float
    confidence: float