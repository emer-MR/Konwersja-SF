"""
Orkiestrator wsadowej konwersji sprawozdań finansowych.

Działanie:
1. Zbiera pliki XML/XAdES z przekazanych ścieżek (pliki i/lub foldery).
2. Parsuje każdy plik na obiekt Sprawozdanie.
3. Grupuje sprawozdania po podmiocie (union-find: wspólny NIP lub KRS;
   sprawozdania bez identyfikatorów - po znormalizowanej nazwie).
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
    """Klucz grupowania: NIP, a w razie braku KRS, a w ostateczności nazwa.

    Zachowany dla zgodności; grupowanie w run_batch używa _grupuj_podmioty
    (union-find po wszystkich identyfikatorach)."""
    nip = re.sub(r"\D", "", spr.dane_firmy.nip or "")
    if nip:
        return f"NIP:{nip}"
    krs = re.sub(r"\D", "", spr.dane_firmy.krs or "")
    if krs:
        return f"KRS:{krs}"
    return f"NAZWA:{_normalizuj_nazwe(spr.dane_firmy.nazwa)}"


# Dopiski o stanie spółki i formy prawne sp. z o.o. / S.A. usuwane przy
# porównywaniu nazw. Formy komandytowe (SKA, sp.k.) są ZACHOWANE - odróżniają
# np. "X sp. z o.o." od "X sp. z o.o. SKA" (różne podmioty).
_WZORCE_NAZWY = [
    r"\bw\s+upad[łl]o[śs]ci(\s+likwidacyjnej|\s+uk[łl]adowej)?\b",
    r"\bw\s+likwidacji\b",
    r"\bw\s+restrukturyzacji\b",
    r"\bsp[óo][łl]ka\s+z\s+ograniczon[ąa]\s+odpowiedzialno[śs]ci[ąa]\b",
    r"\bsp[óo][łl]ka\s+akcyjna\b",
    r"\bsp\s*\.?\s*z\s*o\s*\.?\s*o\s*\.?",
    r"\bs\s*\.\s*a\s*\.?(?=\s|$)",
]


def _normalizuj_nazwe(nazwa: str) -> str:
    """Nazwa do porównań: małe litery, bez dopisków 'w likwidacji'/'w upadłości',
    bez formy prawnej sp. z o.o./S.A., bez spacji i znaków interpunkcyjnych."""
    n = (nazwa or "").lower()
    for wz in _WZORCE_NAZWY:
        n = re.sub(wz, " ", n)
    return re.sub(r"[\W_]+", "", n)


def _grupuj_podmioty(sparsowane, log=print) -> "OrderedDict":
    """Grupuje sprawozdania po podmiocie (union-find).

    Sprawozdania łączone są, gdy mają wspólny NIP lub KRS. Sprawozdanie bez
    żadnego identyfikatora dołączane jest po znormalizowanej nazwie - tylko
    gdy nazwa wskazuje jednoznacznie jedną grupę (inaczej zostaje osobno).
    """
    n = len(sparsowane)
    rodzic = list(range(n))

    def find(i):
        while rodzic[i] != i:
            rodzic[i] = rodzic[rodzic[i]]
            i = rodzic[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            rodzic[max(ra, rb)] = min(ra, rb)

    pierwszy = {}
    bez_id = []
    for i, (_p, spr) in enumerate(sparsowane):
        nip = re.sub(r"\D", "", spr.dane_firmy.nip or "")
        krs = re.sub(r"\D", "", spr.dane_firmy.krs or "")
        ids = ([f"NIP:{nip}"] if nip else []) + ([f"KRS:{krs}"] if krs else [])
        if not ids:
            bez_id.append(i)
        for k in ids:
            if k in pierwszy:
                union(i, pierwszy[k])
            else:
                pierwszy[k] = i

    # Znormalizowane nazwy grup z identyfikatorami
    nazwa_do_grup = {}
    for i, (_p, spr) in enumerate(sparsowane):
        if i in bez_id:
            continue
        nazwa_do_grup.setdefault(_normalizuj_nazwe(spr.dane_firmy.nazwa), set()).add(i)
    nazwa_bez_id = {}
    for i in bez_id:
        nz = _normalizuj_nazwe(sparsowane[i][1].dane_firmy.nazwa)
        grupy_nazwy = {find(g) for g in nazwa_do_grup.get(nz, set())}
        if len(grupy_nazwy) == 1:
            union(i, grupy_nazwy.pop())
        elif len(grupy_nazwy) > 1:
            log(f"  [UWAGA] {sparsowane[i][0].name}: brak NIP/KRS, nazwa pasuje do kilku "
                "podmiotów - sprawozdanie pozostawione osobno.")
        elif nz and nz in nazwa_bez_id:
            union(i, nazwa_bez_id[nz])
        else:
            nazwa_bez_id[nz] = i

    grupy = OrderedDict()
    for i, ps in enumerate(sparsowane):
        grupy.setdefault(find(i), []).append(ps)
    return grupy


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
    grupy = _grupuj_podmioty(sparsowane, log=log)

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
