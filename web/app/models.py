"""
Modele bazy danych.
"""

from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Text, Boolean, func, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Tabela asocjacyjna: wpisy bloga <-> tagi
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("blog_posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("blog_tags.id"), primary_key=True),
)


class User(Base):
    """Model użytkownika."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    # Relacja do konwersji
    conversions: Mapped[list["Conversion"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Relacja do wpisów bloga
    posts: Mapped[list["BlogPost"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Conversion(Base):
    """Model konwersji (historia)."""

    __tablename__ = "conversions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Dane pliku wejściowego
    input_filename: Mapped[str] = mapped_column(String(255))
    input_size_bytes: Mapped[int] = mapped_column(Integer)

    # Dane pliku wyjściowego
    output_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadane sprawozdania
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_nip: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Mikro/Mala/Inna
    period_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status i czas
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, success, error
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Załączniki (JSON)
    attachments_json: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)

    # Relacja do użytkownika
    user: Mapped["User"] = relationship(back_populates="conversions")

    def __repr__(self) -> str:
        return f"<Conversion {self.id} by User {self.user_id}>"


class BlogCategory(Base):
    """Kategoria wpisów bloga."""

    __tablename__ = "blog_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relacja do wpisów
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<BlogCategory {self.name}>"


class BlogTag(Base):
    """Tag wpisów bloga."""

    __tablename__ = "blog_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relacja do wpisów (many-to-many)
    posts: Mapped[list["BlogPost"]] = relationship(
        secondary=post_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<BlogTag {self.name}>"


class BlogPost(Base):
    """Wpis bloga."""

    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)  # HTML z WYSIWYG
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Krótki opis
    featured_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # URL obrazu

    # Status publikacji
    is_published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadane
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relacje
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("blog_categories.id"), nullable=True)
    category: Mapped[Optional["BlogCategory"]] = relationship(back_populates="posts")

    tags: Mapped[list["BlogTag"]] = relationship(
        secondary=post_tags, back_populates="posts"
    )

    def __repr__(self) -> str:
        return f"<BlogPost {self.title}>"


class StaticPage(Base):
    """Strona statyczna (np. O nas, Kontakt, Zastrzeżenie)."""

    __tablename__ = "static_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # np. "kontakt", "zastrzezenie"
    content: Mapped[str] = mapped_column(Text)  # HTML z WYSIWYG
    is_in_menu: Mapped[bool] = mapped_column(default=True)  # Czy pokazywać w menu
    menu_order: Mapped[int] = mapped_column(default=0)  # Kolejność w menu

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<StaticPage {self.slug}>"
