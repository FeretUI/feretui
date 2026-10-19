.. This file is a part of the FeretUI project
..
..    Copyright (C) 2026 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

How to Build a Modern CMS with FeretUI
======================================

FeretUI provides an exceptional foundation for building **Content Management Systems (CMS)**, blog engines, and editorial portals. 

Unlike traditional CMS stacks that require complex JavaScript build pipelines (Webpack, Vite, Node.js) or bloated third-party plugins, FeretUI offers a **100% pure Python** back-office:

* **Native WYSIWYG Rich-Text Editor**: Formatted content editing with zero external npm dependencies.
* **Visual Editorial Workflows**: Kanban board (drag-and-drop) and Status Bar pipelines for article lifecycle management (*Draft* → *Under Review* → *Published* → *Archived*).
* **Instant Reactivity with HTMX**: Auto-generate URL slugs from titles in real time using Python ``@onchange``.
* **Relational Categorization**: Seamless parent-child relationships with ``Many2OneField`` and embedded ``One2ManyField`` sub-tables.
* **Responsive Pico CSS v2 Theme**: Clean, accessible (RGAA 11.5 compliant) interface with built-in dark and light modes.

A complete runnable example is available in the repository under ``examples/mini_cms/``.

---

1. Architecture of a FeretUI CMS
--------------------------------

A typical CMS back-office in FeretUI is composed of four main layers:

.. list-table::
   :widths: 25 35 40
   :header-rows: 1

   * - Layer
     - FeretUI Component
     - Purpose
   * - **Data Models**
     - SQLAlchemy ORM
     - Persistent storage for categories, articles, authors, and tags.
   * - **Editorial Forms**
     - :class:`~feretui.form.FeretUIForm`, :class:`~feretui.form.WYSIWYGField`
     - Form validation, rich-text editing, tags, and reactive auto-slugification.
   * - **Editorial Desk**
     - :class:`~feretui.resources.kanban.KResource`
     - Visual editorial board grouping articles by publication stage with drag-and-drop.
   * - **Web Server**
     - Starlette / FastAPI
     - High-performance ASGI serving with sessions and routing.

---

2. Step 1: Defining Data Models
-------------------------------

Start by defining your SQLAlchemy models in ``models.py``. Here we define a ``Category`` and an ``Article``:

.. code-block:: python

    from sqlalchemy import ForeignKey, Integer, String, Text
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

    class Base(DeclarativeBase):
        pass

    class Category(Base):
        __tablename__ = "categories"

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
        description: Mapped[str] = mapped_column(Text, default="")

        articles: Mapped[list["Article"]] = relationship(
            "Article",
            back_populates="category",
            lazy="selectin",
        )

    class Article(Base):
        __tablename__ = "articles"

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        title: Mapped[str] = mapped_column(String(200), nullable=False)
        slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
        category_id: Mapped[int | None] = mapped_column(
            Integer,
            ForeignKey("categories.id"),
            nullable=True,
        )
        category_name: Mapped[str] = mapped_column(String(100), default="")
        status: Mapped[str] = mapped_column(String(30), default="draft")
        author: Mapped[str] = mapped_column(String(100), default="Editor")
        tags: Mapped[str] = mapped_column(String(200), default="")
        summary: Mapped[str] = mapped_column(Text, default="")
        content: Mapped[str] = mapped_column(Text, default="")

        category: Mapped[Category | None] = relationship(
            "Category",
            back_populates="articles",
            lazy="selectin",
        )

---

3. Step 2: Creating the Editorial Forms
---------------------------------------

The article form leverages FeretUI's specialized fields:

* :class:`~feretui.form.WYSIWYGField`: Native rich-text editor with formatting toolbar (Bold, Italic, Headings, Lists, Quotes, Links).
* :class:`~feretui.form.StatusBarField`: Workflow pipeline stage indicator.
* :class:`~feretui.form.TagsField`: Multi-value tag input.
* :func:`~feretui.form.onchange`: Automatically compute the URL slug whenever the title is typed.

