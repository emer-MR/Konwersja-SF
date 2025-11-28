"""
Konfiguracja bazy danych SQLAlchemy (async).
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Silnik async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Fabryka sesji
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Bazowa klasa dla modeli."""
    pass


async def get_db() -> AsyncSession:
    """Dependency do pobierania sesji bazy danych."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Inicjalizuje bazę danych (tworzy tabele)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
