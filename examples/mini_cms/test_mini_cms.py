"""Automated tests for Mini-CMS demonstration application."""

import pytest
from multidict import MultiDict
from sqlalchemy import select
from starlette.testclient import TestClient

from feretui.context import cvar_feretui, cvar_request
from feretui.request import Request
from feretui.session import Session

from .app import (
    Article,
    ArticleForm,
    Base,
    Category,
    SessionLocal,
    app,
    engine,
    init_demo_db,
    myferet,
)


class TestMiniCMS:
    """Test suite for Mini-CMS example."""

    @pytest.fixture(autouse=True)
    def setup_db(self) -> None:
        Base.metadata.drop_all(engine)
        init_demo_db()

    def test_resources_registered(self) -> None:
        """Verify CMS resources are registered in FeretUI."""
        assert "categories" in myferet.resources
        assert "articles" in myferet.resources

    def test_article_slug_onchange(self) -> None:
        """Verify @onchange generates clean URL slug from title."""
        cvar_feretui.set(myferet)
        cvar_request.set(Request(Session()))

        form = ArticleForm(MultiDict([("title", "My New Incredible CMS Article! 2026")]))
        modified = form.process_onchange("title")
        assert "slug" in modified
        assert form.slug.data == "my-new-incredible-cms-article-2026"

    def test_kanban_move_article_status(self) -> None:
        """Verify move_card updates article publication status in database."""
        with SessionLocal() as db:
            article = db.scalar(select(Article).where(Article.status == "draft").limit(1))
            assert article is not None
            aid = str(article.id)

        res = myferet.resources["articles"]
        res.move_card(aid, "published")

        with SessionLocal() as db:
            refreshed = db.scalar(select(Article).where(Article.id == int(aid)))
            assert refreshed.status == "published"

    def test_category_read_view_smart_buttons_and_articles(self) -> None:
        """Verify Category read view displays smart buttons and articles table."""
        client = TestClient(app)
        with SessionLocal() as db:
            cat = db.scalar(select(Category).limit(1))
            assert cat is not None
            cid = str(cat.id)

        response = client.get(f"/?page=resource&resource=categories&view=read&pk={cid}")
        assert response.status_code == 200
        # Verify smart button
        assert "feretui-smart-button" in response.text
        assert "Articles" in response.text
        # Verify One2Many table for articles
        assert "feretui-one2many-table" in response.text
        assert "Articles in this Category" in response.text

    def test_article_read_view_wysiwyg_preview(self) -> None:
        """Verify Article read view renders WYSIWYG preview with formatted HTML."""
        client = TestClient(app)
        with SessionLocal() as db:
            article = db.scalar(select(Article).limit(1))
            assert article is not None
            aid = str(article.id)

        response = client.get(f"/?page=resource&resource=articles&view=read&pk={aid}")
        assert response.status_code == 200
        # Verify preview container and safe rendered HTML tags
        assert "feretui-wysiwyg-preview" in response.text
        assert "<h2>" in response.text or "<p>" in response.text
        # Verify status pipeline
        assert "feretui-status-bar" in response.text
        # Verify Many2One category link
        assert "feretui-many2one-link" in response.text

    def test_article_edit_view_wysiwyg_editor(self) -> None:
        """Verify Article edit view renders WYSIWYG editor container and toolbar."""
        client = TestClient(app)
        with SessionLocal() as db:
            article = db.scalar(select(Article).limit(1))
            assert article is not None
            aid = str(article.id)

        response = client.get(f"/?page=resource&resource=articles&view=edit&pk={aid}")
        assert response.status_code == 200
        assert "feretui-wysiwyg-container" in response.text
        assert "feretui-wysiwyg-toolbar" in response.text
        assert 'data-command="bold"' in response.text
        assert 'data-command="italic"' in response.text
        assert 'data-command="createLink"' in response.text
        assert "feretui-wysiwyg-editor" in response.text
        assert "feretui-wysiwyg-textarea" in response.text

    def test_app_index_client(self) -> None:
        """Verify Starlette test client renders FeretUI CMS home."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "Articles" in response.text
        assert "Categories" in response.text