.. code-block:: python

    import re
    from wtforms import HiddenField, StringField, TextAreaField
    from wtforms.validators import InputRequired
    from feretui.form import FeretUIForm, onchange
    from feretui import Many2OneField, One2ManyField, StatusBarField, TagsField, WYSIWYGField

    class ArticleForm(FeretUIForm):
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
        tags = TagsField("Tags", separator=",", default=["cms", "python"])
        summary = TextAreaField("Summary / Excerpt")
        content = WYSIWYGField(
            "Article Body",
            min_height="350px",
            placeholder="Write your formatted article here...",
        )

        @onchange("title")
        def _on_title_change(self) -> None:
            """Automatically slugify the title on user input."""
            if self.title.data:
                clean = re.sub(r"[^\w\s-]", "", self.title.data.lower())
                self.slug.data = re.sub(r"[-\s]+", "-", clean).strip("-")

---

4. Step 3: Setting Up Resources and Views
-----------------------------------------

Use :class:`~feretui.resources.kanban.KResource` for the articles so editorial staff can manage publication statuses via drag-and-drop:

.. code-block:: python

    from feretui import FeretUI
    from feretui.contrib.sqla import SQLAlchemyResource
    from feretui.resources.kanban import KResource

    myferet = FeretUI(title="My CMS Back-Office")

    @myferet.register_resource()
    class ArticleResource(KResource, SQLAlchemyResource):
        code = "articles"
        label = "Articles"
        model = Article
        session_factory = SessionLocal
        Form = ArticleForm
        default_view = "kanban"

        class MetaViewKanban:
            column_field = "status"
            card_title_field = "title"
            card_body_fields = ["author", "category_name"]
            do_click_on_entry_redirect_to = "read"

        class MetaViewRead:
            body_template_id = "view-sheet-readonly-form"

        class MetaViewEdit:
            body_template_id = "view-sheet-readwrite-form"

For categories, define a resource with a **Smart Button** showing the count of related articles and an embedded :class:`~feretui.form.One2ManyField`:

.. code-block:: python

    class CategoryForm(FeretUIForm):
        pk = HiddenField("ID")
        name = StringField("Category Name", validators=[InputRequired()])
        slug = StringField("Slug", validators=[InputRequired()])
        description = TextAreaField("Description")
        articles = One2ManyField(
            "Articles",
            columns=[("title", "Title"), ("status", "Status"), ("author", "Author")],
            target_resource="articles",
        )

    @myferet.register_resource()
    class CategoryResource(SQLAlchemyResource):
        code = "categories"
        label = "Categories"
        model = Category
        session_factory = SessionLocal
        Form = CategoryForm

        def get_smart_buttons(self, form, feretui, session):
            articles_count = len(getattr(form.articles, "data", []) or [])
            return [
                {
                    "label": "Articles",
                    "count": articles_count,
                    "icon": "ti ti-article",
                    "url": "/?page=resource&resource=articles&view=list",
                },
            ]

---

5. Step 4: Register Navigation and Web Server
---------------------------------------------

Register top toolbar menus and mount with Starlette:

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware
    from feretui.ext.starlette import get_routes_for_feretui_client

    myferet.register_toolbar_left_menus([
        ArticleResource.menu,
        CategoryResource.menu,
    ])

    routes = get_routes_for_feretui_client(myferet, index_path="/")
    app = Starlette(
        routes=routes,
        middleware=[
            Middleware(SessionMiddleware, secret_key="cms-secret-key"),
        ],
    )

---

6. Step 5: Public Front-End Integration
---------------------------------------

To display published articles to the public, query your SQLAlchemy database filtering by ``status == 'published'``.

Because :class:`~feretui.form.WYSIWYGField` stores clean, semantic HTML (paragraphs, headers, lists, quotes), rendering the article body in your public templates is straightforward:

In Jinja2 / Starlette template:

.. code-block:: html

    <article class="cms-article">
      <header>
        <h1>{{ article.title }}</h1>
        <div class="meta">By {{ article.author }} in {{ article.category_name }}</div>
      </header>
      <div class="content">
        {{ article.content | safe }}
      </div>
    </article>

In read-only mode within the FeretUI back-office, the formatted HTML is automatically previewed with full styling inside ``.feretui-wysiwyg-preview``.

---

7. Running the Mini-CMS Example
-------------------------------

The full source code is located in ``examples/mini_cms/``:

.. code-block:: bash

    cd examples/mini_cms
    python app.py

Then open your browser at ``http://localhost:8000``.
