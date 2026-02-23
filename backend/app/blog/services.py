"""
services.py - Business logic for the Blog module.
"""

from __future__ import annotations

import math
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.blog.models import Article, ArticleTag, Category, Comment, Tag
from app.blog.schemas import (
    ArticleCreate,
    ArticleUpdate,
    CategoryCreate,
    CommentCreate,
    TagCreate,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _slugify(text: str) -> str:
    """
    Convert *text* (Arabic or Latin) into a URL-safe slug.

    - Converts to lowercase (Latin only; Arabic characters are preserved).
    - Replaces spaces and underscores with hyphens.
    - Removes characters that are neither alphanumeric, Arabic, nor hyphens.
    - Collapses multiple consecutive hyphens.
    - Strips leading/trailing hyphens.
    """
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Keep: ASCII alphanumeric, Arabic Unicode block (0600-06FF), hyphens
    text = re.sub(r"[^\w\u0600-\u06FF-]", "", text)
    # \w keeps underscores – replace any that crept back in
    text = re.sub(r"_+", "-", text)
    # Collapse multiple hyphens
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


# ---------------------------------------------------------------------------
# Category services
# ---------------------------------------------------------------------------


def get_categories(db: Session) -> List[Category]:
    """Return all active categories."""
    result = db.execute(select(Category).where(Category.is_active.is_(True)))
    return list(result.scalars().all())


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category, auto-generating slug from name when absent."""
    slug = data.slug or _slugify(data.name)
    existing = db.execute(select(Category).where(Category.slug == slug)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Category slug '{slug}' already exists")
    category = Category(name=data.name, slug=slug, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ---------------------------------------------------------------------------
# Tag services
# ---------------------------------------------------------------------------


def get_tags(db: Session) -> List[Tag]:
    """Return all active tags."""
    result = db.execute(select(Tag).where(Tag.is_active.is_(True)))
    return list(result.scalars().all())


def create_tag(db: Session, data: TagCreate) -> Tag:
    """Create a new tag, auto-generating slug from name when absent."""
    slug = data.slug or _slugify(data.name)
    existing = db.execute(select(Tag).where(Tag.slug == slug)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tag slug '{slug}' already exists")
    tag = Tag(name=data.name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# ---------------------------------------------------------------------------
# Article services
# ---------------------------------------------------------------------------


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = "published",
    category_slug: Optional[str] = None,
    tag_slug: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    """Return a paginated list of articles with optional filters."""
    stmt = select(Article).where(Article.is_active.is_(True))

    if status:
        stmt = stmt.where(Article.status == status)

    if category_slug:
        stmt = stmt.join(Category, Article.category_id == Category.id).where(
            Category.slug == category_slug
        )

    if tag_slug:
        stmt = stmt.join(ArticleTag, Article.id == ArticleTag.article_id).join(
            Tag, ArticleTag.tag_id == Tag.id
        ).where(Tag.slug == tag_slug)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Article.title.ilike(pattern), Article.content.ilike(pattern))
        )

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = db.execute(count_stmt).scalar_one()

    # Paginate
    offset = (page - 1) * per_page
    stmt = stmt.order_by(Article.created_at.desc()).offset(offset).limit(per_page)
    items = list(db.execute(stmt).scalars().all())

    pages = math.ceil(total / per_page) if total > 0 else 0

    return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}


def get_article_by_slug(db: Session, slug: str) -> tuple[Article, int]:
    """Fetch a single article by slug, increment its view counter, and return approved comment count."""
    result = db.execute(
        select(Article).where(Article.slug == slug, Article.is_active.is_(True))
    )
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    article.views = (article.views or 0) + 1
    db.commit()
    db.refresh(article)
    comment_count: int = db.execute(
        select(func.count(Comment.id)).where(
            Comment.article_id == article.id, Comment.is_approved.is_(True)
        )
    ).scalar_one()
    return article, comment_count


def get_article_by_id(db: Session, article_id: uuid.UUID) -> Article:
    """Fetch a single article by its UUID primary key."""
    result = db.execute(
        select(Article).where(Article.id == article_id, Article.is_active.is_(True))
    )
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create an article and associate tags; set published_at when status is 'published'."""
    slug = data.slug or _slugify(data.title)
    existing = db.execute(select(Article).where(Article.slug == slug)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Article slug '{slug}' already exists")
    published_at: Optional[datetime] = None
    if data.status == "published":
        published_at = datetime.now(timezone.utc)

    article = Article(
        title=data.title,
        slug=slug,
        content=data.content,
        excerpt=data.excerpt,
        cover_image=data.cover_image,
        author=data.author,
        status=data.status,
        category_id=data.category_id,
        published_at=published_at,
    )
    db.add(article)
    db.flush()  # populate article.id before creating ArticleTag rows

    if data.tag_ids:
        for tag_id in data.tag_ids:
            db.add(ArticleTag(article_id=article.id, tag_id=tag_id))

    db.commit()
    db.refresh(article)
    return article


def update_article(db: Session, article_id: uuid.UUID, data: ArticleUpdate) -> Article:
    """Update an existing article and refresh tag associations when supplied."""
    article = get_article_by_id(db, article_id)

    update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})

    # Auto-set published_at when transitioning to published status
    if "status" in update_data and update_data["status"] == "published" and not article.published_at:
        update_data["published_at"] = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(article, field, value)

    if data.tag_ids is not None:
        # Replace existing tag associations
        db.execute(
            ArticleTag.__table__.delete().where(ArticleTag.article_id == article.id)
        )
        for tag_id in data.tag_ids:
            db.add(ArticleTag(article_id=article.id, tag_id=tag_id))

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: uuid.UUID) -> None:
    """Soft-delete an article by setting is_active=False."""
    article = get_article_by_id(db, article_id)
    article.is_active = False
    db.commit()


# ---------------------------------------------------------------------------
# Comment services
# ---------------------------------------------------------------------------


def add_comment(db: Session, article_id: uuid.UUID, data: CommentCreate) -> Comment:
    """Append a (unapproved) comment to the given article."""
    # Ensure article exists
    get_article_by_id(db, article_id)

    comment = Comment(
        article_id=article_id,
        author_name=data.author_name,
        author_email=data.author_email,
        content=data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
