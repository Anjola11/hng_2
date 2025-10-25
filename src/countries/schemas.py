from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import uuid

class CountryResponse(BaseModel):
    id: uuid.UUID 
    name: str 
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime

class RefreshMetadataResponse(BaseModel):
    id: int
    last_refreshed_at: datetime
    total_countries: int