import httpx
from urllib.parse import urlparse
from robotexclusionrulesparser import RobotExclusionRulesParser
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class RobotsChecker:
    def __init__(self):
        self._cache = {}

    async def _get_parser(self, url: str) -> RobotExclusionRulesParser:
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if domain in self._cache:
            return self._cache[domain]
            
        robots_url = f"{domain}/robots.txt"
        parser = RobotExclusionRulesParser()
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(robots_url, timeout=5.0)
                if response.status_code == 200:
                    parser.parse(response.text)
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt from {robots_url}: {e}")
            
        self._cache[domain] = parser
        return parser

    async def is_allowed(self, url: str, user_agent: str = 'WebArchiverPro') -> bool:
        parser = await self._get_parser(url)
        return parser.is_allowed(user_agent, url)

    async def get_crawl_delay(self, url: str, user_agent: str = 'WebArchiverPro') -> float:
        parser = await self._get_parser(url)
        delay = parser.get_crawl_delay(user_agent)
        return float(delay) if delay else 0.0
