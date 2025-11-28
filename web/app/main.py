"""
Główna aplikacja FastAPI.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import init_db, get_db
from app.auth import (
    get_current_user_optional,
    get_current_user,
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token,
)
from app.models import User
from app.api.auth_routes import router as auth_router
from app.api.convert_routes import router as convert_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicjalizacja przy starcie aplikacji."""
    # Utwórz katalogi
    Path("./data").mkdir(exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Inicjalizuj bazę danych
    await init_db()

    yield

    # Cleanup (opcjonalnie)


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

# Routery API (tylko auth, convert obsługujemy przez HTMX poniżej)
app.include_router(auth_router)
# app.include_router(convert_router)  # wyłączone - używamy HTMX endpointów


# ============== STRONY HTML ==============

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
):
    """Strona główna."""
    if user:
        return RedirectResponse(url="/convert", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
):
    """Strona logowania."""
    if user:
        return RedirectResponse(url="/convert", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "user": None, "error": None},
    )


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Obsługa formularza logowania."""
    user = await authenticate_user(db, email, password)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user": None, "error": "Nieprawidłowy email lub hasło"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Utwórz token i ustaw cookie
    access_token = create_access_token(data={"sub": str(user.id)})

    response = RedirectResponse(url="/convert", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,  # 24 godziny
        samesite="lax",
    )
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
):
    """Strona rejestracji."""
    if user:
        return RedirectResponse(url="/convert", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": None, "error": None, "success": None},
    )


@app.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Obsługa formularza rejestracji."""
    error = None

    # Walidacja
    if password != password_confirm:
        error = "Hasła nie są identyczne"
    elif len(password) < 8:
        error = "Hasło musi mieć co najmniej 8 znaków"
    else:
        # Sprawdź czy email istnieje
        existing_user = await get_user_by_email(db, email)
        if existing_user:
            error = "Ten adres email jest już zarejestrowany"

    if error:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "user": None, "error": error, "success": None},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Utwórz użytkownika
    await create_user(db, email, password)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
            "error": None,
            "success": "Konto utworzone! Możesz się teraz zalogować.",
        },
    )


@app.get("/logout")
async def logout():
    """Wylogowanie."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@app.get("/convert", response_class=HTMLResponse)
async def convert_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    """Strona konwersji (wymaga logowania)."""
    return templates.TemplateResponse(
        "convert.html",
        {"request": request, "user": user},
    )


# ============== HTMX PARTIALS ==============

@app.get("/htmx/history", response_class=HTMLResponse)
async def htmx_history(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fragment HTML z historią konwersji (dla HTMX)."""
    from sqlalchemy import select
    from app.models import Conversion

    result = await db.execute(
        select(Conversion)
        .where(Conversion.user_id == user.id)
        .order_by(Conversion.created_at.desc())
        .limit(20)
    )
    conversions = result.scalars().all()

    # Dodaj download_url do każdej konwersji
    conv_list = []
    for conv in conversions:
        conv_dict = {
            "id": conv.id,
            "input_filename": conv.input_filename,
            "company_name": conv.company_name,
            "status": conv.status,
            "error_message": conv.error_message,
            "created_at": conv.created_at,
            "download_url": None,
        }
        if conv.status == "success" and conv.output_path:
            output_path = Path(conv.output_path)
            if output_path.exists():
                conv_dict["download_url"] = f"/api/convert/download/{conv.id}"
        conv_list.append(conv_dict)

    return templates.TemplateResponse(
        "partials/history_table.html",
        {"request": request, "conversions": conv_list},
    )


