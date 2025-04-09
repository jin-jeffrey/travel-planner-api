from fastapi import FastAPI
from app.api.trips import router as trip_router
#from app.api.user import router as user_router

app = FastAPI()

app.include_router(trip_router, prefix="/api/trips", tags=["trips"])
#app.include_router(user_router, prefix="/api/users", tags=["users"])