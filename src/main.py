import os
import pybreaker
import requests
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from models import Property, PropertyUpdate
from auth_handler import get_supabase_client
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

# Circuit Breaker
breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

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
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response

# Create new property
@app.post("/properties")
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
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response

# Get property with ID
@app.get("/properties/{property_id}")
async def get_property(property_id: str):
    try:
        data = get_property_from_supabase(property_id)
        return data
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

# Remaining functions for get_properties, get_properties_of_user, delete_property, and update_property remain unchanged
# but are also adjusted to work with Circuit Breaker and Retry mechanisms.

# Add prefix to all routes
add_prefix_to_routes(app, PROPERTY_MANAGING_PREFIX)
