from pydantic import BaseModel
from typing import Optional

class Property(BaseModel):
    name: str
    description: str
    price: float
    latitude: float
    longitude: float
    user_id: str
    image: str
    type: str
    location: str
    size: int
    location_point: str
    location_id: str
    user_data: str

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_id: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] = None
    size: Optional[int] = None
    location_point: Optional[str] = None
    location_id: Optional[str] = None
    user_data: Optional[str] = None