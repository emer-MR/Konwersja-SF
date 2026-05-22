"""
Orkiestrator wsadowej konwersji sprawozdań finansowych.

Działanie:
1. Zbiera pliki XML/XAdES z przekazanych ścieżek (pliki i/lub foldery).
2. Parsuje każdy plik na obiekt Sprawozdanie.
3. Grupuje sprawozdania po podmiocie (NIP, a w razie braku KRS / nazwa).
4. Dla podmiotu z 1 sprawozdaniem  -> klasyczny XLSXConverter (8 arkuszy).
   Dla podmiotu z 2+ sprawozdaniami -> MultiYearConverter (kolumny lat).
5. Wyniki (XLSX + załączniki) zapisuje w podfolderze _Konwersja_SF
   obok plików źródłowych danego podmiotu.

Używany przez konwertuj.py (punkt wejścia dla pliku .bat).
"""

import re
from collections import OrderedDict
from pathlib import Path

from parser import SFParser
from converter import XLSXConverter
from multi_converter import MultiYearConverter

NAZWA_PODFOLDERU = "_Konwersja_SF"
ROZSZERZENIA = {".xml", ".xades"}


def _zbierz_pliki(sciezki) -> list:
    """Rozwija listę ścieżek (pliki + foldery) na listę plików XML/XAdES."""
    pliki = []
    for s in sciezki:
        p = Path(s)
        if p.is_file():
            if p.suffix.lower() in ROZSZERZENIA:
                pliki.append(p)
        elif p.is_dir():
            for child in sorted(p.iterdir()):
                if child.is_file() and child.suffix.lower() in ROZSZERZENIA:
                    pliki.append(child)

    # Deduplikacja (po pełnej ścieżce).
    unikalne = []
    widziane = set()
    for p in pliki:
        klucz = str(p.resolve()).lower()
        if klucz not in widziane:
            widziane.add(klucz)
            unikalne.append(p)
    return unikalne


def _klucz_podmiotu(spr) -> str:
    """Klucz grupowania: NIP, a w razie braku KRS, a w ostateczności nazwa."""
    nip = re.sub(r"\D", "", spr.dane_firmy.nip or "")
    if nip:
        return f"NIP:{nip}"
    krs = re.sub(r"\D", "", spr.dane_firmy.krs or "")
    if krs:
        return f"KRS:{krs}"
    return f"NAZWA:{(spr.dane_firmy.nazwa or '').strip().lower()}"


def run_batch(sciezki, log=print) -> dict:
    """Uruchamia konwersję wsadową.

    Args:
        sciezki: lista ścieżek (pliki i/lub foldery) przekazanych do konwersji
        log: funkcja logująca (domyślnie print)

    Returns:
        dict z podsumowaniem: podmioty, pliki_wynikowe, bledy
    """
    podsumowanie = {"podmioty": 0, "pliki_wynikowe": [], "bledy": []}

    pliki = _zbierz_pliki(sciezki)
    if not pliki:
        log("Nie znaleziono plików XML/XAdES do konwersji.")
        return podsumowanie

    log(f"Znaleziono {len(pliki)} plik(ów) do przetworzenia.")
    log("")

    # --- Parsowanie ---------------------------------------------------------
    parser = SFParser()
    sparsowane = []  # list[tuple[Path, Sprawozdanie]]
    for p in pliki:
        try:
            spr = parser.parse(p)
            sparsowane.append((p, spr))
            log(f"  [OK]   {p.name}")
            log(f"         -> {spr.dane_firmy.nazwa}, rok {spr.metadane.okres_do.year}")
        except Exception as e:
            podsumowanie["bledy"].append((str(p), str(e)))
            log(f"  [POMIN] {p.name}")
            log(f"          powod: {e}")

    if not sparsowane:
        log("")
        log("Nie udało się wczytać żadnego sprawozdania.")
        return podsumowanie

    # --- Grupowanie po podmiocie -------------------------------------------
    grupy = OrderedDict()
    for p, spr in sparsowane:
        grupy.setdefault(_klucz_podmiotu(spr), []).append((p, spr))

    podsumowanie["podmioty"] = len(grupy)
    log("")
    log(f"Rozpoznano {len(grupy)} podmiot(ów). Generowanie plików XLSX...")
    log("")

    # --- Konwersja per podmiot ---------------------------------------------
    for elementy in grupy.values():
        elementy.sort(key=lambda ps: ps[1].metadane.okres_do)
        nazwa_firmy = elementy[-1][1].dane_firmy.nazwa
        output_dir = elementy[0][0].parent / NAZWA_PODFOLDERU

        try:
            if len(elementy) == 1:
                spr = elementy[0][1]
                xlsx_path, zalaczniki = XLSXConverter().convert(spr, output_dir)
                log(f"  {nazwa_firmy}  (1 sprawozdanie)")
            else:
                lata = ", ".join(str(s.metadane.okres_do.year) for _, s in elementy)
                xlsx_path, zalaczniki = MultiYearConverter().convert(elementy, output_dir)
                log(f"  {nazwa_firmy}  ({len(elementy)} sprawozdania: {lata})")

            log(f"     XLSX:        {xlsx_path}")
            if zalaczniki:
                log(f"     Załączniki:  {len(zalaczniki)} plik(ów) "
                    f"w folderze {Path(zalaczniki[0]).parent}")
            log("")
            podsumowanie["pliki_wynikowe"].append(str(xlsx_path))

        except Exception as e:
            podsumowanie["bledy"].append((nazwa_firmy, str(e)))
            log(f"  [BŁĄD] {nazwa_firmy}: {e}")
            log("")

    # --- Podsumowanie ------------------------------------------------------
    log("-" * 60)
    log(f"Utworzono plików XLSX: {len(podsumowanie['pliki_wynikowe'])}")
    if podsumowanie["bledy"]:
        log(f"Problemy: {len(podsumowanie['bledy'])}")
        for zrodlo, powod in podsumowanie["bledy"]:
            log(f"  - {zrodlo}: {powod}")

    return podsumowanie
