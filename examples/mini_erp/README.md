# FeretUI Next-Gen Mini-ERP Demonstration

Welcome to the **FeretUI Mini-ERP** demonstration application. This realistic business application showcases the full suite of modern ERP capabilities introduced in FeretUI:

- **Semantic Modern UI**: Built with Pico CSS v2, responsive layouts, and modern color themes (Default, United, Flatly, Materia, Lux, Minty, Pulse, Darkly).
- **Kanban Board**: Drag-and-drop cards between stages (Draft -> In Progress -> Done -> Cancelled) powered by SortableJS with zero business logic in JavaScript.
- **Workflow Pipeline Widget**: Interactive `StatusBarField` / `StatusBarWidget` displayed on sales orders with active stage indicators.
- **Reactive Engine (`@onchange`)**: Real-time Python calculations via HTMX out-of-band updates (changing quantity or unit price automatically recalculates order total without full page reloads).
- **Universal Data Exports**: 1-click export of data to CSV and formatted Microsoft Excel (XLSX).
- **SQLAlchemy 2.0 ORM Integration**: Automatic LCRUD view generation, sorting, filtering, pagination, and persistence.
- **Starlette / FastAPI Async Web Framework**: Native ASGI routing and session management.

---

## 1. Quick Start

### Prerequisites
Make sure you are in your Python virtual environment where FeretUI is installed:

```bash
source ./venv/bin/activate
```

### Running the Application

Run the application with `uvicorn`:

```bash
uvicorn examples.mini_erp.app:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 2. Walkthrough & Features to Try

### 📋 1. Kanban Board (Orders)
1. Navigate to **Orders** from the top navbar.
2. Notice the columns: *Draft*, *In Progress*, *Done*, *Cancelled*.
3. Drag any order card from one column to another.
4. Refresh the page: the stage change was automatically persisted to SQLite in Python!
5. Double-click on any card to open its detail view.

### ⚡ 2. Reactive Calculation (`@onchange`)
1. Open an Order or click **Create** to create a new one.
2. Notice the **Status Bar** pipeline at the top of the form.
3. Change the **Quantity** or **Unit Price**:
   - As soon as focus leaves or changes, the **Total Amount** recalculates instantly via HTMX!
4. Zero JavaScript calculation code was written — all logic executes in Python:
   ```python
   @onchange("qty", "unit_price")
   def _recalc_total(self) -> None:
       q = int(self.qty.data or 0)
       p = float(self.unit_price.data or 0.0)
       self.total_amount.data = round(q * p, 2)
   ```

### 📊 3. Universal Exports (CSV & XLSX)
1. Go to **Customers** or **Products**.
2. Notice the **Export CSV** and **Export XLSX** buttons in the toolbar.
3. Click either button to download structured data formatted according to your active filters.

### 🔗 4. Relational Links (Many2One) & Embedded Sub-Tables (One2Many)
1. Open a **Customer** (e.g. *Acme Corporation*):
   - Notice the **Smart Button** at the top right showing the total order count (e.g. `[ 🛒 1 Orders ]`).
   - Notice the **Sales Orders** embedded table listing all orders for this customer with direct view links!
2. Open a **Sales Order** (e.g. *SO-2026-001*):
   - Look at the **Customer** field: rendered as a clickable Many2One link (`[ ↗ Acme Corporation ]`) in read mode and a select + jump button in edit mode.
   - Look at the **Order Lines** sub-table: dynamically lists line items with product descriptions, quantities, unit prices, and subtotals.
   - Notice how technical IDs are hidden and the order reference or partner name is displayed prominently in the sheet header!

### 🎨 5. Modern Sheet Form Templates & Dark Mode
1. Forms use modern ERP card layouts (``view-sheet-readonly-form`` & ``view-sheet-readwrite-form``) featuring:
   - Technical IDs (``pk`` / ``HiddenField``) hidden from display.
   - Responsive 2-column input grid (``.feretui-form-grid``).
   - Full-width sections for notes and x2many sub-tables.
2. In `app.py`, customize your theme:
   ```python
   myferet = FeretUI(title="Mini ERP", theme="materia")  # or flatly, lux, minty, pulse, darkly, united
   ```
3. Pico CSS automatically supports Dark Mode: toggle via system preferences or `session.color_scheme = "dark"`.

---

## 3. Project Structure

```text
examples/mini_erp/
├── app.py             # FeretUI setup, resources, and Starlette server
├── models.py          # SQLAlchemy 2.0 Declarative models
├── README.md          # Guide & walkthrough
└── test_mini_erp.py   # Automated integration test suite
```
