from fastapi import APIRouter, Depends, status, HTTPException
from src.countries.services import DbUpdateDataTasks
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import FileResponse
import os
from typing import Optional, List
from src.countries.schemas import CountryResponse, RefreshMetadataResponse

router = APIRouter()
db_tasks = DbUpdateDataTasks()

@router.post('/refresh', status_code= status.HTTP_200_OK)
async def add_countries(session: AsyncSession = Depends(get_session)):
    add_countries = await db_tasks.add_countries(session)

    return add_countries

@router.get('/image')
async def get_summary_image():
    """Serve the generated summary image"""
    image_path = 'cache/summary.png'
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )
    
    return FileResponse(image_path, media_type='image/png')

@router.get("", response_model= List[CountryResponse])
@router.get("/", response_model= List[CountryResponse])
async def get_all_countries(
    region: Optional[str] = None,
    currency: Optional[str] = None,
    sort: Optional[str] = None,
    session: AsyncSession = Depends(get_session)):

    countries = await db_tasks.get_all_countries(region, currency, sort, session)

    return countries


@router.get("/status", response_model = RefreshMetadataResponse, status_code=status.HTTP_200_OK)
async def get_refresh_status(session: AsyncSession = Depends(get_session)):
    refresh_status = await db_tasks.get_refresh_status(session)

    return refresh_status

@router.get("/{country}", status_code= status.HTTP_200_OK, response_model=CountryResponse)
async def get_country_by_name(country_name: str,session: AsyncSession = Depends(get_session)):
    country = await db_tasks.get_country_by_name(country_name, session)

    return country

@router.delete("/{country}", status_code= status.HTTP_200_OK)
async def delete_country(country_name: str,session: AsyncSession = Depends(get_session)):
    deleted_country = await db_tasks.delete_country_by_name(country_name, session)

    return deleted_country