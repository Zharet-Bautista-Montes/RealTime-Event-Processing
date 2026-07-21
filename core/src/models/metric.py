from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field
from src.metadata.validators import SismicMagnitude, EventCounter

# Define la estructura establecida para cada registro en Metrics
class MetricModel(BaseModel):
    id: str = Field(..., alias="_id")
    window: datetime
    earthquake_count: EventCounter  
    avg_magnitude: SismicMagnitude  
    max_magnitude: SismicMagnitude  
    magnitude_distribution: Dict[str, EventCounter] = Field(
        default_factory=dict,
        description="Frecuencia de sismos agrupados por rangos de magnitud de 1.0 unidad"
    )