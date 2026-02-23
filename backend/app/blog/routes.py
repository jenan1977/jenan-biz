"""
blog/routes.py – FastAPI router for the Blog module.

Prefix: /api/v1/blog

Endpoints
---------
Categories
  GET    /categories
  POST   /categories

Tags
  GET    /tags
  POST   /tags

Articles (CRUD)
  GET    /articles                       list with search/filter/pagination
  POST   /articles                       create
  GET    /articles/{id_or_slug}          retrieve (increments view_count)
  PATCH  /articles/{article_id}          update
  DELETE /articles/{article_id}          delete

Comments
  GET    /articles/{article_id}/comments
  POST   /articles/{article_id}/comments

Ratings
  POST   /articles/{article_id}/ratings
  GET    /articles/{article_id}/ratings/summary

AI
  POST   /articles/auto-generate
  POST   /articles/ai-improve
  POST   /articles/ai-summary
  POST   /articles/ai-translate
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.blog import services
from app.blog.schemas import (
    AIGenerateRequest,
    AIImproveRequest,
    AISummaryRequest,
    AITextResponse,
    AITranslateRequest,
    ArticleCreate,
    ArticleOut,
    ArticleListOut,
    ArticleUpdate,
    CategoryCreate,
    CategoryOut,
    CommentCreate,
    CommentOut,
    PaginatedArticles,
    RatingCreate,
    RatingOut,
    RatingSummary,
    TagCreate,
    TagOut,
)
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/blog", tags=["blog"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_article_or_404(db: Session, article_id: uuid.UUID):
    article = services.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return services.list_categories(db)


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    cat = services.create_category(db, body)
    db.commit()
    return cat


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@router.get("/tags", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return services.list_tags(db)


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(body: TagCreate, db: Session = Depends(get_db)):
    tag = services.create_tag(db, body)
    db.commit()
    return tag


# ---------------------------------------------------------------------------
# Articles – CRUD
# ---------------------------------------------------------------------------

@router.get("/articles", response_model=PaginatedArticles)
def list_articles(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_id: Optional[uuid.UUID] = Query(None),
    tag_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total, items = services.list_articles(
        db,
        status=status_filter,
        category_id=category_id,
        tag_id=tag_id,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedArticles(total=total, page=page, page_size=page_size, items=items)


@router.post("/articles", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(body: ArticleCreate, db: Session = Depends(get_db)):
    article = services.create_article(db, body)
    db.commit()
    db.refresh(article)
    return article


@router.get("/articles/{id_or_slug}", response_model=ArticleOut)
def get_article(id_or_slug: str, db: Session = Depends(get_db)):
    article = None
    try:
        uid = uuid.UUID(id_or_slug)
        article = services.get_article(db, uid)
    except ValueError:
        article = services.get_article_by_slug(db, id_or_slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    services.increment_view_count(db, article)
    db.commit()
    return article


@router.patch("/articles/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: uuid.UUID,
    body: ArticleUpdate,
    db: Session = Depends(get_db),
):
    article = _get_article_or_404(db, article_id)
    updated = services.update_article(db, article, body)
    db.commit()
    db.refresh(updated)
    return updated


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: uuid.UUID, db: Session = Depends(get_db)):
    article = _get_article_or_404(db, article_id)
    services.delete_article(db, article)
    db.commit()


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

@router.get("/articles/{article_id}/comments", response_model=List[CommentOut])
def list_comments(article_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_article_or_404(db, article_id)
    return services.list_comments(db, article_id, approved_only=True)


@router.post(
    "/articles/{article_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    article_id: uuid.UUID,
    body: CommentCreate,
    db: Session = Depends(get_db),
):
    article = _get_article_or_404(db, article_id)
    comment = services.add_comment(db, article, body)
    db.commit()
    return comment


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------

@router.post(
    "/articles/{article_id}/ratings",
    response_model=RatingOut,
    status_code=status.HTTP_201_CREATED,
)
def rate_article(
    article_id: uuid.UUID,
    body: RatingCreate,
    db: Session = Depends(get_db),
):
    article = _get_article_or_404(db, article_id)
    rating = services.rate_article(db, article, body)
    db.commit()
    return rating


@router.get("/articles/{article_id}/ratings/summary", response_model=RatingSummary)
def rating_summary(article_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_article_or_404(db, article_id)
    return services.get_rating_summary(db, article_id)


# ---------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------

def _ai_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(exc),
    )


@router.post("/articles/auto-generate", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def auto_generate_article(body: AIGenerateRequest, db: Session = Depends(get_db)):
    """Generate a new article using OpenAI and save it as a draft."""
    try:
        article = services.ai_generate_article(db, body)
        db.commit()
        db.refresh(article)
        return article
    except RuntimeError as exc:
        raise _ai_error(exc)


@router.post("/articles/ai-improve", response_model=AITextResponse)
def ai_improve(body: AIImproveRequest, db: Session = Depends(get_db)):
    """Return an AI-improved version of the article body."""
    article = _get_article_or_404(db, body.article_id)
    try:
        improved = services.ai_improve_article(db, article, body.instructions)
        return AITextResponse(result=improved)
    except RuntimeError as exc:
        raise _ai_error(exc)


@router.post("/articles/ai-summary", response_model=AITextResponse)
def ai_summary(body: AISummaryRequest, db: Session = Depends(get_db)):
    """Return a short AI-generated summary of an article."""
    article = _get_article_or_404(db, body.article_id)
    try:
        summary = services.ai_summarize_article(article, body.max_sentences)
        return AITextResponse(result=summary)
    except RuntimeError as exc:
        raise _ai_error(exc)


@router.post("/articles/ai-translate", response_model=AITextResponse)
def ai_translate(body: AITranslateRequest, db: Session = Depends(get_db)):
    """Return a translation of the article body."""
    article = _get_article_or_404(db, body.article_id)
    try:
        translated = services.ai_translate_article(article, body.target_language)
        return AITextResponse(result=translated)
    except RuntimeError as exc:
        raise _ai_error(exc)
