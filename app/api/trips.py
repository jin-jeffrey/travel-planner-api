from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.supabase import supabase
from app.models.trip_management import CreateTrip, TripUpdate
from fastapi.responses import JSONResponse, Response
from app.core.auth import access_required
import logging

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs will be shown on the console (stdout)
    ]
)
logger = logging.getLogger(__name__)

@router.get("/{trip_id}")
def get_trip(trip_id: str, _access = Depends(access_required(["VIEWER", "EDITOR", "OWNER"]))):
    try:
        logger.info(f"Retrieving details for trip with ID: {trip_id}")
        # Query Supabase to get the trip based on the trip_id
        response = supabase.table("trips").select("*").eq("id", str(trip_id)).execute()

        # Check if the trip exists
        logger.info(f"Details for trip {trip_id} retrieved: {response}")
        if response.data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response.data[0]
            )
        else:
            raise HTTPException(status_code=404, detail="Trip not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Need to switch off passing user_id here, use tokens from the UI to get the user_id and use that for the insertion
@router.post("/")
def create_trip(trip: CreateTrip):
    try:
        logger.info(f"Creating a new trip: {trip}")
        
        # Insert the trip into the database
        response = supabase.rpc('create_trip_with_user_access', {
            'p_name': trip.name,
            'p_description': trip.description,
            'p_trip_duration': trip.trip_duration,
            'p_start_date': trip.start_date,
            'p_user_id': trip.user_id
        }).execute()
        
        # Check if the insert was successful
        if response.data:
            logger.info("Trip successfully created, data: ", response.data)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"id": response.data}
            )
        else:
            logger.error(f"Failed to create trip. Error: {response.error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Failed to create trip"
            )
    except Exception as e:
        logger.exception("An error occurred while creating the trip.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{trip_id}")
def update_trip(trip_id: str, trip: TripUpdate, _access = Depends(access_required(["EDITOR", "OWNER"]))):
    try:
        # Prepare the updated trip data
        updated_data = trip.dict(exclude_unset=True)  # Only include fields that were updated

        # Query Supabase to update the trip in the database
        response = supabase.table("trips").update(updated_data).eq("id", trip_id).execute()

        # Check if the update was successful
        if response.data:
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{trip_id}")
def delete_trip(trip_id: str, _access = Depends(access_required(["EDITOR", "OWsNER"]))):
    try:
        # Query Supabase to delete the trip from the database
        response = supabase.table("trips").delete().eq("id", trip_id).execute()

        # Check if the deletion was successful (if the response data contains any rows)
        if response.data:
            # Return status 204 No Content if the deletion was successful
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))