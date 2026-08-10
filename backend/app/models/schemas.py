"""Pydantic schemas — shared API contract between routers, services, and frontend."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════

class ScrapeRequest(BaseModel):
    url: str
    download_images: bool = True
    use_ai: bool = False


class CompareRequest(BaseModel):
    url1: str
    url2: str


class CrawlRequest(BaseModel):
    base_url: str
    max_depth: int = Field(default=3, ge=1, le=10)
    max_pages: int = Field(default=50, ge=1, le=500)


class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(markdown|json|html|pdf|zip)$")


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class MetadataInfo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    favicon: Optional[str] = None
    canonical_url: Optional[str] = None
    language: Optional[str] = None
    og_tags: dict = Field(default_factory=dict)
    twitter_tags: dict = Field(default_factory=dict)
    schema_org: Optional[dict] = None


class ContentNode(BaseModel):
    """Represents a semantic block in the page (heading, paragraph, list, etc.)."""
    tag: str
    text: Optional[str] = None
    children: list[ContentNode] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)


ContentNode.model_rebuild()


class ImageInfo(BaseModel):
    url: str
    absolute_url: str
    filename: str
    alt_text: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    section: Optional[str] = None
    position: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    local_path: Optional[str] = None
    ai_description: Optional[str] = None


class StructureNode(BaseModel):
    """DOM-tree node for structure visualization."""
    tag: str
    id: Optional[str] = None
    classes: list[str] = Field(default_factory=list)
    text_preview: Optional[str] = None
    children: list[StructureNode] = Field(default_factory=list)


StructureNode.model_rebuild()


class PageStats(BaseModel):
    heading_count: int = 0
    paragraph_count: int = 0
    image_count: int = 0
    link_count: int = 0
    table_count: int = 0
    list_count: int = 0
    code_block_count: int = 0
    word_count: int = 0
    char_count: int = 0


# ═══════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class ScrapeResponse(BaseModel):
    id: str
    url: str
    status: str  # pending | processing | complete | error
    metadata: Optional[MetadataInfo] = None
    content: list[ContentNode] = Field(default_factory=list)
    images: list[ImageInfo] = Field(default_factory=list)
    structure: Optional[StructureNode] = None
    raw_html: Optional[str] = None
    clean_html: Optional[str] = None
    markdown: Optional[str] = None
    text_content: Optional[str] = None
    stats: Optional[PageStats] = None
    technologies: list[str] = Field(default_factory=list)
    created_at: str
    error: Optional[str] = None


class TextDiff(BaseModel):
    type: str  # add | remove | equal
    text: str
    section: Optional[str] = None


class StructureDiff(BaseModel):
    type: str  # added | removed | changed
    element: str
    details: Optional[str] = None


class CompareResponse(BaseModel):
    id: str
    url1: str
    url2: str
    status: str
    text_diffs: list[TextDiff] = Field(default_factory=list)
    structure_diffs: list[StructureDiff] = Field(default_factory=list)
    images_added: list[ImageInfo] = Field(default_factory=list)
    images_removed: list[ImageInfo] = Field(default_factory=list)
    similarity_score: float = 0.0
    created_at: str
    error: Optional[str] = None


class CrawlPageInfo(BaseModel):
    url: str
    title: Optional[str] = None
    depth: int = 0
    status: str = "pending"


class SitemapNode(BaseModel):
    url: str
    title: Optional[str] = None
    children: list[SitemapNode] = Field(default_factory=list)


SitemapNode.model_rebuild()


class CrawlResponse(BaseModel):
    id: str
    base_url: str
    status: str  # pending | processing | complete | error
    pages_found: int = 0
    pages_scraped: int = 0
    pages: list[CrawlPageInfo] = Field(default_factory=list)
    sitemap: Optional[SitemapNode] = None
    created_at: str
    error: Optional[str] = None


class HistoryItem(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    status: str
    created_at: str
    image_count: int = 0
    word_count: int = 0


class ExportResponse(BaseModel):
    download_url: str
    filename: str
    format: str
    size: int = 0


class ProgressEvent(BaseModel):
    """Server-Sent Event payload for progress tracking."""
    status: str
    progress: float = 0.0  # 0.0 → 1.0
    message: str
    step: str  # validating | loading | parsing | images | ai | saving
