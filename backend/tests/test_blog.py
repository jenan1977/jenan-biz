"""
test_blog.py – Unit tests for the Blog module.

Uses an in-memory SQLite database; no live PostgreSQL required.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base

# Register all models (including blog)
import app.models  # noqa: F401

from app.blog.models import Article, ArticleCategory, ArticleComment, ArticleRating, ArticleTag
from app.blog import services
from app.blog.schemas import (
    ArticleCreate,
    ArticleUpdate,
    CategoryCreate,
    CommentCreate,
    RatingCreate,
    TagCreate,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.rollback()
    session.close()


# ---------------------------------------------------------------------------
# Category tests
# ---------------------------------------------------------------------------


class TestCategory:
    def test_create_category(self, db):
        data = CategoryCreate(name="Finance", description="Financial topics")
        cat = services.create_category(db, data)
        db.commit()
        assert cat.id is not None
        assert cat.name == "Finance"
        assert cat.slug == "finance"

    def test_list_categories(self, db):
        services.create_category(db, CategoryCreate(name="Marketing"))
        db.commit()
        cats = services.list_categories(db)
        assert len(cats) >= 1

    def test_slug_auto_generated(self, db):
        data = CategoryCreate(name="Business Automation")
        cat = services.create_category(db, data)
        db.commit()
        assert "business" in cat.slug
        assert "automation" in cat.slug

    def test_duplicate_slug_gets_suffix(self, db):
        # Provide an explicit slug that collides with the one auto-generated for "Tech Sector"
        services.create_category(db, CategoryCreate(name="Tech Sector", slug="techslug"))
        db.commit()
        # A second category that would resolve to the same slug should receive a suffix
        cat2 = services.create_category(db, CategoryCreate(name="Tech Sector 2", slug="techslug"))
        db.commit()
        assert cat2.slug != "techslug"
        assert cat2.slug.startswith("techslug")


# ---------------------------------------------------------------------------
# Tag tests
# ---------------------------------------------------------------------------


class TestTag:
    def test_create_tag(self, db):
        tag = services.create_tag(db, TagCreate(name="AI"))
        db.commit()
        assert tag.id is not None
        assert tag.name == "AI"

    def test_get_or_create_tag_idempotent(self, db):
        t1 = services.get_or_create_tag(db, "Python")
        db.commit()
        t2 = services.get_or_create_tag(db, "Python")
        db.commit()
        assert t1.id == t2.id


# ---------------------------------------------------------------------------
# Article tests
# ---------------------------------------------------------------------------


class TestArticle:
    def test_create_article_draft(self, db):
        data = ArticleCreate(title="Hello World", body="This is the body.")
        article = services.create_article(db, data)
        db.commit()
        assert article.id is not None
        assert article.status == "draft"
        assert article.published_at is None
        assert article.read_time_minutes >= 1

    def test_create_article_published(self, db):
        data = ArticleCreate(title="Published", body="Body text.", status="published")
        article = services.create_article(db, data)
        db.commit()
        assert article.status == "published"
        assert article.published_at is not None

    def test_slug_auto_generated(self, db):
        data = ArticleCreate(title="My Great Article", body="content")
        article = services.create_article(db, data)
        db.commit()
        assert "my" in article.slug or "great" in article.slug

    def test_get_article_by_id(self, db):
        data = ArticleCreate(title="Get by ID", body="x")
        article = services.create_article(db, data)
        db.commit()
        fetched = services.get_article(db, article.id)
        assert fetched is not None
        assert fetched.id == article.id

    def test_get_article_by_slug(self, db):
        data = ArticleCreate(title="Slug Article", body="y")
        article = services.create_article(db, data)
        db.commit()
        fetched = services.get_article_by_slug(db, article.slug)
        assert fetched is not None
        assert fetched.slug == article.slug

    def test_get_nonexistent_returns_none(self, db):
        result = services.get_article(db, uuid.uuid4())
        assert result is None

    def test_list_articles_pagination(self, db):
        for i in range(5):
            services.create_article(db, ArticleCreate(title=f"Paginate {i}", body="body"))
        db.commit()
        total, items = services.list_articles(db, page=1, page_size=3)
        assert total >= 5
        assert len(items) == 3

    def test_list_articles_filter_status(self, db):
        services.create_article(db, ArticleCreate(title="Draft F", body="d", status="draft"))
        services.create_article(db, ArticleCreate(title="Published F", body="p", status="published"))
        db.commit()
        total, items = services.list_articles(db, status="published")
        assert all(a.status == "published" for a in items)

    def test_list_articles_search(self, db):
        services.create_article(db, ArticleCreate(title="Unique XYZ Title", body="body"))
        db.commit()
        total, items = services.list_articles(db, search="Unique XYZ")
        assert total >= 1
        assert any("XYZ" in a.title for a in items)

    def test_update_article(self, db):
        article = services.create_article(db, ArticleCreate(title="Old Title", body="body"))
        db.commit()
        updated = services.update_article(db, article, ArticleUpdate(title="New Title"))
        db.commit()
        assert updated.title == "New Title"

    def test_update_article_status_to_published(self, db):
        article = services.create_article(db, ArticleCreate(title="To Publish", body="body"))
        db.commit()
        assert article.published_at is None
        services.update_article(db, article, ArticleUpdate(status="published"))
        db.commit()
        assert article.published_at is not None

    def test_delete_article(self, db):
        article = services.create_article(db, ArticleCreate(title="Delete Me", body="body"))
        db.commit()
        article_id = article.id
        services.delete_article(db, article)
        db.commit()
        assert services.get_article(db, article_id) is None

    def test_increment_view_count(self, db):
        article = services.create_article(db, ArticleCreate(title="Views", body="body"))
        db.commit()
        services.increment_view_count(db, article)
        db.commit()
        assert article.view_count == 1

    def test_article_with_tags(self, db):
        tag = services.create_tag(db, TagCreate(name="TestTag123"))
        db.commit()
        article = services.create_article(
            db, ArticleCreate(title="Tagged Article", body="body", tag_ids=[tag.id])
        )
        db.commit()
        assert any(t.id == tag.id for t in article.tags)


# ---------------------------------------------------------------------------
# Comment tests
# ---------------------------------------------------------------------------


class TestComment:
    def test_add_comment(self, db):
        article = services.create_article(db, ArticleCreate(title="Comment Art", body="body"))
        db.commit()
        data = CommentCreate(author_name="Alice", body="Great article!")
        comment = services.add_comment(db, article, data)
        db.commit()
        assert comment.id is not None
        assert comment.is_approved is False

    def test_list_comments_approved_only(self, db):
        article = services.create_article(db, ArticleCreate(title="Comm List", body="b"))
        db.commit()
        services.add_comment(db, article, CommentCreate(author_name="A", body="Approved"))
        services.add_comment(db, article, CommentCreate(author_name="B", body="Pending"))
        db.commit()
        comments = services.list_comments(db, article.id, approved_only=True)
        assert len(comments) == 0  # none approved yet

    def test_list_all_comments(self, db):
        article = services.create_article(db, ArticleCreate(title="All Comments", body="b"))
        db.commit()
        services.add_comment(db, article, CommentCreate(author_name="A", body="c1"))
        db.commit()
        comments = services.list_comments(db, article.id, approved_only=False)
        assert len(comments) >= 1


# ---------------------------------------------------------------------------
# Rating tests
# ---------------------------------------------------------------------------


class TestRating:
    def test_rate_article(self, db):
        article = services.create_article(db, ArticleCreate(title="Rate Art", body="body"))
        db.commit()
        rating = services.rate_article(
            db, article, RatingCreate(session_key="sess-1", score=5)
        )
        db.commit()
        assert rating.score == 5

    def test_update_rating_idempotent(self, db):
        article = services.create_article(db, ArticleCreate(title="Re-rate", body="body"))
        db.commit()
        services.rate_article(db, article, RatingCreate(session_key="sess-2", score=3))
        db.commit()
        updated = services.rate_article(db, article, RatingCreate(session_key="sess-2", score=5))
        db.commit()
        assert updated.score == 5

    def test_rating_summary(self, db):
        article = services.create_article(db, ArticleCreate(title="Summary Rate", body="body"))
        db.commit()
        services.rate_article(db, article, RatingCreate(session_key="s1", score=4))
        services.rate_article(db, article, RatingCreate(session_key="s2", score=2))
        db.commit()
        summary = services.get_rating_summary(db, article.id)
        assert summary["count"] == 2
        assert summary["average"] == 3.0
