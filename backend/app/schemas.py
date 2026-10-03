from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Category(str, Enum):
    garbage_dump = "garbage_dump"
    pothole = "pothole"
    open_manhole = "open_manhole"
    damaged_lights = "damaged_lights"

class Detection(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    bbox: list[float] = Field(min_length=4, max_length=4)

class DetectResponse(BaseModel):
    report_id: str
    image_width: int
    image_height: int
    detections: list[Detection]
    counts: dict[str, int]
    severity: str
    demo_mode: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    annotated_image_url: Optional[str] = None
