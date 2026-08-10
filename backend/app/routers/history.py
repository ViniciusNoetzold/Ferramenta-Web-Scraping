import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.models.schemas import HistoryItem
from app.models.db_models import Analysis, ComparisonJob, CrawlJob
from app.database import get_session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[HistoryItem])
async def list_history(session: AsyncSession = Depends(get_session)):
    """List all Analysis records."""
    stmt = select(Analysis).order_by(Analysis.created_at.desc())
    result = await session.execute(stmt)
    analyses = result.scalars().all()
    
    return [
        HistoryItem(
            id=a.id,
            url=a.url,
            title=a.title or "",
            status=a.status,
            created_at=a.created_at.isoformat(),
            image_count=len(a.images_json) if a.images_json else 0,
            word_count=a.stats_json.get("word_count", 0) if a.stats_json else 0
        ) for a in analyses
    ]

@router.delete("/{analysis_id}")
async def delete_history(analysis_id: str, session: AsyncSession = Depends(get_session)):
    """Delete an Analysis record."""
    analysis = await session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    await session.delete(analysis)
    await session.commit()
    return {"status": "ok"}

@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)):
    """Get total counts."""
    analysis_count = (await session.execute(select(func.count(Analysis.id)))).scalar_one()
    comparison_count = (await session.execute(select(func.count(ComparisonJob.id)))).scalar_one()
    crawl_count = (await session.execute(select(func.count(CrawlJob.id)))).scalar_one()
    
    return {
        "analyses": analysis_count,
        "comparisons": comparison_count,
        "crawls": crawl_count
    }
