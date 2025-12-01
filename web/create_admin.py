#!/usr/bin/env python3
"""
Skrypt do tworzenia konta administratora.

Użycie:
    python create_admin.py email@example.com haslo123

Skrypt utworzy nowego użytkownika z uprawnieniami administratora,
lub nada uprawnienia istniejącemu użytkownikowi.
"""

import sys
import asyncio
from pathlib import Path

# Dodaj ścieżkę do aplikacji
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.database import async_session, init_db
from app.models import User
from app.auth import get_password_hash


async def create_admin(email: str, password: str):
    """Tworzy lub aktualizuje konto administratora."""

    # Inicjalizuj bazę danych
    await init_db()

    async with async_session() as db:
        # Sprawdź czy użytkownik istnieje
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # Użytkownik istnieje - nadaj uprawnienia admina
            user.is_admin = True
            print(f"Użytkownik {email} już istnieje.")
            print("Nadano uprawnienia administratora.")
        else:
            # Utwórz nowego użytkownika
            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                is_admin=True,
                is_active=True,
            )
            db.add(user)
            print(f"Utworzono konto administratora: {email}")

        await db.commit()

    print("\nGotowe! Możesz się zalogować i przejść do /admin")


async def list_admins():
    """Wyświetla listę administratorów."""

    await init_db()

    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.is_admin == True)
        )
        admins = result.scalars().all()

        if admins:
            print("Administratorzy:")
            for admin in admins:
                print(f"  - {admin.email} (ID: {admin.id})")
        else:
            print("Brak administratorów w systemie.")


def main():
    if len(sys.argv) < 2:
        print("Użycie:")
        print("  python create_admin.py <email> <haslo>  - Tworzy administratora")
        print("  python create_admin.py --list            - Lista administratorów")
        print()
        print("Przykład:")
        print("  python create_admin.py admin@example.com MojeHaslo123")
        sys.exit(1)

    if sys.argv[1] == "--list":
        asyncio.run(list_admins())
    elif len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]

        if len(password) < 8:
            print("Błąd: Hasło musi mieć co najmniej 8 znaków.")
            sys.exit(1)

        asyncio.run(create_admin(email, password))
    else:
        print("Błąd: Podaj email i hasło.")
        print("Użycie: python create_admin.py <email> <haslo>")
        sys.exit(1)


if __name__ == "__main__":
    main()
