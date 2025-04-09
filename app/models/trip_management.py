from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional
from enum import Enum

class Trip(BaseModel):
    name: str
    description: str
    trip_duration: int
    start_date: Optional[str]

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()  # Ensure date is serialized as 'YYYY-MM-DD'
        }

# Will be deleted when the user_id is passed via token
class CreateTrip(Trip):
    user_id: str

    class Config:
        from_attributes = True

class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trip_duration: Optional[int] = None
    start_date: Optional[str] = None
    class Config:
        from_attributes = True

class Day(BaseModel):
    name: str
    description: str
    trip_id: str
    day_number: int

    class Config:
        from_attributes = True

class Activity(BaseModel):
    name: str
    location: str
    description: str
    position: int
    start_time: time
    duration: int
    category: str
    day_id: str

    class Config:
        from_attributes = True

class TripsToCategories(BaseModel):
    trip_id: str
    category_id: str

    class Config:
        from_attributes = True

class CategoryType(Enum):
    PREDEFINED = "PREDEFINED"
    CUSTOM = "CUSTOM"

class Categories(BaseModel):
    name: str
    type: CategoryType

    class Config:
        from_attributes = True