"""
Modele bazy danych - Czytnik SF (uproszczona wersja).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Model użytkownika (tylko administrator)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Conversion(Base):
    """Model konwersji (historia dla admina)."""

    __tablename__ = "conversions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Dane pliku wejściowego
    input_filename: Mapped[str] = mapped_column(String(255))

    # Metadane sprawozdania
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_nip: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Ścieżka do archiwum admina (jeśli przechowywane)
    archive_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Data konwersji
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Conversion {self.id}: {self.company_name}>"
