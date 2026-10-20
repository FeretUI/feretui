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
        assert "/?page=resource&amp;resource=customers&amp;view=read&amp;pk=" in response.text
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

    def test_one2many_goto_navigation(self) -> None:
        """Verify One2Many link points to action/goto with #feretui-body target and returns clean fragment."""
        client = TestClient(app)
        with SessionLocal() as db:
            order = db.scalar(select(SaleOrder).limit(1))
            assert order is not None
            oid = str(order.id)

        response = client.get(f"/?page=resource&resource=orders&view=read&pk={oid}")
        assert response.status_code == 200
        assert 'hx-target="#feretui-body"' in response.text
        assert 'hx-swap="innerHTML"' in response.text
        assert "/feretui/action/goto?page=resource&amp;resource=products&amp;view=read&amp;pk=" in response.text

        # Now simulate HTMX following the link to view the product
        goto_resp = client.get(
            "/feretui/action/goto?page=resource&resource=products&view=read&pk=1",
            headers={"HX-Request": "true"},
        )
        assert goto_resp.status_code == 200
        # Must return ONLY the resource fragment, NOT a full HTML page with duplicate navbar/footer
        assert "<!DOCTYPE html>" not in goto_resp.text
        assert "<feretui-html>" not in goto_resp.text
        assert "<header" not in goto_resp.text
        assert "feretui-client-footer" not in goto_resp.text
        assert 'id="resource-products"' in goto_resp.text
        assert "HX-Push-Url" in goto_resp.headers
        assert goto_resp.headers["HX-Push-Url"] == "/?page=resource&resource=products&view=read&pk=1"

    def test_view_switcher_navigation(self) -> None:
        """Verify view switcher buttons allow toggling between Kanban and List views."""
        client = TestClient(app)
        # Default view for orders is kanban
        resp = client.get("/?page=resource&resource=orders&view=kanban")
        assert resp.status_code == 200
        assert "feretui-view-switcher" in resp.text
        assert "ti ti-layout-kanban" in resp.text
        assert "ti ti-list" in resp.text

        # List view also has the switcher
        resp_list = client.get("/?page=resource&resource=orders&view=list")
        assert resp_list.status_code == 200
        assert "feretui-view-switcher" in resp_list.text
        # List view also displays the Quick Creation modal action
        assert "New Customer" in resp_list.text
        assert 'hx-target="#feretui-modal-stack"' in resp_list.text

        # List view displays quick filters
        assert "feretui-quick-filters" in resp_list.text
        assert "In Progress" in resp_list.text
        assert "Done" in resp_list.text
        assert "filter[status]=in_progress" in resp_list.text

        # Test modal endpoint directly
        modal_resp = client.get(
            "/feretui/action/modal?resource=customers&view=create&title=Quick+Add+Customer&modal_size=normal"
        )
        assert modal_resp.status_code == 200
        assert '<dialog class="feretui-modal"' in modal_resp.text
        assert "Quick Add Customer" in modal_resp.text
        assert "Cancel" in modal_resp.text

    def test_order_chatter(self) -> None:
        """Verify chatter is rendered on order form and new notes can be posted."""
        client = TestClient(app)
        with SessionLocal() as db:
            order = db.scalar(select(SaleOrder).limit(1))
            assert order is not None
            oid = str(order.id)

        order_res = myferet.get_resource("orders")
        order_res.add_chatter_message(
            oid,
            "Order confirmed and sent to warehouse.",
            author="Alice Smith",
            msg_type="note",
        )

        # Read view includes chatter and pre-seeded notes
        resp = client.get(f"/?page=resource&resource=orders&view=read&pk={oid}")
        assert resp.status_code == 200
        assert "feretui-chatter" in resp.text
        assert "Order confirmed and sent to warehouse." in resp.text
        assert "Alice Smith" in resp.text

        # Post a new chatter note
        post_resp = client.post(
            f"/feretui/action/resource?resource=orders&action=chatter_post&pk={oid}",
            data={"chatter_body": "Payment received by wire transfer."},
        )
        assert post_resp.status_code == 200
        assert "Payment received by wire transfer." in post_resp.text
        assert "feretui-chatter-thread" in post_resp.text

    def test_orders_graph_view(self) -> None:
        """Verify Graph view renders analytics SVG and pivot table for orders."""
        client = TestClient(app)
        resp = client.get("/?page=resource&resource=orders&view=graph")
        assert resp.status_code == 200
        assert "feretui-graph-view" in resp.text
        assert "feretui-chart-svg" in resp.text
        assert "feretui-pivot-table" in resp.text
        assert "Bar" in resp.text
        assert "Line" in resp.text
        assert "Pie" in resp.text

    def test_orders_search_and_group_by(self) -> None:
        """Verify Control Panel search and dynamic group by on orders."""
        client = TestClient(app)

        # 1. Real-time search query
        resp_search = client.get("/?page=resource&resource=orders&view=list&search=SO-2026-001")
        assert resp_search.status_code == 200
        assert "SO-2026-001" in resp_search.text
        assert "SO-2026-002" not in resp_search.text

        # 2. Dynamic group by
        resp_gb = client.get("/?page=resource&resource=orders&view=list&group_by=status")
        assert resp_gb.status_code == 200
        assert "feretui-group-header" in resp_gb.text
        assert "draft" in resp_gb.text
        assert "done" in resp_gb.text

    def test_orders_batch_wizard_action(self) -> None:
        """Verify Batch Wizard execution cancels selected orders."""
        client = TestClient(app)

        # 1. Order list displays batch action
        resp_list = client.get("/?page=resource&resource=orders&view=list")
        assert resp_list.status_code == 200
        assert "Batch Cancel" in resp_list.text
        assert 'hx-include="closest form"' in resp_list.text

        # 2. Open wizard modal
        open_resp = client.get(
            "/feretui/action/wizard?wizard=batch_cancel_orders&active_ids=1"
        )
        assert open_resp.status_code == 200
        assert "Batch Cancel Orders" in open_resp.text
        assert "Cancellation requested for 1 order(s)" in open_resp.text

        # 3. Submit wizard form
        submit_resp = client.post(
            "/feretui/action/resource?resource=batch_cancel_orders&action=wizard_execute",
            data={
                "active_ids": "1",
                "reason": "Customer changed mind",
            },
        )
        assert submit_resp.status_code == 200
        assert "<!-- modal-closed -->" in submit_resp.text
        assert "closeModal" in submit_resp.headers.get("HX-Trigger", "")

        # 4. Verify order 1 is cancelled in DB
        with SessionLocal() as db:
            o1 = db.scalar(select(SaleOrder).where(SaleOrder.id == 1))
            assert o1 is not None
            assert o1.status == "cancelled"
            assert "Customer changed mind" in (o1.notes or "")

    def test_products_grid_view_and_progress_bar(self) -> None:
        """Verify Products Grid card view and ProgressBar stock indicator."""
        client = TestClient(app)

        # 1. Grid view renders card mosaic and items
        resp_grid = client.get("/?page=resource&resource=products&view=grid")
        assert resp_grid.status_code == 200
        assert "feretui-grid-view" in resp_grid.text
        assert "feretui-cards-grid" in resp_grid.text
        assert "feretui-grid-card" in resp_grid.text
        assert "Ergonomic Chair" in resp_grid.text
        assert "CHAIR-01" in resp_grid.text
        assert "ti-layout-grid" in resp_grid.text
        assert "ti-list" in resp_grid.text


        # 2. List view renders ProgressBarField in table row
        resp_list = client.get("/?page=resource&resource=products&view=list")
        assert resp_list.status_code == 200
        assert "<progress" in resp_list.text
        assert 'value="45.0"' in resp_list.text
        assert "45%" in resp_list.text





