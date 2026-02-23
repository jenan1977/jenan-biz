"""
routes.py - FastAPI router for the Blog module.

Prefix : /api/v1/blog
Tag    : blog
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.blog import services
from app.blog.schemas import (
    ArticleCreate,
    ArticleListOut,
    ArticleOut,
    ArticleUpdate,
    CategoryCreate,
    CategoryOut,
    CommentCreate,
    CommentOut,
    PaginatedArticles,
    TagCreate,
    TagOut,
)
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/blog", tags=["blog"])


# ---------------------------------------------------------------------------
# Article endpoints
# ---------------------------------------------------------------------------


@router.get("/articles", response_model=PaginatedArticles)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str = Query("published"),
    category: Optional[str] = Query(None, description="Category slug"),
    tag: Optional[str] = Query(None, description="Tag slug"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedArticles:
    """Return a paginated list of articles."""
    result = services.get_articles(
        db,
        page=page,
        per_page=per_page,
        status=status,
        category_slug=category,
        tag_slug=tag,
        search=search,
    )
    items = [
        ArticleListOut.model_validate(a) for a in result["items"]
    ]
    return PaginatedArticles(
        items=items,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        pages=result["pages"],
    )


@router.post("/articles", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(data: ArticleCreate, db: Session = Depends(get_db)) -> ArticleOut:
    """Create a new article."""
    article = services.create_article(db, data)
    return ArticleOut.model_validate(article)


@router.get("/articles/search", response_model=PaginatedArticles)
def search_articles(
    q: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedArticles:
    """Search articles by title or content."""
    result = services.get_articles(db, page=page, per_page=per_page, status=None, search=q)
    items = [ArticleListOut.model_validate(a) for a in result["items"]]
    return PaginatedArticles(
        items=items,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        pages=result["pages"],
    )


@router.get("/articles/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)) -> ArticleOut:
    """Retrieve a single article by slug (also increments view count)."""
    article, comment_count = services.get_article_by_slug(db, slug)
    out = ArticleOut.model_validate(article)
    out.comment_count = comment_count
    return out


@router.put("/articles/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: uuid.UUID, data: ArticleUpdate, db: Session = Depends(get_db)
) -> ArticleOut:
    """Update an existing article."""
    article = services.update_article(db, article_id, data)
    return ArticleOut.model_validate(article)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_article(article_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Soft-delete an article."""
    services.delete_article(db, article_id)


@router.post(
    "/articles/{article_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    article_id: uuid.UUID, data: CommentCreate, db: Session = Depends(get_db)
) -> CommentOut:
    """Add a comment to an article."""
    comment = services.add_comment(db, article_id, data)
    return CommentOut.model_validate(comment)


# ---------------------------------------------------------------------------
# Category endpoints
# ---------------------------------------------------------------------------


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryOut]:
    """List all active categories."""
    categories = services.get_categories(db)
    return [CategoryOut.model_validate(c) for c in categories]


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryOut:
    """Create a new category."""
    category = services.create_category(db, data)
    return CategoryOut.model_validate(category)


# ---------------------------------------------------------------------------
# Tag endpoints
# ---------------------------------------------------------------------------


@router.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)) -> list[TagOut]:
    """List all active tags."""
    tags = services.get_tags(db)
    return [TagOut.model_validate(t) for t in tags]


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(data: TagCreate, db: Session = Depends(get_db)) -> TagOut:
    """Create a new tag."""
    tag = services.create_tag(db, data)
    return TagOut.model_validate(tag)
