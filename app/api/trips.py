from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.supabase import supabase
from app.models.trip_management import DayCreate, DayUpdate, Trip, TripUpdate
from fastapi.responses import JSONResponse, Response
from app.core.auth import access_required, validate_user_exists
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_INTERNAL_500_SERVER_ERROR, detail=str(e))


@router.post("/")
def create_trip(trip: Trip, token: dict = Depends(validate_user_exists)):
    try:
        logger.info(f"Creating a new trip: {trip}")
        
        # Insert the trip into the database
        response = supabase.rpc('create_trip_with_user_access', {
            'p_name': trip.name,
            'p_description': trip.description,
            'p_trip_duration': trip.trip_duration,
            'p_start_date': trip.start_date if trip.start_date else None,
            'p_user_id': token.get("sub")
        }).execute()
        
        # Check if the insert was successful
        if response and response.data:
            logger.info(f"Trip successfully created, trip_id: {response.data}")
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
def delete_trip(trip_id: str, _access = Depends(access_required(["EDITOR", "OWNER"]))):
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
    

@router.post("/{trip_id}/days")
def create_day(trip_id: str, day: DayCreate, _access=Depends(access_required(["EDITOR", "OWNER"]))):
    try:
        logger.info(f"Creating day for trip {trip_id}")
        response = supabase.table("days").insert({
            "trip_id": trip_id,
            "name": day.name,
            "description": day.description,
            "day_number": day.day_number,
        }).execute()

        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create day")

        day_id = response.data[0]["id"]

        # Insert activities if they exist
        if day.activities:
            activity_data = [
                {**a.dict(), "day_id": day_id} for a in day.activities
            ]
            supabase.table("activities").insert(activity_data).execute()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": day_id})

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{trip_id}/days")
def get_days(trip_id: str, _access=Depends(access_required(["VIEWER", "EDITOR", "OWNER"]))):
    try:
        days = supabase.table("days").select("*").eq("trip_id", trip_id).order("day_number").execute().data
        return JSONResponse(status_code=status.HTTP_200_OK, content=days)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@router.delete("/{trip_id}/days/{day_id}")
def delete_day(trip_id: str, day_id: str, _access=Depends(access_required(["EDITOR", "OWNER"]))):
    try:
        # Check if the day exists
        supabase.table("days").delete().eq("id", day_id).eq("trip_id", trip_id).execute()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{trip_id}/days/{day_id}")
def update_day(trip_id: str, day_id: str, day: DayUpdate, _access=Depends(access_required(["EDITOR", "OWNER"]))):
    try:
        # Update day fields if any provided
        if any([day.name, day.day_number, day.description]):
            day_fields = day.dict(exclude_unset=True, exclude={"activities"})
            supabase.table("days").update(day_fields).eq("id", day_id).eq("trip_id", trip_id).execute()

        # Handle activity updates if provided
        if day.activities is not None:
            current = supabase.table("activities").select("id").eq("day_id", day_id).execute().data
            current_ids = {a["id"] for a in current}
            updates = {a.id: a for a in day.activities if a.id}
            incoming_ids = set(updates.keys())

            # Delete removed activities
            to_delete = current_ids - incoming_ids
            if to_delete:
                supabase.table("activities").delete().in_("id", list(to_delete)).execute()

            # Update existing activities
            for act_id in current_ids & incoming_ids:
                act = updates[act_id]
                supabase.table("activities").update(act.dict(exclude={"id"})).eq("id", act_id).execute()

            # Insert new activities
            new_acts = [a.dict() for a in day.activities if not a.id]
            for act in new_acts:
                act["day_id"] = day_id
            if new_acts:
                supabase.table("activities").insert(new_acts).execute()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
