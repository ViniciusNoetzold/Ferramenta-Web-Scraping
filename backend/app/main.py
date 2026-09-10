from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
import asyncio
import logging

# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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

STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    
    # Initialize output dir
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Initialize ScraperEngine
    app.state.scraper = ScraperEngine()
    try:
        await app.state.scraper.initialize()
    except Exception as e:
        logger.warning(f"Could not initialize scraper browser engine: {e}")
    
    yield
    
    # Cleanup
    if hasattr(app.state, "scraper"):
        try:
            await app.state.scraper.close()
        except Exception as e:
            logger.warning(f"Error closing scraper: {e}")

app = FastAPI(
    title="WebArchiver Pro by Mezzold Studio",
    description="Ferramenta profissional de Web Scraping & Análise de Conteúdo desenvolvida pela Mezzold Studio",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount scraped files directory
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=settings.OUTPUT_DIR), name="files")

# API Routers
app.include_router(scrape_router, prefix="/api/scrape", tags=["scrape"])
app.include_router(compare_router, prefix="/api/compare", tags=["compare"])
app.include_router(crawl_router, prefix="/api/crawl", tags=["crawl"])
app.include_router(export_router, prefix="/api/export", tags=["export"])
app.include_router(history_router, prefix="/api/history", tags=["history"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint with Mezzold Studio metadata."""
    return {
        "status": "ok",
        "app": "WebArchiver Pro",
        "brand": "Mezzold Studio",
        "website": "https://mezzoldstudio.com.br/"
    }

@app.get("/api/status")
async def app_status():
    """Application status information."""
    return {
        "status": "online",
        "version": "1.0.0",
        "developed_by": "Mezzold Studio",
        "website": "https://mezzoldstudio.com.br/",
        "ai_available": settings.ai_available
    }

# Direct Brand Static Assets
@app.get("/mezzold-logo.png")
async def get_mezzold_logo():
    logo_path = STATIC_DIR / "mezzold-logo.png"
    if logo_path.is_file():
        return FileResponse(str(logo_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/mezzold-emblem.png")
async def get_mezzold_emblem():
    emblem_path = STATIC_DIR / "mezzold-emblem.png"
    if emblem_path.is_file():
        return FileResponse(str(emblem_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Emblem not found")

@app.get("/favicon.ico")
async def get_favicon():
    fav_path = STATIC_DIR / "favicon.ico"
    if fav_path.is_file():
        return FileResponse(str(fav_path), media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")

# Serve Next.js static files if built
if (STATIC_DIR / "_next").exists():
    app.mount("/_next", StaticFiles(directory=str(STATIC_DIR / "_next")), name="next_static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve Next.js exported static frontend."""
    if full_path.startswith("api/") or full_path.startswith("files/"):
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))
    
    # Try .html extension (e.g. /crawl -> /crawl.html)
    html_file = STATIC_DIR / f"{full_path}.html"
    if html_file.is_file():
        return FileResponse(str(html_file))
    
    # Try directory index.html
    dir_index = file_path / "index.html"
    if dir_index.is_file():
        return FileResponse(str(dir_index))
    
    # Fallback to root index.html
    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    
    return JSONResponse(
        status_code=200,
        content={"message": "WebArchiver Pro API by Mezzold Studio is running.", "docs": "/docs"}
    )
