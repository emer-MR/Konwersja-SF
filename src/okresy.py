"""
Okresy sprawozdawcze - etykiety kolumn i okres danych porównawczych.

Sprawozdanie nie zawsze obejmuje rok kalendarzowy: rok obrotowy może być
przesunięty (np. 01.04-31.03), a przy otwarciu likwidacji / ogłoszeniu
upadłości powstają sprawozdania za okresy niepełne (np. 01.01-17.07 oraz
18.07-31.12). Kolumny w konwerterze wieloletnim są więc kluczowane okresem
(okres_od, okres_do), a nie samym rokiem.
"""

from datetime import date, timedelta
from typing import Optional, Tuple

Okres = Tuple[Optional[date], date]


def _przesun_o_rok(d: date, lat: int) -> date:
    try:
        return d.replace(year=d.year + lat)
    except ValueError:  # 29 lutego
        return d.replace(year=d.year + lat, day=28)


def czy_rok_kalendarzowy(od: Optional[date], do: date) -> bool:
    return od is not None and od == date(do.year, 1, 1) and do == date(do.year, 12, 31)


def czy_pelny_rok(od: Optional[date], do: date) -> bool:
    """Okres dwunastomiesięczny (kalendarzowy lub przesunięty rok obrotowy)."""
    return od is not None and _przesun_o_rok(od, 1) - timedelta(days=1) == do


def dni_okresu(od: Optional[date], do: Optional[date]) -> Optional[int]:
    if od is None or do is None:
        return None
    return (do - od).days + 1


def okres_poprzedni(od: date, do: date) -> Okres:
    """Okres, którego dotyczą dane porównawcze (KwotaB) sprawozdania.

    Dla okresu dwunastomiesięcznego - poprzednie 12 miesięcy. Dla okresu
    niepełnego długość okresu poprzedniego nie wynika z XML - znany jest
    tylko jego koniec (dzień przed okres_od); początek = None.
    """
    koniec = od - timedelta(days=1)
    if czy_pelny_rok(od, do):
        return (_przesun_o_rok(od, -1), koniec)
    return (None, koniec)


def etykieta_okresu(od: Optional[date], do: date) -> str:
    """Czytelna etykieta kolumny: '2022', '2022 (01.01-17.07)',
    '01.04.2022-31.03.2023' albo 'okres do 17.07.2022'."""
    if od is None:
        return f"okres do {do:%d.%m.%Y}"
    if czy_rok_kalendarzowy(od, do):
        return str(do.year)
    if od.year == do.year:
        return f"{do.year} ({od:%d.%m}-{do:%d.%m})"
    return f"{od:%d.%m.%Y}-{do:%d.%m.%Y}"


def klucz_sortowania(okres: Okres):
    od, do = okres
    return (do, od or date.min)
