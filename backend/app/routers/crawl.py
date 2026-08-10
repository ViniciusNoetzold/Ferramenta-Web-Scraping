import logging
import asyncio
import json
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import CrawlRequest, CrawlResponse, ProgressEvent, CrawlPageInfo, SitemapNode
from app.models.db_models import CrawlJob
from app.database import get_session

router = APIRouter()
logger = logging.getLogger(__name__)

from app.services.crawler import SiteCrawler

async def background_crawl_task(crawl_id: str, base_url: str, max_depth: int, max_pages: int):
    try:
        async for session in get_session():
            job = await session.get(CrawlJob, crawl_id)
            if job:
                job.status = "processing"
                await session.commit()
            break
            
        crawler = SiteCrawler()
        result = await crawler.crawl(base_url, max_depth, max_pages)
        
        async for session in get_session():
            job = await session.get(CrawlJob, crawl_id)
            if job:
                job.pages_found = result["pages_found"]
                job.pages_scraped = result["pages_scraped"]
                job.pages_json = result["pages"]
                job.sitemap_json = result["sitemap"]
                job.status = "complete"
                await session.commit()
            break
    except Exception as e:
        logger.error(f"Error in crawl task: {e}")
        async for session in get_session():
            job = await session.get(CrawlJob, crawl_id)
            if job:
                job.status = "error"
                job.error = str(e)
                await session.commit()
            break

@router.post("", response_model=dict)
async def create_crawl(request: CrawlRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """Create a new crawl job."""
    job = CrawlJob(base_url=request.base_url, max_depth=request.max_depth, max_pages=request.max_pages, status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    background_tasks.add_task(background_crawl_task, job.id, request.base_url, request.max_depth, request.max_pages)
    return {"id": job.id, "status": "processing"}

@router.get("/{crawl_id}", response_model=CrawlResponse)
async def get_crawl(crawl_id: str, session: AsyncSession = Depends(get_session)):
    """Get crawl result by ID."""
    job = await session.get(CrawlJob, crawl_id)
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    
    return CrawlResponse(
        id=job.id,
        base_url=job.base_url,
        status=job.status,
        pages_found=job.pages_found,
        pages_scraped=job.pages_scraped,
        pages=[CrawlPageInfo(**p) for p in job.pages_json] if job.pages_json else [],
        sitemap=SitemapNode(**job.sitemap_json) if job.sitemap_json else None,
        created_at=job.created_at.isoformat(),
        error=job.error
    )

@router.get("/{crawl_id}/progress")
async def crawl_progress(crawl_id: str):
    """SSE endpoint for crawl progress tracking."""
    async def event_generator():
        while True:
            async for session in get_session():
                job = await session.get(CrawlJob, crawl_id)
                if not job:
                    yield f"data: {json.dumps({'status': 'error', 'message': 'Not found', 'step': 'error', 'progress': 0.0})}\n\n"
                    return
                
                event = ProgressEvent(status=job.status, progress=1.0 if job.status in ['complete', 'error'] else 0.5, message=f"Status is {job.status}", step=job.status)
                yield f"data: {event.model_dump_json()}\n\n"
                
                if job.status in ["complete", "error"]:
                    return
                break
            await asyncio.sleep(1)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
