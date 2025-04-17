from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional
from enum import Enum

class Trip(BaseModel):
    name: str
    description: str
    trip_duration: int
    start_date: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat()  # Ensure date is serialized as 'YYYY-MM-DD'
        }

class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trip_duration: Optional[int] = None
    start_date: Optional[str] = None
    class Config:
        from_attributes = True

class DayBase(BaseModel):
    name: str
    description: str
    trip_id: Optional[str] = None
    day_number: int

    class Config:
        from_attributes = True

class ActivityBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[int] = None  # in minutes
    position: Optional[int] = None
    category: Optional[str] = None  # UUID of category

    class Config:
        from_attributes = True

class ActivityUpdate(ActivityBase):
    id: Optional[str] = None
    day_id: Optional[str] = None

    class Config:
        from_attributes = True

class DayCreate(DayBase):
    activities: Optional[List[ActivityBase]] = []

class DayUpdate(BaseModel):
    name: Optional[str] = None
    day_number: Optional[int] = None
    description: Optional[str] = None
    activities: Optional[List[ActivityUpdate]] = None

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