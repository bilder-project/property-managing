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

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_id: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    size: Optional[int] = None