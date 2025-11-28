"""
Modele bazy danych.
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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

    # Relacja do konwersji
    conversions: Mapped[list["Conversion"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
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

    # Relacja do użytkownika
    user: Mapped["User"] = relationship(back_populates="conversions")

    def __repr__(self) -> str:
        return f"<Conversion {self.id} by User {self.user_id}>"
