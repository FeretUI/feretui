# FeretUI Mini-CMS Demonstration

Welcome to the **FeretUI Mini-CMS** demonstration application. This application showcases how to build a complete Content Management System (CMS) and editorial back-office with FeretUI using Python, HTMX, and Pico CSS.

---

## 1. Features Showcased

- **Native WYSIWYG Rich-Text Editor (`WYSIWYGField`)**:
  - Full-featured formatting toolbar: Bold, Italic, Underline, Strikethrough.
  - Headings (H1 to H3), Paragraphs, Blockquotes, and Preformatted Code.
  - Bullet and numbered lists.
  - Hyperlinks insertion and removal.
  - Zero external npm / Node.js runtime dependencies; uses native HTML5 contenteditable styled with Pico CSS v2 and Tabler icons.
  - Seamless synchronization with an underlying `<textarea>` for standard form POST and HTMX triggers.
  - Read-only preview container with formatted HTML rendering.

- **Editorial Workflow Pipeline (`StatusBarField`)**:
  - Visual status stages: *Draft* → *Under Review* → *Published* → *Archived*.
  - Step progression indicators matching current stage with accessibility ARIA markup.

- **Editorial Kanban Desk (`KResource`)**:
  - Interactive board grouping articles by publication status.
  - Drag-and-drop cards across workflow stages powered by SortableJS.
  - Automatic Python server-side state persistence without custom JavaScript.

- **Relational Data Modeling**:
  - Categories with embedded articles sub-table via `One2ManyField`.
  - Articles linked to Categories via `Many2OneField` with clickable navigation.
  - Smart / Stat buttons displaying article counts on category headers.

- **Reactive Server-Side Intelligence (`@onchange`)**:
  - Real-time slug auto-generation when entering or updating article titles.

- **Tagging System (`TagsField`)**:
  - Multi-tag badges for articles (e.g. `cms, python, architecture`).

---

## 2. Quick Start

### Prerequisites
Make sure you are in your Python virtual environment where FeretUI is installed:

```bash
source ./venv/bin/activate
```

### Running the Application

Run the application with `uvicorn`:

```bash
uvicorn examples.mini_cms.app:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 3. Walkthrough & Features to Try

### ✍️ 1. WYSIWYG Article Editor
1. Click on **Articles** in the top navigation bar.
2. Click **Create** or open an existing article (e.g. *Building Modern Back-Offices with FeretUI*).
3. Switch to edit mode by clicking the **Edit** button.
4. Try typing text into the **Article Body** editor:
   - Select text and apply formatting (**Bold**, *Italic*, Headings, Quotes, Lists).
   - Insert links with the Link tool.
5. Notice the **URL Slug** field automatically populates from the **Article Title** via `@onchange`.
6. Save the article: the content is saved as clean, semantic HTML in the database.
7. In **Read** view, notice the article body displays as a clean formatted HTML preview.

### 📋 2. Editorial Kanban Desk
1. Navigate to **Articles** (default view is Kanban).
2. The columns represent: *Draft*, *Under Review*, *Published*, and *Archived*.
3. Drag any article card from *Draft* to *Under Review* or *Published*.
4. Refresh the page: the status change was automatically persisted to SQLite in Python!
5. Click on any card to view its full details.

### 🏷️ 3. Categories and One2Many Sub-Tables
1. Click on **Categories** in the navigation bar.
2. Open *Web Architecture* or *Product Guides*.
3. Notice the **Stat Button** at the top showing the number of articles in this category.
4. Scroll down to see the embedded **Articles** sub-table with direct links to view or edit each related article.

---

## 4. Code Architecture

```
examples/mini_cms/
├── __init__.py        # Package initializer
├── models.py          # SQLAlchemy Category & Article models
├── app.py             # FeretUI resources, forms, and Starlette ASGI app
├── test_mini_cms.py   # Automated pytest test suite
└── README.md          # Documentation
```
