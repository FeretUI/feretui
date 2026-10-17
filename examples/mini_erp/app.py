"""Mini-ERP Demonstration Application.

Showcases FeretUI Next-Gen features:
- SQLAlchemy CRUD helpers
- Universal Exports (CSV, XLSX)
- Reactive HTMX @onchange calculations
- Kanban board with SortableJS drag-and-drop
- StatusBar pipeline widget
- Pico CSS modern themes (United, Flatly, Materia, Lux, Minty, etc.)
- Starlette / FastAPI web server integration
"""

import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from wtforms import FloatField, IntegerField, StringField, TextAreaField
from wtforms.validators import InputRequired

from feretui import (
    FeretUI,
)
from feretui.contrib.sqla import SQLAlchemyResource
from feretui.ext.starlette import get_routes_for_feretui_client
from feretui.form import FeretUIForm, StatusBarField, onchange
from feretui.resources.kanban import KResource

from .models import Base, Customer, Product, SaleOrder

DB_PATH = os.environ.get("FERETUI_ERP_DB", "sqlite:///mini_erp.db")
engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(bind=engine)


def init_demo_db() -> None:
    """Create tables and seed initial demo data if empty."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Customer).limit(1)) is None:
            c1 = Customer(
                name="Acme Corporation",
                email="contact@acme.com",
                phone="+1 555-0199",
                city="New York",
            )
            c2 = Customer(
                name="Globex Industries",
                email="sales@globex.com",
                phone="+33 1 42 68 00 00",
                city="Paris",
            )
            c3 = Customer(
                name="Soylent Corp",
                email="info@soylent.com",
                phone="+44 20 7946 0912",
                city="London",
            )
            db.add_all([c1, c2, c3])

            p1 = Product(name="Ergonomic Chair", sku="CHAIR-01", price=249.99, stock=45)
            p2 = Product(name="Standing Desk Pro", sku="DESK-02", price=599.00, stock=18)
            p3 = Product(name="USB-C Docking Station", sku="DOCK-03", price=129.50, stock=80)
            db.add_all([p1, p2, p3])

            o1 = SaleOrder(
                order_ref="SO-2026-001",
                customer_name="Acme Corporation",
                status="in_progress",
                qty=2,
                unit_price=249.99,
                total_amount=499.98,
                notes="Express shipping requested",
            )
            o2 = SaleOrder(
                order_ref="SO-2026-002",
                customer_name="Globex Industries",
                status="draft",
                qty=5,
                unit_price=599.00,
                total_amount=2995.00,
                notes="Quarterly refurbishment order",
            )
            o3 = SaleOrder(
                order_ref="SO-2026-003",
                customer_name="Soylent Corp",
                status="done",
                qty=10,
                unit_price=129.50,
                total_amount=1295.00,
                notes="Delivered to HQ",
            )
            db.add_all([o1, o2, o3])
            db.commit()


# ---------------------------------------------------------------------------
# FeretUI Application & Resources Setup
# ---------------------------------------------------------------------------

myferet = FeretUI(
    title="FeretUI Next-Gen Mini ERP",
)


@myferet.register_resource()
class CustomerResource(SQLAlchemyResource):
    """Customer management resource."""

    code = "customers"
    label = "Customers"
    model = Customer
    session_factory = SessionLocal
    menu_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]


@myferet.register_resource()
class ProductResource(SQLAlchemyResource):
    """Product catalog management resource."""

    code = "products"
    label = "Products"
    model = Product
    session_factory = SessionLocal
    menu_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]


class OrderForm(FeretUIForm):
    """Sales order form with status pipeline and reactive onchange."""

    pk = StringField("ID")
    order_ref = StringField("Order Reference", validators=[InputRequired()])
    customer_name = StringField("Customer Name", validators=[InputRequired()])
    status = StatusBarField(
        "Workflow Status",
        choices=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    qty = IntegerField("Quantity", default=1, validators=[InputRequired()])
    unit_price = FloatField("Unit Price ($)", default=0.0, validators=[InputRequired()])
    total_amount = FloatField("Total Amount ($)", default=0.0)
    notes = TextAreaField("Notes")

    @onchange("qty", "unit_price")
    def _recalc_total(self) -> None:
        """Reactive calculation of total order amount."""
        q = int(self.qty.data or 0)
        p = float(self.unit_price.data or 0.0)
        self.total_amount.data = round(q * p, 2)


@myferet.register_resource()
class OrderResource(KResource, SQLAlchemyResource):
    """Sales Order resource supporting List, Kanban, and Form views."""

    code = "orders"
    label = "Orders"
    model = SaleOrder
    session_factory = SessionLocal
    Form = OrderForm
    default_view = "kanban"
    menu_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]

    class MetaViewKanban:
        column_field = "status"
        card_title_field = "order_ref"
        card_body_fields = ["customer_name", "total_amount"]
        do_click_on_entry_redirect_to = "read"


# Toolbar Navigation
myferet.register_toolbar_left_menus([
    CustomerResource.menu,
    ProductResource.menu,
    OrderResource.menu,
])


def create_app() -> Starlette:
    """Build and return Starlette application."""
    init_demo_db()
    routes = get_routes_for_feretui_client(myferet, index_path="/")
    return Starlette(
        routes=routes,
        middleware=[
            Middleware(SessionMiddleware, secret_key="feretui-secret-key-erp-demo"),
        ],
    )


app = create_app()

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting FeretUI Mini-ERP at http://localhost:8000 ...")
    uvicorn.run("feretui.examples.mini_erp.app:app", host="0.0.0.0", port=8000, reload=True)
