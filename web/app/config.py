"""
Konfiguracja aplikacji.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ustawienia aplikacji."""

    # Aplikacja
    APP_NAME: str = "Czytnik SF"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Baza danych
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"

    # JWT (tylko dla admina)
    SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 godziny

    # reCAPTCHA v2
    RECAPTCHA_SITE_KEY: str = ""  # Klucz publiczny (do formularza)
    RECAPTCHA_SECRET_KEY: str = ""  # Klucz prywatny (do weryfikacji)
    RECAPTCHA_ENABLED: bool = True  # Włącz/wyłącz reCAPTCHA

    # Limity (bez ograniczeń dla użytkowników - tylko captcha)
    MAX_UPLOAD_SIZE_MB: int = 10

    # Czas życia plików dla użytkownika (w minutach)
    USER_FILE_EXPIRY_MINUTES: int = 5

    # Czas przechowywania plików dla admina (w dniach, 0 = nie przechowuj)
    ADMIN_FILE_RETENTION_DAYS: int = 30

    # Google Analytics
    GA_MEASUREMENT_ID: str = ""  # Format: G-XXXXXXXXXX

    # Dane kontaktowe
    CONTACT_EMAIL: str = "kontakt@analizy.io"
    CONTACT_ADDRESS: str = ""

    # Ścieżki
    UPLOAD_DIR: Path = Path("./data/uploads")
    OUTPUT_DIR: Path = Path("./data/outputs")
    ATTACHMENTS_DIR: Path = Path("./data/attachments")
    ADMIN_ARCHIVE_DIR: Path = Path("./data/admin_archive")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Upewnij się, że katalogi istnieją
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
settings.ADMIN_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
