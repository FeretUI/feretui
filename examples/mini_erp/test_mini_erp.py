"""Automated tests for Mini-ERP demonstration application."""

import pytest
from multidict import MultiDict
from sqlalchemy import select
from starlette.testclient import TestClient

from feretui.context import cvar_feretui, cvar_request
from feretui.request import Request
from feretui.session import Session

from .app import (
    Customer,
    OrderForm,
    SessionLocal,
    app,
    init_demo_db,
    myferet,
)
from .models import SaleOrder


class TestMiniERP:
    """Test suite for Mini-ERP example."""

    @pytest.fixture(autouse=True)
    def setup_db(self) -> None:
        init_demo_db()

    def test_resources_registered(self) -> None:
        """Verify all resources are registered in FeretUI."""
        assert "customers" in myferet.resources
        assert "products" in myferet.resources
        assert "orders" in myferet.resources

    def test_order_onchange_customer(self) -> None:
        """Verify @onchange updates notes based on selected customer."""
        cvar_feretui.set(myferet)
        cvar_request.set(Request(Session()))
        with SessionLocal() as db:
            customer = db.scalar(select(Customer).limit(1))
            assert customer is not None
            cid = str(customer.id)

        form = OrderForm(MultiDict([("customer_id", cid)]))
        modified = form.process_onchange("customer_id")
        assert "notes" in modified
        assert customer.name in form.notes.data

    def test_kanban_move_card_db_update(self) -> None:
        """Verify move_card updates order status in database."""
        with SessionLocal() as db:
            order = db.scalar(select(SaleOrder).limit(1))
            assert order is not None
            oid = str(order.id)

        res = myferet.resources["orders"]
        res.move_card(oid, "cancelled")

        with SessionLocal() as db:
            refreshed = db.scalar(select(SaleOrder).where(SaleOrder.id == int(oid)))
            assert refreshed.status == "cancelled"

    def test_customer_read_view_smart_buttons_and_orders(self) -> None:
        """Verify Customer read view displays smart buttons and orders table."""
        client = TestClient(app)
        with SessionLocal() as db:
            customer = db.scalar(select(Customer).limit(1))
            assert customer is not None
            cid = str(customer.id)

        response = client.get(f"/?page=resource&resource=customers&view=read&pk={cid}")
        assert response.status_code == 200
        # Verify smart button
        assert "feretui-smart-button" in response.text
        assert "Orders" in response.text
        # Verify One2Many table for orders
        assert "feretui-one2many-table" in response.text
        assert "Sales Orders" in response.text
        assert "SO-2026-001" in response.text

    def test_order_read_view_many2one_link_and_lines(self) -> None:
        """Verify Order read view renders Many2One customer link and order lines table."""
        client = TestClient(app)
        with SessionLocal() as db:
            order = db.scalar(select(SaleOrder).limit(1))
            assert order is not None
            oid = str(order.id)

        response = client.get(f"/?page=resource&resource=orders&view=read&pk={oid}")
        assert response.status_code == 200
        # Verify Many2One link to customer
        assert "feretui-many2one-link" in response.text
        assert "Acme Corporation" in response.text
        assert "/?page=resource&resource=customers&view=read&pk=" in response.text
        # Verify One2Many order lines table
        assert "feretui-one2many-table" in response.text
        assert "Order Lines" in response.text
        assert "Ergonomic Chair" in response.text
        # Verify ID text box is not visible in the sheet
        assert 'name="pk"' not in response.text

    def test_app_index_client(self) -> None:
        """Verify Starlette test client renders FeretUI ERP index."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "Customers" in response.text
        assert "Products" in response.text
        assert "Orders" in response.text