@app.get("/htmx/limit", response_class=HTMLResponse)
async def htmx_limit(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fragment HTML z limitem dziennym (dla HTMX)."""
    from datetime import date
    from sqlalchemy import select, func
    from app.models import Conversion

    today = date.today()
    result = await db.execute(
        select(func.count(Conversion.id))
        .where(Conversion.user_id == user.id)
        .where(func.date(Conversion.created_at) == today)
    )
    used = result.scalar() or 0
    remaining = max(0, settings.MAX_CONVERSIONS_PER_DAY - used)

    return templates.TemplateResponse(
        "partials/limit_badge.html",
        {
            "request": request,
            "used": used,
            "limit": settings.MAX_CONVERSIONS_PER_DAY,
            "remaining": remaining,
        },
    )


# ============== OVERRIDE API CONVERT DLA HTMX ==============

@app.post("/htmx/convert", response_class=HTMLResponse)
async def htmx_convert(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint konwersji zwracający HTML (dla HTMX).
    """
    import uuid
    import aiofiles
    from datetime import date
    from sqlalchemy import select, func
    from app.models import Conversion
    from app.converter_simple import convert_file

    # Sprawdź limit dzienny
    today = date.today()
    result = await db.execute(
        select(func.count(Conversion.id))
        .where(Conversion.user_id == user.id)
        .where(func.date(Conversion.created_at) == today)
    )
    today_count = result.scalar() or 0

    if today_count >= settings.MAX_CONVERSIONS_PER_DAY:
        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": f"Przekroczono dzienny limit {settings.MAX_CONVERSIONS_PER_DAY} konwersji.",
            },
        )

    # Pobierz plik z formularza
    form = await request.form()
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

    # Utwórz rekord konwersji
    conversion = Conversion(
        user_id=user.id,
        input_filename=filename,
        input_size_bytes=len(content),
        status="pending",
    )
    db.add(conversion)
    await db.flush()

    # Generuj ścieżki
    unique_id = str(uuid.uuid4())
    input_path = settings.UPLOAD_DIR / f"{unique_id}.xml"
    output_path = settings.OUTPUT_DIR / f"{unique_id}.xlsx"

    try:
        # Zapisz plik
        async with aiofiles.open(input_path, 'wb') as f:
            await f.write(content)

        # Konwertuj
        metadata = convert_file(str(input_path), str(output_path))

        # Aktualizuj rekord
        conversion.status = "success"
        conversion.output_filename = metadata["output_filename"]
        conversion.output_path = str(output_path)
        conversion.company_name = metadata.get("company_name")
        conversion.company_nip = metadata.get("company_nip")
        conversion.entity_type = metadata.get("entity_type")
        conversion.period_from = metadata.get("period_from")
        conversion.period_to = metadata.get("period_to")

        await db.flush()

        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "success",
                "download_url": f"/api/convert/download/{conversion.id}",
                "company_name": conversion.company_name,
                "company_nip": conversion.company_nip,
                "entity_type": conversion.entity_type,
                "period_from": conversion.period_from,
                "period_to": conversion.period_to,
            },
        )

    except Exception as e:
        conversion.status = "error"
        conversion.error_message = str(e)[:500]
        await db.flush()

        return templates.TemplateResponse(
            "partials/conversion_result.html",
            {
                "request": request,
                "status": "error",
                "error_message": str(e),
            },
        )

    finally:
        if input_path.exists():
            input_path.unlink()


@app.get("/api/convert/download/{conversion_id}")
async def download_file(
    conversion_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobieranie pliku XLSX."""
    from fastapi.responses import FileResponse
    from sqlalchemy import select
    from app.models import Conversion

    result = await db.execute(
        select(Conversion)
        .where(Conversion.id == conversion_id)
        .where(Conversion.user_id == user.id)
    )
    conversion = result.scalar_one_or_none()

    if not conversion:
        raise HTTPException(status_code=404, detail="Konwersja nie znaleziona")

    if conversion.status != "success" or not conversion.output_path:
        raise HTTPException(status_code=400, detail="Plik niedostępny")

    output_path = Path(conversion.output_path)
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Plik nie istnieje")

    return FileResponse(
        path=output_path,
        filename=conversion.output_filename or f"konwersja_{conversion_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
