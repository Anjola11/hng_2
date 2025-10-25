from fastapi import APIRouter, Depends, status
from src.countries.services import DbUpdateDataTasks
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import FileResponse
import os

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
