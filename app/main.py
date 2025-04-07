from fastapi import FastAPI
from app.api.itinerary import router as itinerary_router
#from app.api.user import router as user_router

app = FastAPI()

app.include_router(itinerary_router, prefix="/api/itineraries", tags=["itineraries"])
#app.include_router(user_router, prefix="/api/users", tags=["users"])