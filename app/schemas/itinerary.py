from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Itinerary(BaseModel):
    name: str = Field(..., title="Itinerary Name", description="The name of the itinerary")
    description: Optional[str] = Field(None, title="Itinerary Description", description="A brief description of the itinerary")
    start_date: date = Field(..., title="Start Date", description="The start date of the itinerary")
    end_date: date = Field(..., title="End Date", description="The end date of the itinerary")

