"""
Konfiguracja aplikacji.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ustawienia aplikacji."""

    # Aplikacja
    APP_NAME: str = "Konwerter SF"
    APP_VERSION: str = "1.1.0"
    DEBUG: bool = False

    # Baza danych
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"

    # JWT
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 godziny

    # reCAPTCHA v2
    RECAPTCHA_SITE_KEY: str = ""  # Klucz publiczny (do formularza)
    RECAPTCHA_SECRET_KEY: str = ""  # Klucz prywatny (do weryfikacji)
    RECAPTCHA_ENABLED: bool = True  # Włącz/wyłącz reCAPTCHA

    # Limity
    MAX_CONVERSIONS_PER_DAY: int = 10
    MAX_UPLOAD_SIZE_MB: int = 10
    FILE_CLEANUP_HOURS: int = 1

    # Ścieżki
    UPLOAD_DIR: Path = Path("./data/uploads")
    OUTPUT_DIR: Path = Path("./data/outputs")
    ATTACHMENTS_DIR: Path = Path("./data/attachments")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Upewnij się, że katalogi istnieją
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
