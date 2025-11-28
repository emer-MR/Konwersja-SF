"""
Schematy Pydantic do walidacji danych.
"""

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============== AUTH ==============

class UserCreate(BaseModel):
    """Schemat rejestracji użytkownika."""
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 znaków")


class UserLogin(BaseModel):
    """Schemat logowania."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Odpowiedź z danymi użytkownika."""
    id: int
    email: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Dane z tokena."""
    user_id: Optional[int] = None


# ============== CONVERSION ==============

class ConversionResponse(BaseModel):
    """Odpowiedź po konwersji."""
    id: int
    status: str
    input_filename: str
    output_filename: Optional[str] = None
    download_url: Optional[str] = None
    company_name: Optional[str] = None
    company_nip: Optional[str] = None
    entity_type: Optional[str] = None
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversionHistoryResponse(BaseModel):
    """Historia konwersji użytkownika."""
    conversions: list[ConversionResponse]
    today_count: int
    daily_limit: int


class DailyLimitResponse(BaseModel):
    """Status limitu dziennego."""
    used: int
    limit: int
    remaining: int
