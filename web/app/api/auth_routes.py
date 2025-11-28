"""
Endpointy autoryzacji.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import (
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.models import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Rejestracja nowego użytkownika."""
    # Sprawdź czy email już istnieje
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten adres email jest już zarejestrowany",
        )

    # Utwórz użytkownika
    user = await create_user(db, user_data.email, user_data.password)
    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Logowanie użytkownika."""
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło",
        )

    # Utwórz token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Ustaw cookie (dla przeglądarki)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,  # 24 godziny
        samesite="lax",
    )

    return Token(access_token=access_token)


@router.post("/logout")
async def logout(response: Response):
    """Wylogowanie użytkownika."""
    response.delete_cookie("access_token")
    return {"message": "Wylogowano pomyślnie"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Pobiera dane zalogowanego użytkownika."""
    return user
