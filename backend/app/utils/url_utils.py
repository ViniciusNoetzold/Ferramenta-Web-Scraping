"""URL validation and normalisation helpers."""

from urllib.parse import urlparse, urljoin, urldefrag
import re
import validators


def is_valid_url(url: str) -> bool:
    """Return True if *url* looks like a valid HTTP(S) URL."""
    if not url:
        return False
    result = validators.url(url)
    return result is True


def normalise_url(url: str) -> str:
    """Strip fragment, enforce scheme, lowercase host."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    return parsed._replace(netloc=parsed.netloc.lower()).geturl()


def make_absolute(base_url: str, relative_url: str) -> str:
    """Resolve a possibly-relative URL against *base_url*."""
    if not relative_url:
        return ""
    return urljoin(base_url, relative_url)


def same_domain(url1: str, url2: str) -> bool:
    """Check whether two URLs share the same registered domain."""
    return urlparse(url1).netloc.lower() == urlparse(url2).netloc.lower()


def extract_filename(url: str) -> str:
    """Pull the filename from a URL path, falling back to 'unknown'."""
    path = urlparse(url).path
    name = path.rsplit("/", 1)[-1] if "/" in path else path
    return name or "unknown"


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_length: int = 60) -> str:
    """Create a filesystem-safe slug from arbitrary text."""
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return slug[:max_length]
