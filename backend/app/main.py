from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import sys
import asyncio
import logging

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.database import init_db
from app.config import settings
from app.services.scraper import ScraperEngine

from app.routers.scrape import router as scrape_router
from app.routers.compare import router as compare_router
from app.routers.crawl import router as crawl_router
from app.routers.export import router as export_router
from app.routers.history import router as history_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    
    # Initialize output dir
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Initialize ScraperEngine
    app.state.scraper = ScraperEngine()
    await app.state.scraper.initialize()
    
    yield
    
    # Cleanup
    if hasattr(app.state, "scraper"):
        await app.state.scraper.close()

app = FastAPI(
    title='WebArchiver Pro API',
    description='A professional web scraping tool',
    version='1.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=settings.OUTPUT_DIR), name="files")

app.include_router(scrape_router, prefix="/api/scrape", tags=["scrape"])
app.include_router(compare_router, prefix="/api/compare", tags=["compare"])
app.include_router(crawl_router, prefix="/api/crawl", tags=["crawl"])
app.include_router(export_router, prefix="/api/export", tags=["export"])
app.include_router(history_router, prefix="/api/history", tags=["history"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
