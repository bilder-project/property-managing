from fastapi import FastAPI, HTTPException, Depends
from supabase import create_client, Client
from models import Property, PropertyUpdate
import os
from dotenv import load_dotenv 
from auth_handler import verify_jwt_token

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Replace these with your actual Supabase URL and API key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@app.get("/")
async def root():
    return {"Hello": "World"}

# Create new property
@app.post("/properties", dependencies=[Depends(verify_jwt_token)])
async def create_property(property: Property):
    try:
        response = (
            supabase.table("properties")
            .insert(property.dict())
            .execute()
        )

        return {"Property added successfully: ": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get property with ID
@app.get("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def get_property(property_id: str):
    try:
        response = (
            supabase.table("properties")
            .select("*")
            .eq("id", property_id)
            .execute()
        )

        if (response.data == []):
            raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all properties
@app.get("/properties", dependencies=[Depends(verify_jwt_token)])
async def get_properties():
    try:
        response = (
            supabase.table("properties")
            .select("*")
            .execute()
        )

        if (response.data == []):
            raise HTTPException(status_code=404, detail=str("No properties found."))

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Get all properties of a user with ID
@app.get("/properties/user/{user_id}", dependencies=[Depends(verify_jwt_token)])
async def get_properties_of_user(user_id: str):
    try:
        response = (
            supabase.table("properties")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if (response.data == []):
            raise HTTPException(status_code=404, detail=str("No properties found for requested user."))

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete property with ID
@app.delete("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def delete_property(property_id: str):
    try:
        response = (
            supabase.table("properties")
            .delete()
            .eq("id", property_id)
            .execute()
        )

        if (response.data == []):
            raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Update property with ID
@app.put("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def update_property(property_id: str, property: PropertyUpdate):
    try:
        update_data = property.dict(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update.")
        
        response = (
            supabase.table("properties")
            .update(update_data)
            .eq("id", property_id)
            .execute()
        )

        if (response.data == []):
            raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

        return {"Property updated successfully: ": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))