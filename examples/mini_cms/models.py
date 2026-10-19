"""SQLAlchemy models for the Mini-CMS demonstration application."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for Mini-CMS models."""


class Category(Base):
    """CMS Category model for grouping articles."""

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
    """CMS Article / Post model with rich content and publication workflow."""

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
