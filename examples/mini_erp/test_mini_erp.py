"""Automated tests for Mini-ERP demonstration application."""

import pytest
from multidict import MultiDict
from sqlalchemy import select
from starlette.testclient import TestClient

from feretui.context import cvar_feretui, cvar_request
from feretui.request import Request
from feretui.session import Session

from .app import (
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

    def test_order_onchange_recalc(self) -> None:
        """Verify @onchange recalculates total amount in OrderForm."""
        cvar_feretui.set(myferet)
        cvar_request.set(Request(Session()))
        form = OrderForm(MultiDict([("qty", "3"), ("unit_price", "150.0")]))
        modified = form.process_onchange("qty")
        assert "total_amount" in modified
        assert form.total_amount.data == 450.0

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

    def test_app_index_client(self) -> None:
        """Verify Starlette test client renders FeretUI ERP index."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "Customers" in response.text
        assert "Products" in response.text
        assert "Orders" in response.text
