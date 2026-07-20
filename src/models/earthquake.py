from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.metadata.validators import PyObjectId, SismicMagnitude

class EarthquakeModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    event_id: str = Field(..., min_length=5)
    magnitude: SismicMagnitude  
    location: str = Field(..., min_length=1)
    event_time: datetime