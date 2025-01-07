# from fastapi import FastAPI, HTTPException, Depends
# from models import Property, PropertyUpdate
# from auth_handler import verify_jwt_token, get_supabase_client_with_jwt

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"Hello": "World"}

# # Create new property
# @app.post("/properties", dependencies=[Depends(verify_jwt_token)])
# async def create_property(property: Property, jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         response = (
#             supabase.table("properties")
#             .insert(property.dict())
#             .execute()
#         )

#         return {"Property added successfully: ": response}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # Get property with ID
# @app.get("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
# async def get_property(property_id: str, jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         response = (
#             supabase.table("properties")
#             .select("*")
#             .eq("id", property_id)
#             .execute()
#         )

#         if (response.data == []):
#             raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # Get all properties
# @app.get("/properties", dependencies=[Depends(verify_jwt_token)])
# async def get_properties(jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         response = (
#             supabase.table("properties")
#             .select("*")
#             .execute()
#         )

#         if (response.data == []):
#             raise HTTPException(status_code=404, detail=str("No properties found."))

#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# # Get all properties of a user with ID
# @app.get("/properties/user/{user_id}", dependencies=[Depends(verify_jwt_token)])
# async def get_properties_of_user(user_id: str, jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         response = (
#             supabase.table("properties")
#             .select("*")
#             .eq("user_id", user_id)
#             .execute()
#         )

#         if (response.data == []):
#             raise HTTPException(status_code=404, detail=str("No properties found for requested user."))

#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # Delete property with ID
# @app.delete("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
# async def delete_property(property_id: str, jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         response = (
#             supabase.table("properties")
#             .delete()
#             .eq("id", property_id)
#             .execute()
#         )

#         if (response.data == []):
#             raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

#         return response
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# # Update property with ID
# @app.put("/properties/{property_id}", dependencies=[Depends(verify_jwt_token)])
# async def update_property(property_id: str, property: PropertyUpdate, jwt_token: str = Depends(verify_jwt_token)):
#     try:
#         supabase = get_supabase_client_with_jwt(jwt_token)

#         update_data = property.dict(exclude_unset=True)

#         if not update_data:
#             raise HTTPException(status_code=400, detail="No fields provided for update.")
        
#         response = (
#             supabase.table("properties")
#             .update(update_data)
#             .eq("id", property_id)
#             .execute()
#         )

#         if (response.data == []):
#             raise HTTPException(status_code=404, detail=str("No properties found with ID {property_id}."))

#         return {"Property updated successfully: ": response}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))



import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.routing import APIRoute
from models import Property, PropertyUpdate
from auth_handler import verify_jwt_token, get_supabase_client_with_jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
PROPERTY_MANAGING_SERVER_PORT = os.getenv("PROPERTY_MANAGING_SERVER_PORT", "8080")
PROPERTY_MANAGING_SERVER_MODE = os.getenv("PROPERTY_MANAGING_SERVER_MODE", "development")
PROPERTY_MANAGING_PREFIX = f"/property-managing" if PROPERTY_MANAGING_SERVER_MODE == "production" else ""

# Initialize the FastAPI app
app = FastAPI()

# Add prefix to all routes dynamically
def add_prefix_to_routes(app: FastAPI, prefix: str):
    """Add a prefix to all API routes."""
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.path = f"{prefix}{route.path}"


# Define API routes
@app.get(f"${PROPERTY_MANAGING_PREFIX}")
async def root():
    return {"Hello": "World"}

# Create new property
@app.post(f"${PROPERTY_MANAGING_PREFIX}", dependencies=[Depends(verify_jwt_token)])
async def create_property(property: Property, jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        response = (
            supabase.table("properties")
            .insert(property.dict())
            .execute()
        )

        return {"Property added successfully: ": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get property with ID
@app.get(f"${PROPERTY_MANAGING_PREFIX}"+"/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def get_property(property_id: str, jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        response = (
            supabase.table("properties")
            .select("*")
            .eq("id", property_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail=f"No properties found with ID {property_id}.")

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all properties
@app.get(f"${PROPERTY_MANAGING_PREFIX}", dependencies=[Depends(verify_jwt_token)])
async def get_properties(jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        response = (
            supabase.table("properties")
            .select("*")
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No properties found.")

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get all properties of a user with ID
@app.get(f"${PROPERTY_MANAGING_PREFIX}"+"/user/{user_id}", dependencies=[Depends(verify_jwt_token)])
async def get_properties_of_user(user_id: str, jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        response = (
            supabase.table("properties")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No properties found for requested user.")

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete property with ID
@app.delete(f"${PROPERTY_MANAGING_PREFIX}"+"/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def delete_property(property_id: str, jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        response = (
            supabase.table("properties")
            .delete()
            .eq("id", property_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail=f"No properties found with ID {property_id}.")

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update property with ID
@app.put(f"${PROPERTY_MANAGING_PREFIX}"+"/{property_id}", dependencies=[Depends(verify_jwt_token)])
async def update_property(property_id: str, property: PropertyUpdate, jwt_token: str = Depends(verify_jwt_token)):
    try:
        supabase = get_supabase_client_with_jwt(jwt_token)

        update_data = property.dict(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update.")
        
        response = (
            supabase.table("properties")
            .update(update_data)
            .eq("id", property_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail=f"No properties found with ID {property_id}.")

        return {"Property updated successfully: ": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add a health check route
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Add prefix to all routes
# add_prefix_to_routes(app, PROPERTY_MANAGING_PREFIX)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PROPERTY_MANAGING_SERVER_PORT))
