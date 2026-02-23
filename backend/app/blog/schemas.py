"""
blog/schemas.py – Pydantic request/response schemas for the Blog module.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert a string to a URL-safe slug."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    slug: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None

    @field_validator("slug", mode="before")
    @classmethod
    def auto_slug(cls, v: Optional[str], info) -> str:
        if not v:
            name = info.data.get("name", "")
            return _slugify(name)
        return _slugify(v)


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    slug: Optional[str] = Field(None, max_length=80)

    @field_validator("slug", mode="before")
    @classmethod
    def auto_slug(cls, v: Optional[str], info) -> str:
        if not v:
            name = info.data.get("name", "")
            return _slugify(name)
        return _slugify(v)


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    body: str = Field(default="")
    cover_image_url: Optional[str] = Field(None, max_length=512)
    status: str = Field(default="draft", pattern=r"^(draft|published|archived)$")
    author: Optional[str] = Field(None, max_length=120)
    category_id: Optional[uuid.UUID] = None
    tag_ids: List[uuid.UUID] = Field(default_factory=list)

    @field_validator("slug", mode="before")
    @classmethod
    def auto_slug(cls, v: Optional[str], info) -> str:
        if not v:
            title = info.data.get("title", "")
            return _slugify(title)
        return _slugify(v)


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    body: Optional[str] = None
    cover_image_url: Optional[str] = Field(None, max_length=512)
    status: Optional[str] = Field(None, pattern=r"^(draft|published|archived)$")
    author: Optional[str] = Field(None, max_length=120)
    category_id: Optional[uuid.UUID] = None
    tag_ids: Optional[List[uuid.UUID]] = None


class ArticleOut(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str]
    body: str
    cover_image_url: Optional[str]
    status: str
    author: Optional[str]
    view_count: int
    read_time_minutes: Optional[int]
    category: Optional[CategoryOut]
    tags: List[TagOut]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ArticleListOut(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str]
    status: str
    author: Optional[str]
    view_count: int
    read_time_minutes: Optional[int]
    category: Optional[CategoryOut]
    tags: List[TagOut]
    created_at: datetime
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PaginatedArticles(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ArticleListOut]


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class CommentCreate(BaseModel):
    author_name: str = Field(..., min_length=1, max_length=120)
    author_email: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., min_length=1)


class CommentOut(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    author_name: str
    body: str
    is_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Rating
# ---------------------------------------------------------------------------

class RatingCreate(BaseModel):
    session_key: str = Field(..., min_length=1, max_length=128)
    score: int = Field(..., ge=1, le=5)


class RatingOut(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RatingSummary(BaseModel):
    article_id: uuid.UUID
    average: float
    count: int


# ---------------------------------------------------------------------------
# AI request/response helpers
# ---------------------------------------------------------------------------

class AIGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=255, description="Article topic")
    language: str = Field(default="ar", max_length=10)
    target_word_count: int = Field(default=800, ge=100, le=5000)
    category_id: Optional[uuid.UUID] = None
    tag_ids: List[uuid.UUID] = Field(default_factory=list)


class AIImproveRequest(BaseModel):
    article_id: uuid.UUID
    instructions: Optional[str] = Field(None, max_length=500)


class AISummaryRequest(BaseModel):
    article_id: uuid.UUID
    max_sentences: int = Field(default=5, ge=1, le=20)


class AITranslateRequest(BaseModel):
    article_id: uuid.UUID
    target_language: str = Field(..., min_length=2, max_length=10)


class AITextResponse(BaseModel):
    result: str
