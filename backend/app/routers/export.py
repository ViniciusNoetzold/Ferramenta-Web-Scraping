import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ExportRequest, ExportResponse
from app.models.db_models import Analysis
from app.database import get_session
import os
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{analysis_id}", response_model=ExportResponse)
async def create_export(analysis_id: str, request: ExportRequest, session: AsyncSession = Depends(get_session)):
    """Export analysis result to a specific format."""
    analysis = await session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    filename = f"export_{analysis_id}.{request.format}"
    
    from app.services.exporter import ExportService
    exporter = ExportService()
    
    data = {
        "id": analysis.id,
        "url": analysis.url,
        "title": analysis.title,
        "status": analysis.status,
        "metadata": analysis.metadata_json,
        "content": analysis.content_json,
        "images": analysis.images_json,
        "structure": analysis.structure_json,
        "raw_html": analysis.raw_html,
        "clean_html": analysis.clean_html,
        "markdown": analysis.markdown,
        "text_content": analysis.text_content,
        "stats": analysis.stats_json,
        "technologies": analysis.technologies_json,
        "created_at": str(analysis.created_at) if analysis.created_at else None
    }
    
    # Force format to zip regardless of what was requested
    request.format = "zip"
    filename = f"export_{analysis_id}.zip"
    filepath = exporter.export_zip(data, settings.OUTPUT_DIR, filename)
        
    return ExportResponse(
        download_url=f"/api/export/download/{filename}",
        filename=filename,
        format="zip",
        size=os.path.getsize(filepath) if os.path.exists(filepath) else 0
    )

@router.get("/download/{filename}")
async def download_export(filename: str):
    """Download an exported file."""
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(path=file_path, filename=filename)
