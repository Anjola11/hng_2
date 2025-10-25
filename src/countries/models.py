from sqlmodel import SQLModel, Field, Column
import uuid
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy.dialects.postgresql as pg

def utc_now():
    return datetime.now(timezone.utc)

class Country(SQLModel, table=True):
    __tablename__ = "countries"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,  
        primary_key=True  
    )
    
    name: str = Field(index=True, unique=True)
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )

class RefreshMetadata(SQLModel, table=True):
    __tablename__ = "refresh_metadata"
    id: int = Field(default=1, primary_key=True)
    last_refreshed_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    total_countries: int