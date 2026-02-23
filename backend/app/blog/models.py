"""
blog/models.py – SQLAlchemy ORM models for the Blog module.

Tables
------
article_categories  – content categories (e.g. finance, automation)
article_tags        – free-form tags
articles            – blog articles (supports Markdown body)
article_tag_map     – many-to-many join between articles and tags
article_comments    – reader comments on articles
article_ratings     – one rating per user per article
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import _utcnow


# ---------------------------------------------------------------------------
# Many-to-many join table: articles <-> tags
# ---------------------------------------------------------------------------
article_tag_map = Table(
    "article_tag_map",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("article_tags.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# ArticleCategory
# ---------------------------------------------------------------------------
class ArticleCategory(Base):
    """Content category (finance, automation, marketing, …)."""

    __tablename__ = "article_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    articles: Mapped[List["Article"]] = relationship(
        "Article", back_populates="category", passive_deletes=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ArticleCategory name={self.name!r}>"


# ---------------------------------------------------------------------------
# ArticleTag
# ---------------------------------------------------------------------------
class ArticleTag(Base):
    """Free-form tag that can be attached to many articles."""

    __tablename__ = "article_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    articles: Mapped[List["Article"]] = relationship(
        "Article", secondary=article_tag_map, back_populates="tags"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ArticleTag name={self.name!r}>"


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------
class ArticleStatus(str):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Article(Base):
    """A single blog article."""

    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_status_created", "status", "created_at"),
        Index("ix_articles_category", "category_id"),
        CheckConstraint("status IN ('draft','published','archived')", name="ck_article_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(
        Text, nullable=False, default="", comment="Markdown-formatted article body"
    )
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    author: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    read_time_minutes: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("article_categories.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    category: Mapped[Optional[ArticleCategory]] = relationship(
        "ArticleCategory", back_populates="articles"
    )
    tags: Mapped[List[ArticleTag]] = relationship(
        "ArticleTag", secondary=article_tag_map, back_populates="articles"
    )
    comments: Mapped[List["ArticleComment"]] = relationship(
        "ArticleComment", back_populates="article", passive_deletes=True
    )
    ratings: Mapped[List["ArticleRating"]] = relationship(
        "ArticleRating", back_populates="article", passive_deletes=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Article id={self.id} title={self.title!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# ArticleComment
# ---------------------------------------------------------------------------
class ArticleComment(Base):
    """Reader comment on an article."""

    __tablename__ = "article_comments"
    __table_args__ = (Index("ix_article_comments_article", "article_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    author_name: Mapped[str] = mapped_column(String(120), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    article: Mapped[Article] = relationship("Article", back_populates="comments")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ArticleComment id={self.id} article={self.article_id}>"


# ---------------------------------------------------------------------------
# ArticleRating
# ---------------------------------------------------------------------------
class ArticleRating(Base):
    """One star-rating (1–5) per user session per article."""

    __tablename__ = "article_ratings"
    __table_args__ = (
        UniqueConstraint("article_id", "session_key", name="uq_rating_article_session"),
        CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    session_key: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Anonymous session identifier"
    )
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    article: Mapped[Article] = relationship("Article", back_populates="ratings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ArticleRating article={self.article_id} score={self.score}>"
