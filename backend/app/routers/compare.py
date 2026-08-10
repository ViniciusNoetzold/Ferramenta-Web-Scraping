import logging
import httpx
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import CompareRequest, CompareResponse, TextDiff, StructureDiff, ImageInfo
from app.models.db_models import ComparisonJob
from app.database import get_session
from app.services.comparator import compare_pages

router = APIRouter()
logger = logging.getLogger(__name__)

async def background_compare_task(comparison_id: str, url1: str, url2: str):
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp1 = await client.get(url1)
            resp2 = await client.get(url2)
            html1 = resp1.text
            html2 = resp2.text

        result = compare_pages(html1, html2, url1, url2)
        
        async for session in get_session():
            job = await session.get(ComparisonJob, comparison_id)
            if job:
                job.similarity_score = result["similarity_score"]
                job.result_json = {
                    "text_diffs": result["text_diffs"],
                    "structure_diffs": result["structure_diffs"],
                    "images_added": result["images_added"],
                    "images_removed": result["images_removed"]
                }
                job.status = "complete"
                await session.commit()
            break
    except Exception as e:
        logger.error(f"Error in comparison task: {e}")
        async for session in get_session():
            job = await session.get(ComparisonJob, comparison_id)
            if job:
                job.status = "error"
                job.error = str(e)
                await session.commit()
            break

@router.post("", response_model=dict)
async def create_compare(request: CompareRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """Create a new comparison job."""
    job = ComparisonJob(url1=request.url1, url2=request.url2, status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    background_tasks.add_task(background_compare_task, job.id, request.url1, request.url2)
    return {"id": job.id, "status": "processing"}

@router.get("/{comparison_id}", response_model=CompareResponse)
async def get_compare(comparison_id: str, session: AsyncSession = Depends(get_session)):
    """Get comparison result by ID."""
    job = await session.get(ComparisonJob, comparison_id)
    if not job:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    result = job.result_json or {}
    
    return CompareResponse(
        id=job.id,
        url1=job.url1,
        url2=job.url2,
        status=job.status,
        text_diffs=[TextDiff(**d) for d in result.get("text_diffs", [])],
        structure_diffs=[StructureDiff(**d) for d in result.get("structure_diffs", [])],
        images_added=[ImageInfo(**d) for d in result.get("images_added", [])],
        images_removed=[ImageInfo(**d) for d in result.get("images_removed", [])],
        similarity_score=job.similarity_score or 0.0,
        created_at=job.created_at.isoformat(),
        error=job.error
    )
