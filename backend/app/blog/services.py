"""
blog/services.py – Business logic for the Blog module.

All database operations are handled here so that routers stay thin.
AI features call an optional OpenAI client; if OPENAI_API_KEY is not
configured the AI endpoints return a clear error rather than crashing.
"""

from __future__ import annotations

import math
import os
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.blog.models import (
    Article,
    ArticleCategory,
    ArticleComment,
    ArticleRating,
    ArticleTag,
)
from app.blog.schemas import (
    AIGenerateRequest,
    ArticleCreate,
    ArticleUpdate,
    CategoryCreate,
    CommentCreate,
    RatingCreate,
    TagCreate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WORDS_PER_MINUTE = 200


def _estimate_read_time(body: str) -> int:
    """Return estimated reading time in minutes (minimum 1)."""
    word_count = len(body.split())
    return max(1, math.ceil(word_count / _WORDS_PER_MINUTE))


def _unique_slug(db: Session, base_slug: str, model, exclude_id: Optional[uuid.UUID] = None) -> str:
    """Ensure slug uniqueness by appending a counter when needed."""
    slug = base_slug
    counter = 1
    while True:
        q = db.query(model).filter(model.slug == slug)
        if exclude_id:
            q = q.filter(model.id != exclude_id)
        if q.first() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# ---------------------------------------------------------------------------
# Category CRUD
# ---------------------------------------------------------------------------

def create_category(db: Session, data: CategoryCreate) -> ArticleCategory:
    slug = _unique_slug(db, data.slug or data.name.lower(), ArticleCategory)
    cat = ArticleCategory(name=data.name, slug=slug, description=data.description)
    db.add(cat)
    db.flush()
    return cat


def list_categories(db: Session) -> List[ArticleCategory]:
    return db.query(ArticleCategory).order_by(ArticleCategory.name).all()


def get_category(db: Session, category_id: uuid.UUID) -> Optional[ArticleCategory]:
    return db.get(ArticleCategory, category_id)


# ---------------------------------------------------------------------------
# Tag CRUD
# ---------------------------------------------------------------------------

def create_tag(db: Session, data: TagCreate) -> ArticleTag:
    slug = _unique_slug(db, data.slug or data.name.lower(), ArticleTag)
    tag = ArticleTag(name=data.name, slug=slug)
    db.add(tag)
    db.flush()
    return tag


def list_tags(db: Session) -> List[ArticleTag]:
    return db.query(ArticleTag).order_by(ArticleTag.name).all()


def get_or_create_tag(db: Session, name: str) -> ArticleTag:
    slug = re.sub(r"[\s_]+", "-", name.strip().lower())
    tag = db.query(ArticleTag).filter(ArticleTag.slug == slug).first()
    if tag is None:
        tag = ArticleTag(name=name.strip(), slug=slug)
        db.add(tag)
        db.flush()
    return tag


# ---------------------------------------------------------------------------
# Article CRUD
# ---------------------------------------------------------------------------

def _load_tags(db: Session, tag_ids: List[uuid.UUID]) -> List[ArticleTag]:
    if not tag_ids:
        return []
    return db.query(ArticleTag).filter(ArticleTag.id.in_(tag_ids)).all()


def _article_query(db: Session):
    return db.query(Article).options(
        selectinload(Article.category),
        selectinload(Article.tags),
    )


def create_article(db: Session, data: ArticleCreate) -> Article:
    slug = _unique_slug(db, data.slug or data.title.lower(), Article)
    now = datetime.now(timezone.utc)
    article = Article(
        title=data.title,
        slug=slug,
        summary=data.summary,
        body=data.body or "",
        cover_image_url=data.cover_image_url,
        status=data.status,
        author=data.author,
        category_id=data.category_id,
        read_time_minutes=_estimate_read_time(data.body or ""),
        published_at=now if data.status == "published" else None,
    )
    article.tags = _load_tags(db, data.tag_ids)
    db.add(article)
    db.flush()
    return article


def get_article(db: Session, article_id: uuid.UUID) -> Optional[Article]:
    return _article_query(db).filter(Article.id == article_id).first()


def get_article_by_slug(db: Session, slug: str) -> Optional[Article]:
    return _article_query(db).filter(Article.slug == slug).first()


def list_articles(
    db: Session,
    *,
    status: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    tag_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[int, List[Article]]:
    q = _article_query(db)
    if status:
        q = q.filter(Article.status == status)
    if category_id:
        q = q.filter(Article.category_id == category_id)
    if tag_id:
        q = q.filter(Article.tags.any(ArticleTag.id == tag_id))
    if search:
        term = f"%{search}%"
        q = q.filter(or_(Article.title.ilike(term), Article.summary.ilike(term)))
    total = q.count()
    items = q.order_by(Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def update_article(db: Session, article: Article, data: ArticleUpdate) -> Article:
    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)
    for field, value in update_data.items():
        setattr(article, field, value)
    if "slug" in update_data:
        article.slug = _unique_slug(db, update_data["slug"], Article, exclude_id=article.id)
    if tag_ids is not None:
        article.tags = _load_tags(db, tag_ids)
    if update_data.get("status") == "published" and article.published_at is None:
        article.published_at = datetime.now(timezone.utc)
    article.read_time_minutes = _estimate_read_time(article.body or "")
    db.flush()
    return article


def delete_article(db: Session, article: Article) -> None:
    db.delete(article)
    db.flush()


def increment_view_count(db: Session, article: Article) -> None:
    article.view_count = (article.view_count or 0) + 1
    db.flush()


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

def add_comment(db: Session, article: Article, data: CommentCreate) -> ArticleComment:
    comment = ArticleComment(
        article_id=article.id,
        author_name=data.author_name,
        author_email=data.author_email,
        body=data.body,
        is_approved=False,
    )
    db.add(comment)
    db.flush()
    return comment


def list_comments(db: Session, article_id: uuid.UUID, approved_only: bool = True) -> List[ArticleComment]:
    q = db.query(ArticleComment).filter(ArticleComment.article_id == article_id)
    if approved_only:
        q = q.filter(ArticleComment.is_approved.is_(True))
    return q.order_by(ArticleComment.created_at).all()


# ---------------------------------------------------------------------------
# Rating
# ---------------------------------------------------------------------------

def rate_article(db: Session, article: Article, data: RatingCreate) -> ArticleRating:
    existing = (
        db.query(ArticleRating)
        .filter(
            ArticleRating.article_id == article.id,
            ArticleRating.session_key == data.session_key,
        )
        .first()
    )
    if existing:
        existing.score = data.score
        db.flush()
        return existing
    rating = ArticleRating(
        article_id=article.id,
        session_key=data.session_key,
        score=data.score,
    )
    db.add(rating)
    db.flush()
    return rating


def get_rating_summary(db: Session, article_id: uuid.UUID) -> dict:
    row = (
        db.query(
            func.avg(ArticleRating.score).label("avg"),
            func.count(ArticleRating.id).label("cnt"),
        )
        .filter(ArticleRating.article_id == article_id)
        .first()
    )
    return {
        "article_id": article_id,
        "average": round(float(row.avg or 0), 2),
        "count": row.cnt or 0,
    }


# ---------------------------------------------------------------------------
# AI helpers
# ---------------------------------------------------------------------------

def _get_openai_client():
    """Return an OpenAI client or raise RuntimeError if not configured."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Configure it to use AI features."
        )
    try:
        from openai import OpenAI  # type: ignore[import-untyped]
        return OpenAI(api_key=api_key)
    except ImportError as exc:
        raise RuntimeError(
            "openai package is not installed. Add 'openai' to requirements.txt."
        ) from exc


def _chat(client, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


_BLOG_SYSTEM_PROMPT = (
    "أنت كاتب متخصص في الأعمال والمال والريادة. "
    "تكتب مقالات احترافية وعملية تناسب رواد الأعمال والمستثمرين العرب. "
    "استخدم أسلوباً واضحاً ومباشراً مع أمثلة وأرقام حقيقية."
)

_IMPROVE_SYSTEM_PROMPT = (
    "أنت محرر محترف. مهمتك تحسين المقالات من حيث الأسلوب والوضوح والتدفق "
    "دون تغيير المعنى الأساسي. أعد المقال كاملاً بعد التحسين."
)

_FINANCIAL_REPORT_SYSTEM_PROMPT = (
    "أنت محلل مالي متخصص في إعداد التقارير. "
    "تقدم تحليلات دقيقة مع أرقام ومؤشرات مالية واضحة."
)


def ai_generate_article(db: Session, data: AIGenerateRequest) -> Article:
    """Generate a full article using OpenAI and persist it."""
    client = _get_openai_client()
    user_prompt = (
        f"اكتب مقالاً شاملاً عن: {data.topic}\n"
        f"اللغة: {'العربية' if data.language == 'ar' else data.language}\n"
        f"الطول المستهدف: حوالي {data.target_word_count} كلمة\n"
        "الهيكل: عنوان جذاب، مقدمة، محتوى رئيسي مقسّم بعناوين فرعية، خاتمة وتوصيات.\n"
        "استخدم تنسيق Markdown."
    )
    content = _chat(client, _BLOG_SYSTEM_PROMPT, user_prompt, max_tokens=3000)

    # Extract title from first Markdown heading
    lines = content.strip().split("\n")
    title = data.topic
    body = content
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            body = "\n".join(lines[i + 1:]).strip()
            break

    article_data = ArticleCreate(
        title=title,
        body=body,
        status="draft",
        category_id=data.category_id,
        tag_ids=data.tag_ids,
    )
    return create_article(db, article_data)


def ai_improve_article(db: Session, article: Article, instructions: Optional[str]) -> str:
    """Return improved body text for an article."""
    client = _get_openai_client()
    user_prompt = f"المقال:\n\n{article.body}"
    if instructions:
        user_prompt += f"\n\nتعليمات إضافية: {instructions}"
    return _chat(client, _IMPROVE_SYSTEM_PROMPT, user_prompt, max_tokens=3000)


def ai_summarize_article(article: Article, max_sentences: int = 5) -> str:
    """Return a concise summary using OpenAI."""
    client = _get_openai_client()
    system = "أنت ملخّص محترف. لخّص النص المعطى في عدد الجمل المحدد."
    user_prompt = f"لخّص هذا المقال في {max_sentences} جمل كحد أقصى:\n\n{article.body}"
    return _chat(client, system, user_prompt, max_tokens=500)


def ai_translate_article(article: Article, target_language: str) -> str:
    """Translate the article body to the target language."""
    client = _get_openai_client()
    lang_map = {"en": "English", "fr": "French", "de": "German", "ar": "Arabic"}
    lang_name = lang_map.get(target_language, target_language)
    system = f"أنت مترجم محترف. ترجم النص إلى {lang_name} مع الحفاظ على التنسيق."
    user_prompt = f"ترجم هذا المقال:\n\n{article.body}"
    return _chat(client, system, user_prompt, max_tokens=3000)
