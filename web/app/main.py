"""
Główna aplikacja FastAPI - Czytnik SF.
Uproszczona wersja bez rejestracji użytkowników.
"""

import httpx
import uuid
import shutil
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import init_db, get_db
from app.auth import (
    get_current_user_optional,
    get_current_user,
    authenticate_user,
    create_access_token,
)
from app.models import User, Conversion
from app.xml_validator import validate_xml


# Przechowywanie tymczasowych plików w pamięci (session_id -> file_info)
temp_files: dict[str, dict] = {}


async def cleanup_expired_files():
    """Zadanie w tle - usuwa wygasłe pliki."""
    while True:
        await asyncio.sleep(60)  # Sprawdzaj co minutę
        now = datetime.now()
        expired = []
        for session_id, file_info in temp_files.items():
            if file_info["expires_at"] < now:
                expired.append(session_id)
                # Usuń plik
                try:
                    file_path = Path(file_info["path"])
                    if file_path.exists():
                        file_path.unlink()
                except Exception:
                    pass
        for session_id in expired:
            del temp_files[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicjalizacja przy starcie aplikacji."""
    # Utwórz katalogi
    Path("./data").mkdir(exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    settings.ADMIN_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Wyczyść osierocone pliki tymczasowe z poprzedniego uruchomienia
    for f in settings.OUTPUT_DIR.glob("*.xlsx"):
        try:
            f.unlink()
        except Exception:
            pass

    # Inicjalizuj bazę danych
    await init_db()

    # Uruchom zadanie czyszczące
    cleanup_task = asyncio.create_task(cleanup_expired_files())

    yield

    # Cleanup
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


async def verify_recaptcha(recaptcha_response: str) -> bool:
    """Weryfikuje odpowiedź reCAPTCHA z Google."""
    if not settings.RECAPTCHA_ENABLED:
        return True

    if not settings.RECAPTCHA_SECRET_KEY:
        return True

    if not recaptcha_response:
        return False

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response,
            }
        )
        result = response.json()
        return result.get("success", False)


# Utwórz aplikację
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Szablony Jinja2
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Pliki statyczne
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# ============== STRONY PUBLICZNE ==============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Strona główna z konwerterem."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
            "recaptcha_enabled": settings.RECAPTCHA_ENABLED and bool(settings.RECAPTCHA_SITE_KEY),
            "ga_measurement_id": settings.GA_MEASUREMENT_ID,
            "contact_email": settings.CONTACT_EMAIL,
            "contact_address": settings.CONTACT_ADDRESS,
        },
    )


@app.get("/polityka-prywatnosci", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Polityka prywatności."""
    return templates.TemplateResponse(
        "privacy.html",
        {
            "request": request,
            "ga_measurement_id": settings.GA_MEASUREMENT_ID,
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


@app.get("/regulamin", response_class=HTMLResponse)
async def terms(request: Request):
    """Regulamin."""
    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "ga_measurement_id": settings.GA_MEASUREMENT_ID,
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


# ============== KONWERSJA (HTMX) ==============

@app.post("/htmx/convert", response_class=HTMLResponse)
async def htmx_convert(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint konwersji zwracający HTML (dla HTMX).
    Dostępny bez logowania.
    """
    import json
    import aiofiles
    from app.converter_simple import convert_file

    # Pobierz dane formularza
    form = await request.form()

    # Weryfikacja reCAPTCHA
    if settings.RECAPTCHA_ENABLED and settings.RECAPTCHA_SECRET_KEY:
        recaptcha_response = form.get("g-recaptcha-response", "")
        is_valid = await verify_recaptcha(recaptcha_response)
        if not is_valid:
            return templates.TemplateResponse(
                "partials/conversion_result.html",
                {
                    "request": request,
                    "status": "error",
                    "error_message": "Weryfikacja reCAPTCHA nie powiodła się. Spróbuj ponownie.",
                },
            )

    # Pobierz plik z formularza
    file = form.get("file")

    if not file or not hasattr(file, 'filename'):
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": "Nie wybrano pliku",
            },
        )

    filename = file.filename
    if not filename.lower().endswith(('.xml', '.xades')):
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": "Dozwolone są tylko pliki XML lub XAdES",
            },
        )

    # Odczytaj zawartość
    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": f"Plik jest zbyt duży (max {settings.MAX_UPLOAD_SIZE_MB} MB)",
            },
        )

    # Walidacja XML - bezpieczeństwo i struktura
    is_valid, error_message, entity_type = validate_xml(content)
    if not is_valid:
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": f"Walidacja pliku XML nieudana: {error_message}",
            },
        )

    # Generuj unikalne ID sesji
    session_id = str(uuid.uuid4())
    input_path = settings.UPLOAD_DIR / f"{session_id}.xml"
    output_path = settings.OUTPUT_DIR / f"{session_id}.xlsx"
    attachments_subdir = settings.ATTACHMENTS_DIR / session_id

    try:
        # Zapisz plik wejściowy
        async with aiofiles.open(input_path, 'wb') as f:
            await f.write(content)

        # Utwórz katalog na załączniki
        attachments_subdir.mkdir(parents=True, exist_ok=True)

        # Konwertuj
        metadata = convert_file(str(input_path), str(output_path), str(attachments_subdir))

        # Zapisz do bazy i archiwizuj (tylko gdy włączone gromadzenie danych)
        if settings.ADMIN_FILE_RETENTION_DAYS > 0:
            conversion = Conversion(
                input_filename=filename,
                company_name=metadata.get("company_name"),
                company_nip=metadata.get("company_nip"),
            )
            archive_dir = settings.ADMIN_ARCHIVE_DIR / session_id
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_xlsx = archive_dir / f"{session_id}.xlsx"
            shutil.copy2(output_path, archive_xlsx)
            conversion.archive_path = str(archive_xlsx)
            db.add(conversion)
            await db.commit()

        # Zapisz plik tymczasowy dla użytkownika (5 minut)
        temp_files[session_id] = {
            "path": str(output_path),
            "filename": metadata["output_filename"],
            "expires_at": datetime.now() + timedelta(minutes=settings.USER_FILE_EXPIRY_MINUTES),
        }

        # Przygotuj załączniki do odpowiedzi
        attachments = metadata.get("attachments", [])
        if attachments:
            for att in attachments:
                att_session_id = f"{session_id}_att_{att['id']}"
                temp_files[att_session_id] = {
                    "path": att["path"],
                    "filename": att.get("original_name", f"zalacznik.{att.get('extension', 'bin')}"),
                    "expires_at": datetime.now() + timedelta(minutes=settings.USER_FILE_EXPIRY_MINUTES),
                }
                att["download_url"] = f"/download/{att_session_id}"

        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "success",
                "session_id": session_id,
                "download_url": f"/download/{session_id}",
                "company_name": metadata.get("company_name"),
                "company_nip": metadata.get("company_nip"),
                "entity_type": metadata.get("entity_type"),
                "period_from": metadata.get("period_from"),
                "period_to": metadata.get("period_to"),
                "jednostka_walutowa": metadata.get("jednostka_walutowa", "PLN"),
                "wariant_rzis": metadata.get("wariant_rzis", "porownawczy"),
                "preview": metadata.get("preview", {}),
                "attachments": attachments,
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": str(e),
            },
        )

    finally:
        # Usuń plik wejściowy
        if input_path.exists():
            input_path.unlink()


@app.get("/download/{session_id}")
async def download_file(request: Request, session_id: str):
    """Pobieranie pliku XLSX (tymczasowy link)."""
    error_msg = None

    if session_id not in temp_files:
        error_msg = "Link do pobrania wygasł lub nie istnieje"
    else:
        file_info = temp_files[session_id]
        if file_info["expires_at"] < datetime.now():
            del temp_files[session_id]
            error_msg = "Link do pobrania wygasł (pliki są dostępne przez 5 minut)"
        else:
            file_path = Path(file_info["path"])
            if not file_path.exists():
                del temp_files[session_id]
                error_msg = "Plik został już usunięty z serwera"

    if error_msg:
        return templates.TemplateResponse(
            "download_expired.html",
            {
                "request": request,
                "error_message": error_msg,
                "ga_measurement_id": settings.GA_MEASUREMENT_ID,
            },
            status_code=404,
        )

    return FileResponse(
        path=file_path,
        filename=file_info["filename"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ============== PANEL ADMINISTRACYJNY ==============

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
):
    """Strona logowania admina."""
    if user and user.is_admin:
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": None, "ga_measurement_id": settings.GA_MEASUREMENT_ID},
    )


@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Obsługa formularza logowania admina."""
    user = await authenticate_user(db, email, password)

    if not user or not user.is_admin:
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Nieprawidłowe dane lub brak uprawnień administratora", "ga_measurement_id": settings.GA_MEASUREMENT_ID},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Utwórz token i ustaw cookie
    access_token = create_access_token(data={"sub": str(user.id)})

    response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,
        samesite="lax",
    )
    return response


@app.get("/admin/logout")
async def admin_logout():
    """Wylogowanie admina."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Panel administracyjny - lista konwersji."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Brak uprawnień")

    # Pobierz konwersje
    result = await db.execute(
        select(Conversion)
        .order_by(Conversion.created_at.desc())
        .limit(100)
    )
    conversions = result.scalars().all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "conversions": conversions,
            "retention_days": settings.ADMIN_FILE_RETENTION_DAYS,
            "ga_measurement_id": settings.GA_MEASUREMENT_ID,
        },
    )


@app.get("/admin/download/{conversion_id}")
async def admin_download_file(
    conversion_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobieranie pliku z archiwum admina."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Brak uprawnień")

    result = await db.execute(
        select(Conversion).where(Conversion.id == conversion_id)
    )
    conversion = result.scalar_one_or_none()

    if not conversion or not conversion.archive_path:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")

    file_path = Path(conversion.archive_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plik nie istnieje na dysku")

    filename = f"{conversion.company_name or 'sprawozdanie'}_{conversion.id}.xlsx"
    # Sanitize filename
    filename = "".join(c for c in filename if c not in '<>:"/\\|?*')

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.post("/admin/settings", response_class=HTMLResponse)
async def admin_update_settings(
    request: Request,
    retention_days: int = Form(...),
    user: User = Depends(get_current_user),
):
    """Aktualizacja ustawień admina (wymaga restartu)."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Brak uprawnień")

    # Informacja - zmiana wymaga edycji .env i restartu
    return templates.TemplateResponse(
        "admin/settings_info.html",
        {
            "request": request,
            "user": user,
            "message": f"Aby zmienić czas przechowywania na {retention_days} dni, ustaw ADMIN_FILE_RETENTION_DAYS={retention_days} w pliku .env i zrestartuj aplikację.",
            "ga_measurement_id": settings.GA_MEASUREMENT_ID,
        },
    )
