"""Mini-CMS Demonstration Application.

Showcases FeretUI CMS and Content Management capabilities:
- Native zero-dependency WYSIWYG editor (WYSIWYGField) for rich text content
- Editorial workflow stages with interactive pipeline (StatusBarField)
- Kanban editorial desk with drag-and-drop card movements (KResource)
- Relational categorization with Many2One and One2Many fields
- Reactive HTMX @onchange auto-slugification
- Category Stat / Smart buttons on form headers
- Article tagging with TagsField
- Starlette ASGI web server integration
"""

import os
import re
from typing import Any
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import InputRequired

from feretui import (
    FeretUI,
    Many2OneField,
    One2ManyField,
    Session,
    StatusBarField,
    TagsField,
    WYSIWYGField,
)
from feretui.contrib.sqla import SQLAlchemyResource
from feretui.ext.starlette import get_routes_for_feretui_client
from feretui.form import FeretUIForm, onchange
from feretui.resources.kanban import KResource

from .models import Article, Base, Category

DB_PATH = os.environ.get("FERETUI_CMS_DB", "sqlite:///mini_cms.db")
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(bind=engine)


def init_demo_db() -> None:
    """Create tables and seed initial CMS demo data if empty."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Category).limit(1)) is None:
            c1 = Category(
                name="Web Architecture",
                slug="web-architecture",
                description="Technical articles on modern web design, APIs, and micro-frameworks.",
            )
            c2 = Category(
                name="Product Guides",
                slug="product-guides",
                description="Practical tutorials, how-tos, and best practices for back-offices.",
            )
            c3 = Category(
                name="Company News",
                slug="company-news",
                description="Announcements, roadmap updates, and release notes.",
            )
            db.add_all([c1, c2, c3])
            db.flush()

            a1 = Article(
                title="Building Modern Back-Offices with FeretUI",
                slug="building-modern-back-offices-with-feretui",
                category_id=c1.id,
                category_name=c1.name,
                status="published",
                author="Sarah Connor",
                tags="python, htmx, architecture",
                summary="Why zero-JS architectures powered by HTMX and Python reduce maintenance costs.",
                content=(
                    "<h2>Why Zero-JS Back-Offices Matter</h2>"
                    "<p>Traditional single-page applications (SPAs) often introduce massive "
                    "complexity, build pipelines, and duplicate business logic. <strong>FeretUI</strong> "
                    "flips the script by pairing <em>Python</em> with <strong>HTMX</strong>.</p>"
                    "<blockquote>Simplicity is prerequisite for reliability. — Edsger W. Dijkstra</blockquote>"
                    "<h3>Core Benefits:</h3>"
                    "<ul>"
                    "<li><strong>100% Server-side validation</strong> via WTForms</li>"
                    "<li>Instant reactive recomputations with <code>@onchange</code></li>"
                    "<li>Accessible, responsive UI styled with Pico CSS v2</li>"
                    "</ul>"
                ),
            )
            a2 = Article(
                title="WYSIWYG Rich-Text Editing Without Node.js",
                slug="wysiwyg-rich-text-editing-without-nodejs",
                category_id=c2.id,
                category_name=c2.name,
                status="published",
                author="Alex Vance",
                tags="wysiwyg, cms, tutorial",
                summary="How FeretUI provides built-in rich text editing without external npm dependencies.",
                content=(
                    "<h2>Native HTML5 Contenteditable</h2>"
                    "<p>FeretUI includes a lightweight <code>WYSIWYGField</code> that integrates "
                    "directly with your forms.</p>"
                    "<h3>What's included in the toolbar:</h3>"
                    "<ul>"
                    "<li><strong>Text formatting:</strong> bold, italic, underline, strikethrough</li>"
                    "<li><strong>Block structures:</strong> headings (H1 to H3), paragraphs, quotes</li>"
                    "<li><strong>Lists:</strong> bullet points and numbered sequences</li>"
                    "<li><strong>Hyperlinks:</strong> quick link insertion and removal</li>"
                    "</ul>"
                    "<p>All edits synchronize seamlessly with a hidden <code>&lt;textarea&gt;</code>.</p>"
                ),
            )
            a3 = Article(
                title="Next-Gen Editorial Workflows with Kanban Boards",
                slug="next-gen-editorial-workflows-with-kanban-boards",
                category_id=c2.id,
                category_name=c2.name,
                status="review",
                author="Gordon Freeman",
                tags="editorial, kanban, workflow",
                summary="Streamlining article drafts through editorial review and publication stages.",
                content=(
                    "<h2>Visual Editorial Desks</h2>"
                    "<p>With FeretUI's <code>KResource</code>, your editorial team can manage "
                    "article lifecycles visually by dragging cards across workflow columns:</p>"
                    "<ol>"
                    "<li><strong>Draft:</strong> Initial authoring</li>"
                    "<li><strong>Under Review:</strong> Peer review and proofreading</li>"
                    "<li><strong>Published:</strong> Live on the website</li>"
                    "<li><strong>Archived:</strong> Deprecated or superseded content</li>"
                    "</ol>"
                ),
            )
            a4 = Article(
                title="FeretUI 2.0 Roadmap & Release Announcement",
                slug="feretui-2-0-roadmap-release-announcement",
                category_id=c3.id,
                category_name=c3.name,
                status="draft",
                author="Admin",
                tags="announcement, roadmap",
                summary="Sneak peek into upcoming features and community contributions.",
                content=(
                    "<h2>Welcome to the Future of FeretUI</h2>"
                    "<p>We are thrilled to unveil new capabilities including universal exports, "
                    "advanced One2Many sub-tables, and enhanced CMS widgets.</p>"
                ),
            )
            db.add_all([a1, a2, a3, a4])
            db.commit()


def get_category_choices() -> list[tuple[str, str]]:
    """Return available categories as (id, name) tuples for Select/Many2One."""
    with SessionLocal() as db:
        categories = db.scalars(select(Category).order_by(Category.name)).all()
        return [(str(c.id), c.name) for c in categories]


# ---------------------------------------------------------------------------
# FeretUI Application & Resources Setup
# ---------------------------------------------------------------------------

myferet = FeretUI(
    title="FeretUI Mini-CMS",
)


class CategoryForm(FeretUIForm):
    """Category form with embedded articles sub-table."""

    pk = HiddenField("ID")
    name = StringField("Category Name", validators=[InputRequired()])
    slug = StringField("Slug", validators=[InputRequired()])
    description = TextAreaField("Description")
    articles = One2ManyField(
        "Articles in this Category",
        columns=[
            ("title", "Title"),
            ("status", "Status"),
            ("author", "Author"),
        ],
        target_resource="articles",
    )


@myferet.register_resource()
class CategoryResource(SQLAlchemyResource):
    """Category management resource."""

    code = "categories"
    label = "Categories"
    model = Category
    session_factory = SessionLocal
    Form = CategoryForm
    menu_visibility = None
    page_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]

    class MetaViewRead:
        body_template_id = "view-sheet-readonly-form"

    class MetaViewEdit:
        body_template_id = "view-sheet-readwrite-form"

    def get_smart_buttons(
        self,
        form: FeretUIForm,
        feretui: FeretUI,  # noqa: ARG002
        session: Session,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Return smart stat buttons displayed at the top of category form."""
        articles_count = len(getattr(form.articles, "data", []) or [])
        return [
            {
                "label": "Articles",
                "count": articles_count,
                "icon": "ti ti-article",
                "url": "/?page=resource&resource=articles&view=list",
            },
        ]


