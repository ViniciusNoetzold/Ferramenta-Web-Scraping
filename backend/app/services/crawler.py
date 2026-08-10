import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Set, List
from urllib.parse import urlparse
from app.models.schemas import CrawlPageInfo, SitemapNode
from app.services.robots_checker import RobotsChecker
from app.utils.url_utils import same_domain, make_absolute, is_valid_url
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class SiteCrawler:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.robots_checker = RobotsChecker()
        self.visited: Set[str] = set()
        self.pages: List[CrawlPageInfo] = []
        
    async def fetch_page(self, url: str, depth: int, base_url: str):
        if url in self.visited or not is_valid_url(url) or not same_domain(url, base_url):
            return []
            
        self.visited.add(url)
        
        if not await self.robots_checker.is_allowed(url):
            return []
            
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(url, timeout=10.0)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "lxml")
                        title = soup.title.string.strip() if soup.title else None
                        
                        self.pages.append(CrawlPageInfo(
                            url=url,
                            title=title,
                            depth=depth,
                            status="complete"
                        ))
                        
                        links = []
                        for a in soup.find_all("a", href=True):
                            href = a["href"]
                            abs_url = make_absolute(href, url)
                            if same_domain(abs_url, base_url) and abs_url not in self.visited:
                                links.append(abs_url)
                        return links
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                self.pages.append(CrawlPageInfo(
                    url=url,
                    title=None,
                    depth=depth,
                    status="error"
                ))
        return []

    async def crawl(self, base_url: str, max_depth: int, max_pages: int) -> dict:
        self.visited.clear()
        self.pages.clear()
        
        queue = [(base_url, 0)]
        sitemap = SitemapNode(url=base_url)
        node_map = {base_url: sitemap}
        
        while queue and len(self.visited) < max_pages:
            url, depth = queue.pop(0)
            
            if depth > max_depth:
                continue
                
            current_node = node_map.get(url)
                
            new_links = await self.fetch_page(url, depth, base_url)
            
            for link in new_links:
                if link not in self.visited:
                    queue.append((link, depth + 1))
                    if link not in node_map:
                        new_node = SitemapNode(url=link)
                        node_map[link] = new_node
                        if current_node:
                            current_node.children.append(new_node)
                    
        return {
            "base_url": base_url,
            "pages_found": len(self.pages),
            "pages_scraped": len([p for p in self.pages if p.status == "complete"]),
            "pages": [p.model_dump() for p in self.pages],
            "sitemap": sitemap.model_dump()
        }
