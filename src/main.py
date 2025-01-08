import os
import pybreaker
import requests
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from src.models import Property, PropertyUpdate
from src.auth_handler import get_supabase_client
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read environment variables
PROPERTY_MANAGING_SERVER_PORT = os.getenv("PROPERTY_MANAGING_SERVER_PORT", "8080")
PROPERTY_MANAGING_SERVER_MODE = os.getenv(
    "PROPERTY_MANAGING_SERVER_MODE", "development"
)
PROPERTY_MANAGING_PREFIX = (
    f"/property-managing" if PROPERTY_MANAGING_SERVER_MODE == "release" else ""
)

# Initialize the FastAPI app
app = FastAPI(
    title="Property Managing API",
    description="API for managing properties",
    version="1.0.0",
    openapi_url=f"{PROPERTY_MANAGING_PREFIX}/openapi.json",
    docs_url=f"{PROPERTY_MANAGING_PREFIX}/docs",
    redoc_url=f"{PROPERTY_MANAGING_PREFIX}/redoc",
)

PLACES_BASE_URL = os.getenv("PLACES_BASE_URL")
USERS_BASE_URL = os.getenv("USERS_BASE_URL")

# Circuit Breaker
breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)


# Retry Configuration
def is_transient_error(exception):
    """Define what qualifies as a transient error."""
    return isinstance(exception, requests.exceptions.RequestException)


retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)


# Helper function with Circuit Breaker for creating property data
@retry_strategy
@breaker
def create_property_in_supabase(property: Property):
    supabase = get_supabase_client()
    response = supabase.table("properties").insert(property.dict()).execute()
    return response


# Create new property
@app.post(f"{PROPERTY_MANAGING_PREFIX}/properties")
async def create_property(property: Property):
    try:
        data = create_property_in_supabase(property)
        return {"Property added successfully: ": data}
    except RetryError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )
    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function with Circuit Breaker for getting data by ID
@retry_strategy
@breaker
def get_property_from_supabase(property_id: str):
    supabase = get_supabase_client()
    response = supabase.table("properties").select("*").eq("id", property_id).execute()

    user_id = response.data[0]["user_id"]
    user_data = requests.get(f"https://oblak.sagaj.si/user-managing/users/{user_id}").json()

    response.data[0]["user_data"] = user_data

    return response


# Get property with ID
@app.get(f"{PROPERTY_MANAGING_PREFIX}" + "/properties/{property_id}")
async def get_property(property_id: str):
    try:
        response = get_property_from_supabase(property_id)
        return response.data[0]

    except RetryError as retry_error:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )
    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function with Circuit Breaker for getting data
@retry_strategy
@breaker
def get_properties_from_supabase(count: int):
    supabase = get_supabase_client()

    if count == 0:
        response = supabase.table("properties").select("*").execute()
    else:
        response = supabase.table("properties").select("*").limit(count).execute()

    return response


# Get all properties
@app.get(f"{PROPERTY_MANAGING_PREFIX}/properties")
# Make count not required
async def get_properties(count: int = 0):
    try:
        data = get_properties_from_supabase(count)
        return data

    except RetryError as retry_error:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )

    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function with Circuit Breaker for getting data of user
@retry_strategy
@breaker
def get_properties_from_user_from_supabase(user_id: str):
    supabase = get_supabase_client()

    response = supabase.table("properties").select("*").eq("user_id", user_id).execute()

    return response


# Get all properties of a user with ID
@app.get(f"{PROPERTY_MANAGING_PREFIX}" + "/properties/user/{user_id}")
async def get_properties_of_user(user_id: str):
    try:
        data = get_properties_from_user_from_supabase(user_id)
        return data

    except RetryError as retry_error:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )

    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function with Circuit Breaker for deleting data
@retry_strategy
@breaker
def delete_property_from_supabase(property_id: str):
    supabase = get_supabase_client()

    response = supabase.table("properties").delete().eq("id", property_id).execute()

    return response


# Delete property with ID
@app.delete(f"{PROPERTY_MANAGING_PREFIX}" + "/properties/{property_id}")
async def delete_property(property_id: str):
    try:
        data = delete_property_from_supabase(property_id)
        return [{"Property deleted successfully: ": data}]

    except RetryError as retry_error:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )

    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function with Circuit Breaker for updating data
@retry_strategy
@breaker
def update_property_in_supabase(property_id: str, property: PropertyUpdate):
    supabase = get_supabase_client()

    update_data = property.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    response = (
        supabase.table("properties").update(update_data).eq("id", property_id).execute()
    )

    return response


# Update property with ID
@app.put(f"{PROPERTY_MANAGING_PREFIX}" + "/properties/{property_id}")
async def update_property(property_id: str, property: PropertyUpdate):
    try:
        data = update_property_in_supabase(property_id, property)
        return data.data[0]

    except RetryError as retry_error:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable after multiple retry attempts. Please try again later.",
        )

    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to repeated failures.",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health check
@app.get(f"{PROPERTY_MANAGING_PREFIX}/health")
async def health_check():
    return {"status": "ok"}
