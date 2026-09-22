"""Core scraping engine — uses Playwright for full JS rendering."""

import asyncio
from typing import Dict, Any, Optional
import httpx
from playwright.async_api import async_playwright, Playwright, Browser
from app.models.schemas import PageStats
from app.services.parser import parse_content, build_structure_tree, extract_text, to_markdown, to_clean_html
from app.services.metadata_extractor import extract_metadata
from app.services.image_extractor import extract_images, download_images as dl_images
from app.services.robots_checker import RobotsChecker
from app.config import settings
from app.utils.logging_config import get_logger
from bs4 import BeautifulSoup

logger = get_logger(__name__)


class ScraperEngine:
    """Manages Playwright browser lifecycle and orchestrates page scraping."""

    def __init__(self, max_concurrent: int | None = None):
        self.semaphore = asyncio.Semaphore(max_concurrent or settings.MAX_CONCURRENT_SCRAPES)
        self.robots_checker = RobotsChecker()
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    # ── lifecycle ──────────────────────────────────────────────
    async def initialize(self) -> None:
        """Launch Playwright browser (call once at startup)."""
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-first-run",
                    "--no-zygote",
                    "--single-process",
                    "--disable-extensions",
                ]
            )
            logger.info("ScraperEngine initialized — Chromium launched")
        except Exception as e:
            logger.warning(f"ScraperEngine: Playwright browser launch failed or binary missing: {e}")
            self._browser = None

    async def close(self) -> None:
        """Shut down browser and Playwright."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info("ScraperEngine closed")
        except Exception as e:
            logger.warning(f"ScraperEngine close error: {e}")

    # ── main scrape ────────────────────────────────────────────
    async def scrape(self, url: str, download_images: bool = True) -> dict:
        """Orchestrate a full page scrape.

        Returns a dict with keys: metadata, content, images, structure,
        raw_html, clean_html, markdown, text_content, stats, technologies.
        """
        async with self.semaphore:
            # 1. robots.txt check
            if not await self.robots_checker.is_allowed(url):
                raise ValueError(f"URL blocked by robots.txt: {url}")

            # 2. optional crawl-delay
            delay = await self.robots_checker.get_crawl_delay(url)
            if delay > 0:
                await asyncio.sleep(delay)

            # 3. load page
            html = None
            if self._browser:
                try:
                    context = await self._browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 WebArchiverPro/1.0",
                        viewport={"width": 1280, "height": 900},
                    )
                    page = await context.new_page()
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=settings.REQUEST_TIMEOUT * 1000)
                        html = await page.content()
                    finally:
                        await context.close()
                except Exception as exc:
                    logger.warning("Playwright navigation error for %s (%s). Attempting HTTP fallback.", url, exc)
                    html = None

            # Fallback to direct HTTP fetch if Playwright is unavailable or failed
            if not html:
                logger.info("Using HTTP client fallback for %s", url)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 WebArchiverPro/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=float(settings.REQUEST_TIMEOUT)) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    html = resp.text

            # 4. parse
            soup = BeautifulSoup(html, "lxml")

            metadata = extract_metadata(soup, url)
            images = extract_images(soup, url)
            content = parse_content(html, url)
            structure = build_structure_tree(html)
            clean_html = to_clean_html(html)
            markdown = to_markdown(html, url)
            text_content = extract_text(html)

            # 5. download images
            if download_images and settings.DOWNLOAD_IMAGES:
                images = await dl_images(images, settings.OUTPUT_DIR)

            # 6. detect technologies
            technologies = self._detect_technologies(soup)

            # 7. compute stats
            stats = PageStats(
                heading_count=len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
                paragraph_count=len(soup.find_all("p")),
                image_count=len(images),
                link_count=len(soup.find_all("a")),
                table_count=len(soup.find_all("table")),
                list_count=len(soup.find_all(["ul", "ol"])),
                code_block_count=len(soup.find_all("pre")),
                word_count=len(text_content.split()) if text_content else 0,
                char_count=len(text_content) if text_content else 0,
            )

            return {
                "url": url,
                "metadata": metadata.model_dump(),
                "images": [i.model_dump() for i in images],
                "content": [c.model_dump() for c in content],
                "structure": structure.model_dump() if structure else None,
                "raw_html": html,
                "clean_html": clean_html,
                "markdown": markdown,
                "text_content": text_content,
                "stats": stats.model_dump(),
                "technologies": technologies,
            }

    # ── helpers ────────────────────────────────────────────────
    @staticmethod
    def _detect_technologies(soup: BeautifulSoup) -> list[str]:
        """Heuristically detect frameworks / CMS from HTML hints."""
        techs: list[str] = []
        html_str = str(soup)

        checks = {
            "WordPress": ['wp-content', 'wp-includes'],
            "React": ['__next', '_react', 'react-root', 'data-reactroot'],
            "Vue.js": ['__vue', 'data-v-', 'vue-app'],
            "Angular": ['ng-version', 'ng-app'],
            "Next.js": ['__next', '_next/static'],
            "Gatsby": ['___gatsby'],
            "Tailwind CSS": ['tailwindcss', 'tw-'],
            "Bootstrap": ['bootstrap'],
            "jQuery": ['jquery'],
            "Google Analytics": ['google-analytics.com', 'gtag'],
        }
        for tech, markers in checks.items():
            if any(m in html_str for m in markers):
                techs.append(tech)

        gen = soup.find("meta", attrs={"name": "generator"})
        if gen and gen.get("content"):
            techs.append(gen["content"])

        return techs
