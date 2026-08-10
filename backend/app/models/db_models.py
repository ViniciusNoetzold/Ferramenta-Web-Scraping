"""SQLAlchemy ORM models for SQLite persistence."""

from sqlalchemy import Column, String, Integer, Text, DateTime, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON
from datetime import datetime, timezone
import uuid


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    """Stores a complete page-scrape result."""

    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=_uuid)
    url = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | processing | complete | error
    metadata_json = Column(JSON, nullable=True)
    content_json = Column(JSON, nullable=True)
    images_json = Column(JSON, nullable=True)
    structure_json = Column(JSON, nullable=True)
    raw_html = Column(Text, nullable=True)
    clean_html = Column(Text, nullable=True)
    markdown = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    stats_json = Column(JSON, nullable=True)
    technologies_json = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


class CrawlJob(Base):
    """Stores a multi-page crawl job."""

    __tablename__ = "crawl_jobs"

    id = Column(String, primary_key=True, default=_uuid)
    base_url = Column(String, nullable=False)
    status = Column(String, default="pending")
    max_depth = Column(Integer, default=3)
    max_pages = Column(Integer, default=50)
    pages_found = Column(Integer, default=0)
    pages_scraped = Column(Integer, default=0)
    pages_json = Column(JSON, nullable=True)
    sitemap_json = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


class ComparisonJob(Base):
    """Stores a two-page comparison result."""

    __tablename__ = "comparisons"

    id = Column(String, primary_key=True, default=_uuid)
    url1 = Column(String, nullable=False)
    url2 = Column(String, nullable=False)
    result_json = Column(JSON, nullable=True)
    similarity_score = Column(Float, nullable=True)
    status = Column(String, default="pending")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)
