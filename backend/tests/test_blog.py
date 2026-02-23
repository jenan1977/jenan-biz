"""
test_blog.py - Unit tests for the Blog module (services layer).

Uses an in-memory SQLite database so no live PostgreSQL is required.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
# Register all ORM models
import app.models  # noqa: F401
import app.blog.models  # noqa: F401  (registers blog tables)

from app.blog.services import (
    _slugify,
    create_article,
    create_category,
    create_tag,
    delete_article,
    get_article_by_id,
    get_article_by_slug,
    get_articles,
    get_categories,
    get_tags,
    add_comment,
    update_article,
)
from app.blog.schemas import (
    ArticleCreate,
    ArticleUpdate,
    CategoryCreate,
    CommentCreate,
    TagCreate,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture
def db(engine):
    """Fresh DB session per test."""
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()


# ---------------------------------------------------------------------------
# _slugify
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_latin_lowercase(self):
        assert _slugify("Hello World") == "hello-world"

    def test_arabic_text(self):
        slug = _slugify("عالم الثراء")
        assert "-" in slug or "عالمالثراء" in slug.replace("-", "")

    def test_strips_special_chars(self):
        slug = _slugify("Hello! World? Test.")
        assert "!" not in slug
        assert "?" not in slug
        assert "." not in slug

    def test_collapses_hyphens(self):
        assert "--" not in _slugify("hello   world")


# ---------------------------------------------------------------------------
# Category services
# ---------------------------------------------------------------------------


class TestCategoryServices:
    def test_create_category(self, db):
        cat = create_category(db, CategoryCreate(name="الأعمال"))
        assert cat.id is not None
        assert cat.slug  # auto-generated

    def test_get_categories(self, db):
        create_category(db, CategoryCreate(name="فئة 1"))
        create_category(db, CategoryCreate(name="فئة 2"))
        cats = get_categories(db)
        assert len(cats) == 2

    def test_duplicate_slug_raises_409(self, db):
        from fastapi import HTTPException

        create_category(db, CategoryCreate(name="تكرار", slug="dup-slug"))
        with pytest.raises(HTTPException) as exc_info:
            create_category(db, CategoryCreate(name="تكرار2", slug="dup-slug"))
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tag services
# ---------------------------------------------------------------------------


class TestTagServices:
    def test_create_tag(self, db):
        tag = create_tag(db, TagCreate(name="استثمار"))
        assert tag.id is not None
        assert tag.slug

    def test_get_tags(self, db):
        create_tag(db, TagCreate(name="وسم1"))
        create_tag(db, TagCreate(name="وسم2"))
        tags = get_tags(db)
        assert len(tags) == 2

    def test_duplicate_tag_slug_raises_409(self, db):
        from fastapi import HTTPException

        create_tag(db, TagCreate(name="dup", slug="dup-tag"))
        with pytest.raises(HTTPException):
            create_tag(db, TagCreate(name="dup2", slug="dup-tag"))


# ---------------------------------------------------------------------------
# Article services
# ---------------------------------------------------------------------------


class TestArticleServices:
    def _make_article(self, db, title="مقالة تجريبية", status="draft"):
        return create_article(
            db,
            ArticleCreate(
                title=title,
                content="محتوى تجريبي للاختبار",
                status=status,
            ),
        )

    def test_create_article(self, db):
        article = self._make_article(db)
        assert article.id is not None
        assert article.slug

    def test_create_published_sets_published_at(self, db):
        article = self._make_article(db, status="published")
        assert article.published_at is not None

    def test_draft_does_not_set_published_at(self, db):
        article = self._make_article(db, status="draft")
        assert article.published_at is None

    def test_get_article_by_id(self, db):
        article = self._make_article(db)
        fetched = get_article_by_id(db, article.id)
        assert fetched.id == article.id

    def test_get_article_by_slug(self, db):
        article = self._make_article(db)
        fetched, comment_count = get_article_by_slug(db, article.slug)
        assert fetched.id == article.id
        assert comment_count == 0

    def test_get_article_by_slug_increments_views(self, db):
        article = self._make_article(db)
        original_views = article.views
        get_article_by_slug(db, article.slug)
        updated, _ = get_article_by_slug(db, article.slug)
        assert updated.views == original_views + 2  # called twice

    def test_get_articles_pagination(self, db):
        for i in range(5):
            self._make_article(db, title=f"مقالة {i}", status="published")
        result = get_articles(db, page=1, per_page=3, status="published")
        assert result["total"] == 5
        assert len(result["items"]) == 3
        assert result["pages"] == 2

    def test_get_articles_status_filter(self, db):
        self._make_article(db, status="published")
        self._make_article(db, title="مسودة", status="draft")
        result = get_articles(db, status="published")
        assert result["total"] == 1

    def test_get_articles_search(self, db):
        self._make_article(db, title="أتمتة الأعمال", status="published")
        self._make_article(db, title="التسويق الرقمي", status="published")
        result = get_articles(db, search="أتمتة")
        assert result["total"] == 1

    def test_update_article(self, db):
        article = self._make_article(db)
        updated = update_article(db, article.id, ArticleUpdate(title="عنوان محدّث"))
        assert updated.title == "عنوان محدّث"

    def test_update_to_published_sets_published_at(self, db):
        article = self._make_article(db, status="draft")
        assert article.published_at is None
        updated = update_article(db, article.id, ArticleUpdate(status="published"))
        assert updated.published_at is not None

    def test_delete_article_soft_delete(self, db):
        from fastapi import HTTPException

        article = self._make_article(db)
        delete_article(db, article.id)
        with pytest.raises(HTTPException) as exc_info:
            get_article_by_id(db, article.id)
        assert exc_info.value.status_code == 404

    def test_duplicate_slug_raises_409(self, db):
        from fastapi import HTTPException

        self._make_article(db, title="مقالة")
        with pytest.raises(HTTPException) as exc_info:
            self._make_article(db, title="مقالة")
        assert exc_info.value.status_code == 409

    def test_create_article_with_tags(self, db):
        tag = create_tag(db, TagCreate(name="وسم-اختبار"))
        article = create_article(
            db,
            ArticleCreate(
                title="مقالة بوسوم",
                content="محتوى",
                tag_ids=[tag.id],
            ),
        )
        assert len(article.tags) == 1
        assert article.tags[0].id == tag.id

    def test_create_article_with_category(self, db):
        cat = create_category(db, CategoryCreate(name="تقنية"))
        article = create_article(
            db,
            ArticleCreate(
                title="مقالة بفئة",
                content="محتوى",
                category_id=cat.id,
            ),
        )
        assert article.category_id == cat.id


# ---------------------------------------------------------------------------
# Comment services
# ---------------------------------------------------------------------------


class TestCommentServices:
    def test_add_comment(self, db):
        article = create_article(
            db, ArticleCreate(title="مقالة تعليق", content="محتوى")
        )
        comment = add_comment(
            db,
            article.id,
            CommentCreate(author_name="أحمد", content="تعليق رائع!"),
        )
        assert comment.id is not None
        assert comment.is_approved is False  # default: unapproved

    def test_add_comment_to_nonexistent_article(self, db):
        import uuid
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            add_comment(
                db,
                uuid.uuid4(),
                CommentCreate(author_name="علي", content="تعليق"),
            )
        assert exc_info.value.status_code == 404
