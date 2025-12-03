"""
Schematy Pydantic do walidacji danych - Czytnik SF.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ============== AUTH (tylko admin) ==============

class UserLogin(BaseModel):
    """Schemat logowania admina."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Dane z tokena."""
    user_id: Optional[int] = None


# ============== CONVERSION ==============

class ConversionResponse(BaseModel):
    """Odpowiedź z informacjami o konwersji (dla admina)."""
    id: int
    input_filename: str
    company_name: Optional[str] = None
    company_nip: Optional[str] = None
    archive_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
