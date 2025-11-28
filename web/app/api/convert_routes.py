"""
Endpointy konwersji plików.
"""

import uuid
import aiofiles
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Conversion
from app.schemas import ConversionResponse, ConversionHistoryResponse, DailyLimitResponse
from app.converter_simple import convert_file


router = APIRouter(prefix="/api/convert", tags=["convert"])


async def get_today_conversion_count(db: AsyncSession, user_id: int) -> int:
    """Pobiera liczbę konwersji użytkownika z dzisiejszego dnia."""
    today = date.today()
    result = await db.execute(
        select(func.count(Conversion.id))
        .where(Conversion.user_id == user_id)
        .where(func.date(Conversion.created_at) == today)
    )
    return result.scalar() or 0


@router.get("/limit", response_model=DailyLimitResponse)
async def get_daily_limit(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobiera status limitu dziennego."""
    used = await get_today_conversion_count(db, user.id)
    return DailyLimitResponse(
        used=used,
        limit=settings.MAX_CONVERSIONS_PER_DAY,
        remaining=max(0, settings.MAX_CONVERSIONS_PER_DAY - used),
    )


@router.post("/", response_model=ConversionResponse)
async def convert_xml(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Konwertuje plik XML sprawozdania finansowego do XLSX.
    Limit: 10 konwersji dziennie.
    """
    # Sprawdź limit dzienny
    today_count = await get_today_conversion_count(db, user.id)
    if today_count >= settings.MAX_CONVERSIONS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Przekroczono dzienny limit {settings.MAX_CONVERSIONS_PER_DAY} konwersji. Spróbuj ponownie jutro.",
        )

    # Walidacja pliku
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brak nazwy pliku",
        )

    if not file.filename.lower().endswith(('.xml', '.xades')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dozwolone są tylko pliki XML lub XAdES",
        )

    # Sprawdź rozmiar
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Plik jest zbyt duży. Maksymalny rozmiar: {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    # Utwórz rekord konwersji
    conversion = Conversion(
        user_id=user.id,
        input_filename=file.filename,
        input_size_bytes=len(content),
        status="pending",
    )
    db.add(conversion)
    await db.flush()

    # Generuj unikalne ścieżki
    unique_id = str(uuid.uuid4())
    input_path = settings.UPLOAD_DIR / f"{unique_id}.xml"
    output_path = settings.OUTPUT_DIR / f"{unique_id}.xlsx"

    try:
        # Zapisz plik wejściowy
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

        return ConversionResponse(
            id=conversion.id,
            status="success",
            input_filename=conversion.input_filename,
            output_filename=conversion.output_filename,
            download_url=f"/api/convert/download/{conversion.id}",
            company_name=conversion.company_name,
            company_nip=conversion.company_nip,
            entity_type=conversion.entity_type,
            period_from=conversion.period_from,
            period_to=conversion.period_to,
            created_at=conversion.created_at,
        )

    except Exception as e:
        # Zapisz błąd
        conversion.status = "error"
        conversion.error_message = str(e)[:500]
        await db.flush()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Błąd konwersji: {str(e)}",
        )

    finally:
        # Usuń plik wejściowy
        if input_path.exists():
            input_path.unlink()


@router.get("/download/{conversion_id}")
async def download_file(
    conversion_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobiera skonwertowany plik XLSX."""
    # Pobierz rekord konwersji
    result = await db.execute(
        select(Conversion)
        .where(Conversion.id == conversion_id)
        .where(Conversion.user_id == user.id)
    )
    conversion = result.scalar_one_or_none()

    if not conversion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konwersja nie znaleziona",
        )

    if conversion.status != "success" or not conversion.output_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plik nie jest dostępny do pobrania",
        )

    output_path = Path(conversion.output_path)
    if not output_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plik wygasł lub został usunięty",
        )

    return FileResponse(
        path=output_path,
        filename=conversion.output_filename or "sprawozdanie.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/history", response_model=ConversionHistoryResponse)
async def get_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobiera historię konwersji użytkownika."""
    # Pobierz konwersje (ostatnie 50)
    result = await db.execute(
        select(Conversion)
        .where(Conversion.user_id == user.id)
        .order_by(Conversion.created_at.desc())
        .limit(50)
    )
    conversions = result.scalars().all()

    # Policz dzisiejsze
    today_count = await get_today_conversion_count(db, user.id)

    # Przekształć na response
    conversion_responses = []
    for conv in conversions:
        download_url = None
        if conv.status == "success" and conv.output_path:
            output_path = Path(conv.output_path)
            if output_path.exists():
                download_url = f"/api/convert/download/{conv.id}"

        conversion_responses.append(ConversionResponse(
            id=conv.id,
            status=conv.status,
            input_filename=conv.input_filename,
            output_filename=conv.output_filename,
            download_url=download_url,
            company_name=conv.company_name,
            company_nip=conv.company_nip,
            entity_type=conv.entity_type,
            period_from=conv.period_from,
            period_to=conv.period_to,
            error_message=conv.error_message,
            created_at=conv.created_at,
        ))

    return ConversionHistoryResponse(
        conversions=conversion_responses,
        today_count=today_count,
        daily_limit=settings.MAX_CONVERSIONS_PER_DAY,
    )
