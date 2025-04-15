import jwt
import os
from fastapi import HTTPException, Depends, Header, status, Path
from app.supabase import supabase
from dotenv import load_dotenv

load_dotenv()


def validate_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization token is required")
    
    try:
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]
        JWT_KEY = os.getenv("JWT_KEY")
        if not JWT_KEY:
            raise RuntimeError("JWT_KEY not set in environment")
        decoded_token = jwt.decode(token, JWT_KEY, algorithms=["HS256"], audience="authenticated", options={"verify_exp": False})

        return decoded_token

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


def has_access(token: dict, roles: list, trip_id: str = None) -> bool:
    """
    Check if the user has one of the specified roles.
    
    Args:
        token: The decoded JWT token containing the user information.
        roles: A list of roles that are allowed to access the resource.
        db: Database session for querying the user access table.

    Returns:
        bool: True if the user has access, False otherwise.
    """
    user_id = token.get("sub")  # Assuming the token contains the user_id
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found in the token")
    
    # Query the database to find the user's roles
    query = supabase.table("user_access").select("access_type").eq("user_id", str(user_id))

    if trip_id:
        query = query.eq("trip_id", trip_id)

    response = query.execute()

    if not response.data:
        return False

    access_type = response.data[0].get("access_type")
    return access_type in roles


def access_required(roles: list):
    def validator(token: dict = Depends(validate_token), trip_id: str = Path(...)):
        if not has_access(token, roles, trip_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Insufficient role")
        return True
    return validator

def validate_user_exists(token: dict = Depends(validate_token)):
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found in token")

    response = supabase.table("profiles").select("*").eq("user_id", str(user_id)).execute()

    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or unauthorized to create trips")

    return token