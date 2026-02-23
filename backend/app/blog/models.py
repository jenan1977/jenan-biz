"""
models.py - SQLAlchemy ORM models for the Blog module.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.core.database import Base


# ---------------------------------------------------------------------------
# Association table (no BaseModel – composite PK only)
# ---------------------------------------------------------------------------


class ArticleTag(Base):
    """Many-to-many join table between articles and tags."""

    __tablename__ = "blog_article_tags"
    __table_args__ = (PrimaryKeyConstraint("article_id", "tag_id"),)

    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_tags.id", ondelete="CASCADE"),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class Category(BaseModel):
    """Blog post category."""

    __tablename__ = "blog_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    articles: Mapped[List["Article"]] = relationship(
        "Article",
        back_populates="category",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Category id={self.id} slug={self.slug!r}>"


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class Tag(BaseModel):
    """Blog post tag."""

    __tablename__ = "blog_tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    # Relationships
    articles: Mapped[List["Article"]] = relationship(
        "Article",
        secondary="blog_article_tags",
        back_populates="tags",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tag id={self.id} slug={self.slug!r}>"


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------


class Article(BaseModel):
    """Blog article / post."""

    __tablename__ = "blog_articles"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(600), unique=True, index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False, default="Jenan BIZ AI")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft", index=True)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Foreign Keys
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("blog_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="articles",
        lazy="select",
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="blog_article_tags",
        back_populates="articles",
        lazy="select",
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="article",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Article id={self.id} slug={self.slug!r}>"


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------


class Comment(BaseModel):
    """Reader comment on a blog article."""

    __tablename__ = "blog_comments"

    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("blog_articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="comments",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Comment id={self.id} article_id={self.article_id}>"
