from fastapi import APIRouter

router = APIRouter()

@router.get("/{itinerary_id}")
def get_itinerary():
    return {"message": "List of itineraries"}

@router.post("/")
def create_itinerary():
    return {"message": "List of itineraries"}

@router.patch("/{itinerary_id}")
def update_itinerary():
    return {"message": "List of itineraries"}

@router.delete("/{itinerary_id}")
def delete_itinerary(): 
    return {"message": "List of itineraries"}