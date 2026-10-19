"""SQLAlchemy models for the Mini-ERP demonstration application."""

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for Mini-ERP models."""


class Customer(Base):
    """Customer partner model."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), default="")
    city: Mapped[str] = mapped_column(String(50), default="")

    orders: Mapped[list["SaleOrder"]] = relationship(
        "SaleOrder",
        back_populates="customer",
        lazy="selectin",
    )


class Product(Base):
    """Product catalog model."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, default=0)


class SaleOrder(Base):
    """Sales order with workflow states and calculated totals."""

    __tablename__ = "sale_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True,
    )
    customer_name: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(30), default="draft")
    qty: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")

    customer: Mapped[Customer | None] = relationship(
        "Customer",
        back_populates="orders",
        lazy="selectin",
    )
    lines: Mapped[list["SaleOrderLine"]] = relationship(
        "SaleOrderLine",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SaleOrderLine(Base):
    """Sales order line item."""

    __tablename__ = "sale_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sale_orders.id"),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=True,
    )
    product_name: Mapped[str] = mapped_column(String(100), default="")
    qty: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)

    order: Mapped[SaleOrder] = relationship("SaleOrder", back_populates="lines")
