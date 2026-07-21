from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from src.metadata.validators import PyObjectId, SismicMagnitude, EventCounter

# Define la estructura establecida para cada registro en Reports
class ReportModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    report_date: datetime
    total_events: EventCounter      
    average_magnitude: SismicMagnitude 
    max_magnitude: SismicMagnitude     
    top_locations: List[str]