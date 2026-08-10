import logging
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
from app.models.schemas import ScrapeRequest, ScrapeResponse, ProgressEvent, MetadataInfo, ContentNode, ImageInfo, StructureNode, PageStats
from app.models.db_models import Analysis
from app.database import get_session

router = APIRouter()
logger = logging.getLogger(__name__)

async def background_scrape_task(analysis_id: str, url: str, download_images: bool, app_state):
    async for session in get_session():
        try:
            analysis = await session.get(Analysis, analysis_id)
            if not analysis:
                return
            
            analysis.status = "processing"
            await session.commit()
            
            scraper = app_state.scraper
            result = await scraper.scrape(url, download_images=download_images)
            
            analysis = await session.get(Analysis, analysis_id)
            if not analysis:
                return
                
            analysis.metadata_json = result.get("metadata")
            analysis.content_json = result.get("content")
            analysis.images_json = result.get("images")
            analysis.structure_json = result.get("structure")
            analysis.raw_html = result.get("raw_html")
            analysis.clean_html = result.get("clean_html")
            analysis.markdown = result.get("markdown")
            analysis.text_content = result.get("text_content")
            analysis.stats_json = result.get("stats")
            analysis.technologies_json = result.get("technologies")
            
            analysis.status = "complete"
            await session.commit()
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            analysis = await session.get(Analysis, analysis_id)
            if analysis:
                analysis.status = "error"
                analysis.error = str(e)
                await session.commit()
        finally:
            break

@router.post("", response_model=dict)
async def create_scrape(request: ScrapeRequest, req: Request, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """Create a new scrape task."""
    analysis = Analysis(url=request.url, status="pending")
    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)
    
    background_tasks.add_task(background_scrape_task, analysis.id, request.url, request.download_images, req.app.state)
    return {"id": analysis.id, "status": "processing"}

@router.get("/{analysis_id}", response_model=ScrapeResponse)
async def get_scrape(analysis_id: str, session: AsyncSession = Depends(get_session)):
    """Get scrape result by ID."""
    analysis = await session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    return ScrapeResponse(
        id=analysis.id,
        url=analysis.url,
        status=analysis.status,
        metadata=MetadataInfo(**analysis.metadata_json) if analysis.metadata_json else None,
        content=[ContentNode(**c) for c in analysis.content_json] if analysis.content_json else [],
        images=[ImageInfo(**i) for i in analysis.images_json] if analysis.images_json else [],
        structure=StructureNode(**analysis.structure_json) if analysis.structure_json else None,
        raw_html=analysis.raw_html,
        clean_html=analysis.clean_html,
        markdown=analysis.markdown,
        text_content=analysis.text_content,
        stats=PageStats(**analysis.stats_json) if analysis.stats_json else None,
        technologies=analysis.technologies_json if analysis.technologies_json else [],
        created_at=analysis.created_at.isoformat(),
        error=analysis.error
    )

@router.get("/{analysis_id}/progress")
async def scrape_progress(analysis_id: str):
    """SSE endpoint for progress tracking."""
    async def event_generator():
        while True:
            async for session in get_session():
                analysis = await session.get(Analysis, analysis_id)
                if not analysis:
                    yield f"data: {json.dumps({'status': 'error', 'message': 'Not found', 'step': 'error', 'progress': 0.0})}\n\n"
                    return
                    
                event = ProgressEvent(status=analysis.status, progress=1.0 if analysis.status in ['complete', 'error'] else 0.5, message=f"Status is {analysis.status}", step=analysis.status)
                yield f"data: {event.model_dump_json()}\n\n"
                
                if analysis.status in ["complete", "error"]:
                    return
                break
            await asyncio.sleep(1)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/{analysis_id}/ai")
async def ai_enhancement(analysis_id: str, session: AsyncSession = Depends(get_session)):
    """Apply AI enhancement to scrape result."""
    analysis = await session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    # Stub for AI enhancement
    return {"status": "ok"}
