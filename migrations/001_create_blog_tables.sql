-- Migration: 001_create_blog_tables.sql
-- Creates blog module tables: categories, tags, articles, article_tags, comments.

-- Blog Categories
CREATE TABLE IF NOT EXISTS blog_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    slug        VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_blog_categories_slug ON blog_categories (slug);

-- Blog Tags
CREATE TABLE IF NOT EXISTS blog_tags (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(100) NOT NULL UNIQUE,
    slug       VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active  BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_blog_tags_slug ON blog_tags (slug);

-- Blog Articles
CREATE TABLE IF NOT EXISTS blog_articles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(500) NOT NULL,
    slug        VARCHAR(600) NOT NULL UNIQUE,
    content     TEXT NOT NULL,
    excerpt     VARCHAR(1000),
    cover_image VARCHAR(500),
    author      VARCHAR(200) NOT NULL DEFAULT 'Jenan BIZ AI',
    status      VARCHAR(50)  NOT NULL DEFAULT 'draft',
    views       INTEGER NOT NULL DEFAULT 0,
    likes       INTEGER NOT NULL DEFAULT 0,
    published_at TIMESTAMPTZ,
    category_id UUID REFERENCES blog_categories(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_blog_articles_slug       ON blog_articles (slug);
CREATE INDEX IF NOT EXISTS ix_blog_articles_status     ON blog_articles (status);
CREATE INDEX IF NOT EXISTS ix_blog_articles_category   ON blog_articles (category_id);

-- Article ↔ Tag (many-to-many)
CREATE TABLE IF NOT EXISTS blog_article_tags (
    article_id UUID NOT NULL REFERENCES blog_articles(id) ON DELETE CASCADE,
    tag_id     UUID NOT NULL REFERENCES blog_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- Blog Comments
CREATE TABLE IF NOT EXISTS blog_comments (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id   UUID NOT NULL REFERENCES blog_articles(id) ON DELETE CASCADE,
    author_name  VARCHAR(200) NOT NULL,
    author_email VARCHAR(200),
    content      TEXT NOT NULL,
    is_approved  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active    BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS ix_blog_comments_article ON blog_comments (article_id);
