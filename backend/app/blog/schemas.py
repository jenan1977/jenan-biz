"""
schemas.py - Pydantic v2 schemas for the Blog module.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Category schemas
# ---------------------------------------------------------------------------


class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------------------------
# Tag schemas
# ---------------------------------------------------------------------------


class TagBase(BaseModel):
    name: str
    slug: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------------------------
# Comment schemas
# ---------------------------------------------------------------------------


class CommentBase(BaseModel):
    author_name: str
    author_email: Optional[str] = None
    content: str


class CommentCreate(CommentBase):
    pass


class CommentOut(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    is_approved: bool


# ---------------------------------------------------------------------------
# Article schemas
# ---------------------------------------------------------------------------


class ArticleBase(BaseModel):
    title: str
    slug: Optional[str] = None
    content: str
    excerpt: Optional[str] = None
    cover_image: Optional[str] = None
    author: str = "Jenan BIZ AI"
    status: str = "draft"
    category_id: Optional[uuid.UUID] = None


class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[uuid.UUID]] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    tag_ids: Optional[List[uuid.UUID]] = None


class ArticleOut(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    views: int
    likes: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []
    comment_count: int = 0


class ArticleListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    cover_image: Optional[str] = None
    author: str
    status: str
    views: int
    likes: int
    published_at: Optional[datetime] = None
    created_at: datetime
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []


class PaginatedArticles(BaseModel):
    items: List[ArticleListOut]
    total: int
    page: int
    per_page: int
    pages: int