class ArticleForm(FeretUIForm):
    """Article form with rich WYSIWYG editor, workflow pipeline, and tags."""

    pk = HiddenField("ID")
    title = StringField("Article Title", validators=[InputRequired()])
    slug = StringField("URL Slug", validators=[InputRequired()])
    category_id = Many2OneField(
        "Category",
        resource="categories",
        choices=get_category_choices,
        validators=[InputRequired()],
    )
    status = StatusBarField(
        "Editorial Status",
        choices=[
            ("draft", "Draft"),
            ("review", "Under Review"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        default="draft",
    )
    author = StringField("Author", default="Editor")
    tags = TagsField(
        "Tags",
        separator=",",
        default=["cms", "python"],
    )
    summary = TextAreaField("Summary / Excerpt")
    content = WYSIWYGField(
        "Article Body",
        min_height="350px",
        placeholder="Write your rich text article here...",
    )

    @onchange("title")
    def _on_title_change(self) -> None:
        """Automatically suggest a clean URL slug when title changes."""
        if self.title.data:
            clean = re.sub(r"[^\w\s-]", "", self.title.data.lower())
            self.slug.data = re.sub(r"[-\s]+", "-", clean).strip("-")


@myferet.register_resource()
class ArticleResource(KResource, SQLAlchemyResource):
    """Article resource supporting List, Kanban, and Sheet Form views."""

    code = "articles"
    label = "Articles"
    model = Article
    session_factory = SessionLocal
    Form = ArticleForm
    default_view = "kanban"
    menu_visibility = None
    page_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]

    class MetaViewKanban:
        column_field = "status"
        card_title_field = "title"
        card_body_fields = ["author", "category_name"]
        do_click_on_entry_redirect_to = "read"

    class MetaViewRead:
        body_template_id = "view-sheet-readonly-form"

    class MetaViewEdit:
        body_template_id = "view-sheet-readwrite-form"


# Navigation Menus
myferet.register_toolbar_left_menus([
    ArticleResource.menu,
    CategoryResource.menu,
])


def create_app() -> Starlette:
    """Build and return Starlette application."""
    init_demo_db()
    routes = get_routes_for_feretui_client(myferet, index_path="/")
    return Starlette(
        routes=routes,
        middleware=[
            Middleware(SessionMiddleware, secret_key="feretui-secret-key-cms-demo"),
        ],
    )


app = create_app()

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting FeretUI Mini-CMS at http://localhost:8000 ...")
    uvicorn.run("feretui.examples.mini_cms.app:app", host="0.0.0.0", port=8000, reload=True)
