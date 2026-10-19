"""Mini-ERP Demonstration Application.

Showcases FeretUI Next-Gen features:
- SQLAlchemy CRUD helpers with Many2One and One2Many relationships
- Embedded x2many sub-tables and Many2One navigation links
- Universal Exports (CSV, XLSX)
- Reactive HTMX @onchange calculations
- Kanban board with SortableJS drag-and-drop
- StatusBar pipeline widget
- Smart / Stat Buttons on form headers
- Pico CSS modern themes (United, Flatly, Materia, Lux, Minty, etc.)
- Starlette / FastAPI web server integration
"""

import os
from typing import Any
from markupsafe import Markup
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from wtforms import FloatField, HiddenField, StringField, TextAreaField
from wtforms.validators import InputRequired

from feretui import (
    FeretUI,
    Many2OneField,
    One2ManyField,
    Session,
    StatusBarField,
)
from feretui.contrib.sqla import SQLAlchemyResource
from feretui.ext.starlette import get_routes_for_feretui_client
from feretui.form import FeretUIForm, onchange
from feretui.resources.kanban import KResource

from .models import Base, Customer, Product, SaleOrder, SaleOrderLine

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
            db.flush()

            p1 = Product(name="Ergonomic Chair", sku="CHAIR-01", price=249.99, stock=45)
            p2 = Product(name="Standing Desk Pro", sku="DESK-02", price=599.00, stock=18)
            p3 = Product(name="USB-C Docking Station", sku="DOCK-03", price=129.50, stock=80)
            db.add_all([p1, p2, p3])
            db.flush()

            o1 = SaleOrder(
                order_ref="SO-2026-001",
                customer_id=c1.id,
                customer_name=c1.name,
                status="in_progress",
                total_amount=499.98,
                notes="Express shipping requested",
            )
            o2 = SaleOrder(
                order_ref="SO-2026-002",
                customer_id=c2.id,
                customer_name=c2.name,
                status="draft",
                total_amount=2995.00,
                notes="Quarterly refurbishment order",
            )
            o3 = SaleOrder(
                order_ref="SO-2026-003",
                customer_id=c3.id,
                customer_name=c3.name,
                status="done",
                total_amount=1295.00,
                notes="Delivered to HQ",
            )
            db.add_all([o1, o2, o3])
            db.flush()

            l1 = SaleOrderLine(
                order_id=o1.id,
                product_id=p1.id,
                product_name=p1.name,
                qty=2,
                unit_price=249.99,
                subtotal=499.98,
            )
            l2 = SaleOrderLine(
                order_id=o2.id,
                product_id=p2.id,
                product_name=p2.name,
                qty=5,
                unit_price=599.00,
                subtotal=2995.00,
            )
            l3 = SaleOrderLine(
                order_id=o3.id,
                product_id=p3.id,
                product_name=p3.name,
                qty=10,
                unit_price=129.50,
                subtotal=1295.00,
            )
            db.add_all([l1, l2, l3])
            db.commit()


def get_customer_choices() -> list[tuple[str, str]]:
    """Return available customers as (id, name) tuples for Select/Many2One."""
    with SessionLocal() as db:
        customers = db.scalars(select(Customer).order_by(Customer.name)).all()
        return [(str(c.id), c.name) for c in customers]


# ---------------------------------------------------------------------------
# FeretUI Application & Resources Setup
# ---------------------------------------------------------------------------

myferet = FeretUI(
    title="FeretUI Next-Gen Mini ERP",
)


class CustomerForm(FeretUIForm):
    """Customer partner form with contact info and embedded orders sub-table."""

    pk = HiddenField("ID")
    name = StringField("Customer Name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired()])
    phone = StringField("Phone Number")
    city = StringField("City")
    orders = One2ManyField(
        "Sales Orders",
        columns=[
            ("order_ref", "Order Ref"),
            ("status", "Status"),
            ("total_amount", "Total ($)"),
        ],
        target_resource="orders",
    )


@myferet.register_resource()
class CustomerResource(SQLAlchemyResource):
    """Customer management resource."""

    code = "customers"
    label = "Customers"
    model = Customer
    session_factory = SessionLocal
    Form = CustomerForm
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
        """Return smart stat buttons displayed at the top of customer form."""
        order_count = len(getattr(form.orders, "data", []) or [])
        return [
            {
                "label": "Orders",
                "count": order_count,
                "icon": "ti ti-shopping-cart",
                "url": "/?page=resource&resource=orders&view=list",
            },
        ]


@myferet.register_resource()
class ProductResource(SQLAlchemyResource):
    """Product catalog management resource."""

    code = "products"
    label = "Products"
    model = Product
    session_factory = SessionLocal
    menu_visibility = None
    page_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]

    class MetaViewRead:
        body_template_id = "view-sheet-readonly-form"

    class MetaViewEdit:
        body_template_id = "view-sheet-readwrite-form"


class OrderForm(FeretUIForm):
    """Sales order form with status pipeline, Many2One, and x2many sub-table."""

    pk = HiddenField("ID")
    order_ref = StringField("Order Reference", validators=[InputRequired()])
    customer_id = Many2OneField(
        "Customer",
        resource="customers",
        choices=get_customer_choices,
        validators=[InputRequired()],
    )
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
    lines = One2ManyField(
        "Order Lines",
        columns=[
            ("product_name", "Product"),
            ("qty", "Qty"),
            ("unit_price", "Unit Price ($)"),
            ("subtotal", "Subtotal ($)"),
        ],
        target_resource="products",
    )
    total_amount = FloatField("Total Amount ($)", default=0.0)
    notes = TextAreaField("Notes")

    @onchange("customer_id")
    def _on_customer_change(self) -> None:
        """Reactive update of customer details."""
        cid = self.customer_id.data
        if cid:
            with SessionLocal() as db:
                c = db.scalar(select(Customer).where(Customer.id == int(cid)))
                if c:
                    self.notes.data = f"Default Terms for {c.name} ({c.city})"


@myferet.register_resource()
class OrderResource(KResource, SQLAlchemyResource):
    """Sales Order resource supporting List, Kanban, and Sheet Form views."""

    code = "orders"
    label = "Orders"
    model = SaleOrder
    session_factory = SessionLocal
    Form = OrderForm
    default_view = "kanban"
    menu_visibility = None
    page_visibility = None

    class MetaViewList:
        enable_export = True
        export_formats = ["csv", "xlsx"]

    class MetaViewKanban:
        column_field = "status"
        card_title_field = "order_ref"
        card_body_fields = ["customer_name", "total_amount"]
        do_click_on_entry_redirect_to = "read"

    class MetaViewRead:
        body_template_id = "view-sheet-readonly-form"

    class MetaViewEdit:
        body_template_id = "view-sheet-readwrite-form"


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
