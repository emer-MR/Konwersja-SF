# Plan implementacji konwertera sprawozdań finansowych XML → XLSX

## Cel projektu

Stworzenie skryptów Python do konwersji polskich sprawozdań finansowych z formatu XML/XAdES do formatu XLSX, umożliwiającego dalszą analizę i obróbkę danych (analiza wskaźnikowa, porównawcza, etc.).

---

## Interfejs użytkownika

### GUI (tkinter)

Prosty interfejs graficzny z następującymi elementami:
- Przycisk "Wybierz plik(i)" - wybór pojedynczych plików XML/XAdES
- Przycisk "Wybierz folder" - wybór folderu z plikami
- Checkbox "Przeszukuj podfoldery"
- Pole wyboru folderu wyjściowego
- Lista plików do przetworzenia
- Przycisk "Konwertuj"
- Log/pasek postępu z informacjami o przetwarzaniu

```python
# gui.py - szkic interfejsu
import tkinter as tk
from tkinter import filedialog, ttk

class SFConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Konwerter Sprawozdań Finansowych XML → XLSX")
        self.root.geometry("600x400")

        # Przyciski wyboru plików
        ttk.Button(text="Wybierz plik(i)...", command=self.select_files)
        ttk.Button(text="Wybierz folder...", command=self.select_folder)

        # Lista plików
        self.file_listbox = tk.Listbox()

        # Opcje
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(text="Przeszukuj podfoldery", variable=self.recursive_var)

        # Folder wyjściowy
        ttk.Button(text="Folder wyjściowy...", command=self.select_output)

        # Przycisk konwersji
        ttk.Button(text="Konwertuj", command=self.convert)

        # Log
        self.log_text = tk.Text()
```

---

## Analiza źródeł danych

### Typy jednostek (3 główne)

| Typ | Element XML | Załącznik ustawy | Złożoność |
|-----|-------------|------------------|-----------|
| Mikro | `JednostkaMikro` | Nr 4 | Uproszczona (~15 pozycji bilansu) |
| Mała | `JednostkaMala` | Nr 5 | Średnia |
| Inna | `JednostkaInna` | Nr 1 | Pełna (~100+ pozycji bilansu) |

### Wersje schematów

- **1-0** - namespace: `.../2018/07/09/...`
- **1-2** - namespace: `.../2018/07/09/...`
- **1-3** - namespace: `.../2025/01/01/...`

### Struktura pliku XML sprawozdania

```
JednostkaXXX (root)
├── Naglowek
│   ├── OkresOd, OkresDo
│   ├── DataSporzadzenia
│   ├── KodSprawozdania (z atrybutami: kodSystemowy, wersjaSchemy)
│   └── WariantSprawozdania
├── InformacjeOgolne* / WprowadzenieDoSprawozdania*
│   ├── P_1 (dane firmy)
│   │   ├── P_1A (nazwa, siedziba)
│   │   ├── P_1B (adres)
│   │   ├── P_1C/P_1D (NIP)
│   │   └── P_1D/P_1E (KRS)
│   ├── P_3 (okres sprawozdania)
│   └── P_5, P_6, P_7... (zasady rachunkowości, kontynuacja działalności)
├── Bilans
│   ├── Aktywa (hierarchia pozycji)
│   └── Pasywa (hierarchia pozycji)
├── RZiS
│   ├── RZiSPor (wariant porównawczy) LUB
│   └── RZiSKalk (wariant kalkulacyjny)
├── DodatkoweInformacjeIObjasnienia (nota podatkowa)
├── [Zalaczniki - POMIJAMY]
└── [ds:Signature - POMIJAMY]
```

### Format wartości w XML

- `KwotaA` = rok bieżący (okres sprawozdania)
- `KwotaB` = rok poprzedni (dane porównawcze)

---

## Oczekiwany format XLSX

### Arkusze

1. **Bilans** - pozycje aktywów i pasywów (format czytelny dla człowieka)
2. **RZiS (w.por.)** lub **RZiS (w.kalk.)** - rachunek zysków i strat
3. **Nota podatkowa** - jeśli dane dostępne
4. **Dane surowe** - wszystkie pozycje z kodami (format do analizy)
5. **Dane analityczne** - format "długi" do analizy porównawczej i wskaźnikowej

### Arkusz 1-3: Format czytelny (przykład Bilans)

```
     |        A                    |       B        |       C        |
-----|-----------------------------| ---------------|----------------|
  1  |                             | KRS:0000632089 |                |
  2  |                             |      2023      |      2022      |
  4  | Okres do                    |   2023-12-31   |   2022-12-31   |
  5  | Nazwa firmy                 |   FIRMA SP...  |   FIRMA SP...  |
  6  | Jednostka                   | JednostkaMikro | JednostkaMikro |
  7  | Wynik weryfikacji sum       |      True      |      True      |
  8  | Aktywa razem                |   755584.15    |   755584.15    |
  9  | A. Aktywa trwałe...         |       0.00     |       0.00     |
 ... |           ...               |      ...       |      ...       |
 20  | Pasywa razem                |   755584.15    |   755584.15    |
 ... |           ...               |      ...       |      ...       |
```

### Arkusz 4: Dane surowe (z kodami pozycji)

Format tabelaryczny ze standaryzowanymi kodami - łatwy do filtrowania i wyszukiwania:

```
     |     A      |   B    |       C       |     D      |     E      |
-----|------------|--------|---------------|------------|------------|
  1  | sekcja     | kod    | opis          | rok_biezacy| rok_poprz  |
  2  | Bilans     | Aktywa | Aktywa razem  | 755584.15  | 755584.15  |
  3  | Bilans     |Aktywa_A| A. Aktywa trw.| 0.00       | 0.00       |
  4  | Bilans     |Aktywa_B| B. Aktywa obr.| 755584.15  | 755584.15  |
  5  | RZiS       | A      | A. Przychody..| 1000.00    | 900.00     |
  6  | Nota       | P_ID_1 | Zysk brutto   | 500.00     | 400.00     |
```

### Arkusz 5: Dane analityczne (format "długi")

Format zoptymalizowany do analizy porównawczej wielu firm, analizy wskaźnikowej, pivot tables i importu do baz danych:

```
| firma | nip | krs | typ_jednostki | wersja | okres | sekcja | kod | kod_pelny | opis | kwota |
|-------|-----|-----|---------------|--------|-------|--------|-----|-----------|------|-------|
| FIRMA SP..| 731...| 000...| Mikro | 1-3 | 2023-12-31 | Bilans | Aktywa | Mikro_1-3_Bilans_Aktywa | Aktywa razem | 755584.15 |
| FIRMA SP..| 731...| 000...| Mikro | 1-3 | 2022-12-31 | Bilans | Aktywa | Mikro_1-3_Bilans_Aktywa | Aktywa razem | 755584.15 |
| FIRMA SP..| 731...| 000...| Mikro | 1-3 | 2023-12-31 | RZiS | A | Mikro_1-3_RZiS_A | A. Przychody... | 1000.00 |
| FIRMA SP..| 731...| 000...| Mikro | 1-3 | 2023-12-31 | Nota | P_ID_1 | Mikro_1-3_Nota_P_ID_1 | Zysk brutto | 500.00 |
```

**Kolumna `kod_pelny`** - unikalny identyfikator pozycji uwzględniający:
- Typ jednostki (Mikro/Mala/Inna)
- Wersję schematu (1-0, 1-2, 1-3)
- Sekcję (Bilans/RZiS/Nota)
- Kod pozycji

To rozwiązuje problem, że np. `A` w RZiS to co innego niż `Aktywa_A` w Bilansie, oraz że pozycje mogą mieć różne znaczenia między wersjami schematów.

### Nazwa pliku wyjściowego

Format: `{okres_od}_{okres_do}_e-sprawozdanie_{nazwa_firmy}.xlsx`

Przykład: `2023-01-01_2023-12-31_e-sprawozdanie_SAN-AT INVESTMENTS SP. Z O.O. SPÓŁKA KOMANDYTOWA.xlsx`

---

## Architektura rozwiązania

### Struktura katalogów

```
sf_converter/
├── gui.py               # Interfejs graficzny (tkinter)
├── parser.py            # Parsowanie XML, wykrywanie typu jednostki
├── converter.py         # Generowanie XLSX (wszystkie formaty)
├── mappings.py          # Słownik pozycji → opisy polskie
└── models.py            # Struktury danych (dataclasses)
```

### Zależności

- `openpyxl` - generowanie XLSX (już zainstalowana)
- `lxml` - parsowanie XML z namespace'ami (do zainstalowania: `pip install lxml`)

---

## Szczegóły implementacji

### 1. `models.py` - Struktury danych

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class MetadaneSprawozdania:
    typ_jednostki: str        # "Mikro", "Mala", "Inna"
    wersja_schematu: str      # "1-0", "1-2", "1-3"
    okres_od: date
    okres_do: date
    data_sporzadzenia: date
    wariant_rzis: str         # "porownawczy" lub "kalkulacyjny"

@dataclass
class DaneFirmy:
    nazwa: str
    nip: str
    krs: str | None
    adres: dict               # wojewodztwo, miejscowosc, ulica, kod, etc.

@dataclass
class PozycjaFinansowa:
    sekcja: str               # "Bilans", "RZiS", "Nota"
    kod: str                  # np. "Aktywa_A_II_1"
    opis: str                 # np. "A.II.1. Środki trwałe"
    kwota_biezaca: Decimal | None
    kwota_poprzednia: Decimal | None
    poziom: int               # głębokość wcięcia dla hierarchii (0, 1, 2...)

    def kod_pelny(self, typ_jednostki: str, wersja: str) -> str:
        """Generuje unikalny identyfikator pozycji"""
        return f"{typ_jednostki}_{wersja}_{self.sekcja}_{self.kod}"

@dataclass
class WynikWeryfikacji:
    aktywa_rowne_pasywom_biezacy: bool
    aktywa_rowne_pasywom_poprzedni: bool

@dataclass
class Sprawozdanie:
    metadane: MetadaneSprawozdania
    dane_firmy: DaneFirmy
    bilans_aktywa: list[PozycjaFinansowa]
    bilans_pasywa: list[PozycjaFinansowa]
    rzis: list[PozycjaFinansowa]
    nota_podatkowa: list[PozycjaFinansowa] | None
    weryfikacja: WynikWeryfikacji
```

### 2. `mappings.py` - Mapowania pozycji

Słowniki mapujące kody XML na opisy polskie. Źródło: Słowniczek schematów SF.xlsx

```python
# Jednostka Mikro - Bilans
BILANS_MIKRO = {
    "Aktywa": "Aktywa razem",
    "Aktywa_A": "A. Aktywa trwałe, w tym środki trwałe",
    "Aktywa_B": "B. Aktywa obrotowe",
    "Aktywa_B_1": "B.1. - zapasy",
    "Aktywa_B_2": "B.2. - należności krótkoterminowe",
    "Aktywa_C": "C. Należne wpłaty na kapitał (fundusz) podstawowy",
    "Aktywa_D": "D. Udziały (akcje) własne",
    "Pasywa": "Pasywa razem",
    "Pasywa_A": "A. Kapitał (fundusz) własny",
    "Pasywa_A_1": "A.1. - kapitał (fundusz) podstawowy",
    "Pasywa_B": "B. Zobowiązania i rezerwy na zobowiązania",
    "Pasywa_B_1": "B.1. - rezerwy na zobowiązania",
    "Pasywa_B_2": "B.2. - zobowiązania z tytułu kredytów i pożyczek",
}

# Jednostka Mikro - RZiS
RZIS_MIKRO = {
    "A": "A. Przychody podstawowej działalności operacyjnej i zrównane z nimi",
    "A_1": "A.1. - zmiana stanu produktów",
    "B": "B. Koszty podstawowej działalności operacyjnej",
    "B_I": "B.I. Amortyzacja",
    "B_II": "B.II. Zużycie materiałów i energii",
    "B_III": "B.III. Wynagrodzenia, ubezpieczenia społeczne i inne świadczenia",
    "B_IV": "B.IV. Pozostałe koszty",
    "C": "C. Pozostałe przychody i zyski",
    "C_1": "C.1. - aktualizacja wartości aktywów",
    "D": "D. Pozostałe koszty i straty",
    "D_1": "D.1. - aktualizacja wartości aktywów",
    "E": "E. Podatek dochodowy",
    "F": "F. Zysk/strata netto (A-B+C-D-E)",
}

# Jednostka Inna - Bilans (rozbudowany ~100 pozycji)
BILANS_INNA = {
    "Aktywa": "Aktywa razem",
    "Aktywa_A": "A. Aktywa trwałe",
    "Aktywa_A_I": "A.I. Wartości niematerialne i prawne",
    "Aktywa_A_II": "A.II. Rzeczowe aktywa trwałe",
    "Aktywa_A_II_1": "A.II.1. Środki trwałe",
    "Aktywa_A_II_1_A": "A.II.1.a) grunty",
    "Aktywa_A_II_1_B": "A.II.1.b) budynki, lokale, prawa do lokali i obiekty inżynierii lądowej i wodnej",
    "Aktywa_A_II_1_C": "A.II.1.c) urządzenia techniczne i maszyny",
    "Aktywa_A_II_1_D": "A.II.1.d) środki transportu",
    "Aktywa_A_II_1_E": "A.II.1.e) inne środki trwałe",
    # ... (pełna lista zostanie wygenerowana z słowniczka)
}

# Jednostka Inna - RZiS wariant porównawczy
RZIS_POROWNAWCZY_INNA = {
    "A": "A. Przychody netto ze sprzedaży i zrównane z nimi",
    "A_I": "A.I. Przychody netto ze sprzedaży produktów",
    "A_II": "A.II. Zmiana stanu produktów",
    "A_III": "A.III. Koszt wytworzenia produktów na własne potrzeby jednostki",
    "A_IV": "A.IV. Przychody netto ze sprzedaży towarów i materiałów",
    "B": "B. Koszty działalności operacyjnej",
    "B_I": "B.I. Amortyzacja",
    "B_II": "B.II. Zużycie materiałów i energii",
    "B_III": "B.III. Usługi obce",
    # ... (pełna lista)
}

# Nota podatkowa
NOTA_PODATKOWA = {
    "P_ID_1": "A. Zysk (strata) brutto za dany rok",
    "P_ID_2": "B. Przychody zwolnione z opodatkowania",
    "P_ID_3": "C. Przychody niepodlegające opodatkowaniu w roku bieżącym",
    # ... (pełna lista)
}
```

### 3. `parser.py` - Parser XML

```python
from lxml import etree
from pathlib import Path
from models import *
from mappings import *

class SFParser:
    # Namespace'y dla różnych wersji
    NAMESPACES = {
        'dtsf': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/DefinicjeTypySprawozdaniaFinansowe/',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
    }

    def parse(self, file_path: Path) -> Sprawozdanie:
        """Główna metoda parsowania pliku XML/XAdES"""
        tree = etree.parse(str(file_path))
        root = tree.getroot()

        # Wykryj typ jednostki i wersję
        typ = self._detect_entity_type(root)
        wersja = self._detect_schema_version(root)

        # Parsuj sekcje
        metadane = self._parse_header(root, typ, wersja)
        dane_firmy = self._parse_company_info(root, typ)
        aktywa, pasywa = self._parse_bilans(root, typ)
        rzis = self._parse_rzis(root, typ, metadane.wariant_rzis)
        nota = self._parse_nota_podatkowa(root)

        # Weryfikacja sum
        weryfikacja = self._verify_sums(aktywa, pasywa)

        return Sprawozdanie(
            metadane=metadane,
            dane_firmy=dane_firmy,
            bilans_aktywa=aktywa,
            bilans_pasywa=pasywa,
            rzis=rzis,
            nota_podatkowa=nota,
            weryfikacja=weryfikacja
        )

    def _detect_entity_type(self, root) -> str:
        """Wykrywa typ jednostki z nazwy root elementu"""
        tag = etree.QName(root).localname
        if 'Mikro' in tag:
            return 'Mikro'
        elif 'Mala' in tag:
            return 'Mala'
        else:
            return 'Inna'

    def _detect_schema_version(self, root) -> str:
        """Wykrywa wersję schematu z namespace lub atrybutu"""
        # Szuka atrybutu wersjaSchemy w KodSprawozdania
        # lub dedukuje z namespace
        pass

    def _parse_header(self, root, typ, wersja) -> MetadaneSprawozdania:
        """Parsuje sekcję Naglowek"""
        pass

    def _parse_company_info(self, root, typ) -> DaneFirmy:
        """Parsuje dane firmy z InformacjeOgolne lub WprowadzenieDoSprawozdania"""
        pass

    def _parse_bilans(self, root, typ) -> tuple[list, list]:
        """Parsuje Bilans → lista aktywów i lista pasywów"""
        mapping = BILANS_MIKRO if typ == 'Mikro' else BILANS_INNA
        # Rekurencyjne przechodzenie po elementach
        pass

    def _parse_rzis(self, root, typ, wariant) -> list[PozycjaFinansowa]:
        """Parsuje RZiS (wykrywa wariant porównawczy/kalkulacyjny)"""
        pass

    def _parse_nota_podatkowa(self, root) -> list[PozycjaFinansowa] | None:
        """Parsuje notę podatkową jeśli istnieje"""
        pass

    def _verify_sums(self, aktywa, pasywa) -> WynikWeryfikacji:
        """Sprawdza czy Aktywa = Pasywa dla obu okresów"""
        suma_aktywow_biezaca = aktywa[0].kwota_biezaca if aktywa else None
        suma_pasywow_biezaca = pasywa[0].kwota_biezaca if pasywa else None
        suma_aktywow_poprz = aktywa[0].kwota_poprzednia if aktywa else None
        suma_pasywow_poprz = pasywa[0].kwota_poprzednia if pasywa else None

        return WynikWeryfikacji(
            aktywa_rowne_pasywom_biezacy=(suma_aktywow_biezaca == suma_pasywow_biezaca),
            aktywa_rowne_pasywom_poprzedni=(suma_aktywow_poprz == suma_pasywow_poprz)
        )

    def _extract_positions_recursive(self, element, mapping, level=0) -> list[PozycjaFinansowa]:
        """Rekurencyjnie wyciąga pozycje z hierarchii XML"""
        # Pomija elementy Signature i Zalacznik
        pass
```

### 4. `converter.py` - Konwerter do XLSX

```python
from openpyxl import Workbook
from pathlib import Path
from models import Sprawozdanie

class XLSXConverter:
    def convert(self, sprawozdanie: Sprawozdanie, output_dir: Path) -> Path:
        """Konwertuje sprawozdanie do XLSX, zwraca ścieżkę do pliku"""
        wb = Workbook()

        # Arkusz 1: Bilans (format czytelny)
        ws_bilans = wb.active
        ws_bilans.title = "Bilans"
        self._create_bilans_sheet(ws_bilans, sprawozdanie)

        # Arkusz 2: RZiS (format czytelny)
        wariant = "w.por." if sprawozdanie.metadane.wariant_rzis == "porownawczy" else "w.kalk."
        ws_rzis = wb.create_sheet(f"RZiS ({wariant})")
        self._create_rzis_sheet(ws_rzis, sprawozdanie)

        # Arkusz 3: Nota podatkowa (jeśli dane dostępne)
        if sprawozdanie.nota_podatkowa:
            ws_nota = wb.create_sheet("Nota podatkowa")
            self._create_nota_sheet(ws_nota, sprawozdanie)

        # Arkusz 4: Dane surowe (z kodami pozycji)
        ws_surowe = wb.create_sheet("Dane surowe")
        self._create_raw_data_sheet(ws_surowe, sprawozdanie)

        # Arkusz 5: Dane analityczne (format długi)
        ws_analityczne = wb.create_sheet("Dane analityczne")
        self._create_analytical_sheet(ws_analityczne, sprawozdanie)

        # Generuj nazwę pliku i zapisz
        filename = self._generate_filename(sprawozdanie)
        output_path = output_dir / filename
        wb.save(output_path)
        return output_path

    def _create_bilans_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz Bilans - format czytelny"""
        # ... (jak wcześniej - nagłówek, pozycje aktywów i pasywów)
        pass

    def _create_rzis_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz RZiS - format czytelny"""
        pass

    def _create_nota_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz Nota podatkowa - format czytelny"""
        pass

    def _create_raw_data_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz Dane surowe - wszystkie pozycje z kodami"""
        # Nagłówek
        ws['A1'] = "sekcja"
        ws['B1'] = "kod"
        ws['C1'] = "opis"
        ws['D1'] = "rok_biezacy"
        ws['E1'] = "rok_poprzedni"

        row = 2
        # Wszystkie pozycje z bilansu, RZiS i noty
        wszystkie_pozycje = (
            spr.bilans_aktywa +
            spr.bilans_pasywa +
            spr.rzis +
            (spr.nota_podatkowa or [])
        )

        for poz in wszystkie_pozycje:
            ws[f'A{row}'] = poz.sekcja
            ws[f'B{row}'] = poz.kod
            ws[f'C{row}'] = poz.opis
            ws[f'D{row}'] = float(poz.kwota_biezaca) if poz.kwota_biezaca else None
            ws[f'E{row}'] = float(poz.kwota_poprzednia) if poz.kwota_poprzednia else None
            row += 1

    def _create_analytical_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz Dane analityczne - format długi do analizy"""
        # Nagłówek
        headers = ["firma", "nip", "krs", "typ_jednostki", "wersja",
                   "okres", "sekcja", "kod", "kod_pelny", "opis", "kwota"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        meta = spr.metadane
        firma = spr.dane_firmy
        row = 2

        wszystkie_pozycje = (
            spr.bilans_aktywa +
            spr.bilans_pasywa +
            spr.rzis +
            (spr.nota_podatkowa or [])
        )

        # Dla każdej pozycji - dwa wiersze (rok bieżący i poprzedni)
        for poz in wszystkie_pozycje:
            kod_p = poz.kod_pelny(meta.typ_jednostki, meta.wersja_schematu)

            # Rok bieżący
            if poz.kwota_biezaca is not None:
                ws.cell(row=row, column=1, value=firma.nazwa)
                ws.cell(row=row, column=2, value=firma.nip)
                ws.cell(row=row, column=3, value=firma.krs)
                ws.cell(row=row, column=4, value=meta.typ_jednostki)
                ws.cell(row=row, column=5, value=meta.wersja_schematu)
                ws.cell(row=row, column=6, value=meta.okres_do)
                ws.cell(row=row, column=7, value=poz.sekcja)
                ws.cell(row=row, column=8, value=poz.kod)
                ws.cell(row=row, column=9, value=kod_p)
                ws.cell(row=row, column=10, value=poz.opis)
                ws.cell(row=row, column=11, value=float(poz.kwota_biezaca))
                row += 1

            # Rok poprzedni
            if poz.kwota_poprzednia is not None:
                okres_poprz = date(meta.okres_do.year - 1, 12, 31)
                ws.cell(row=row, column=1, value=firma.nazwa)
                ws.cell(row=row, column=2, value=firma.nip)
                ws.cell(row=row, column=3, value=firma.krs)
                ws.cell(row=row, column=4, value=meta.typ_jednostki)
                ws.cell(row=row, column=5, value=meta.wersja_schematu)
                ws.cell(row=row, column=6, value=okres_poprz)
                ws.cell(row=row, column=7, value=poz.sekcja)
                ws.cell(row=row, column=8, value=poz.kod)
                ws.cell(row=row, column=9, value=kod_p)
                ws.cell(row=row, column=10, value=poz.opis)
                ws.cell(row=row, column=11, value=float(poz.kwota_poprzednia))
                row += 1

    def _generate_filename(self, spr: Sprawozdanie) -> str:
        """Generuje standardową nazwę pliku"""
        meta = spr.metadane
        nazwa = spr.dane_firmy.nazwa
        # Usuń znaki niedozwolone w nazwach plików
        nazwa_clean = "".join(c for c in nazwa if c not in '<>:"/\\|?*')
        return f"{meta.okres_od}_{meta.okres_do}_e-sprawozdanie_{nazwa_clean}.xlsx"
```

### 5. `gui.py` - Interfejs graficzny

```python
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from pathlib import Path
import threading
from parser import SFParser
from converter import XLSXConverter

class SFConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Konwerter Sprawozdań Finansowych XML → XLSX")
        self.root.geometry("700x500")

        self.files_to_process = []
        self.output_dir = None
        self.sf_parser = SFParser()
        self.converter = XLSXConverter()

        self._create_widgets()

    def _create_widgets(self):
        # Frame górny - przyciski wyboru
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="Wybierz plik(i)...",
                   command=self._select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Wybierz folder...",
                   command=self._select_folder).pack(side=tk.LEFT, padx=5)

        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(top_frame, text="Przeszukuj podfoldery",
                        variable=self.recursive_var).pack(side=tk.LEFT, padx=10)

        # Frame środkowy - lista plików
        list_frame = ttk.LabelFrame(self.root, text="Pliki do przetworzenia", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)

        # Przyciski usuwania
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Usuń zaznaczone",
                   command=self._remove_selected).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Wyczyść listę",
                   command=self._clear_list).pack(side=tk.LEFT, padx=5)

        # Frame wyjściowy
        output_frame = ttk.Frame(self.root, padding="10")
        output_frame.pack(fill=tk.X)

        ttk.Label(output_frame, text="Folder wyjściowy:").pack(side=tk.LEFT)
        self.output_label = ttk.Label(output_frame, text="(ten sam co wejściowy)")
        self.output_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Zmień...",
                   command=self._select_output).pack(side=tk.LEFT)

        # Przycisk konwersji
        ttk.Button(self.root, text="KONWERTUJ",
                   command=self._convert).pack(pady=10)

        # Log
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title="Wybierz pliki XML",
            filetypes=[("Pliki XML", "*.xml"), ("Pliki XAdES", "*.xades"),
                       ("Wszystkie pliki", "*.*")]
        )
        for f in files:
            if f not in self.files_to_process:
                self.files_to_process.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder z plikami XML")
        if folder:
            folder_path = Path(folder)
            pattern = "**/*.xml" if self.recursive_var.get() else "*.xml"
            for f in folder_path.glob(pattern):
                if str(f) not in self.files_to_process:
                    self.files_to_process.append(str(f))
                    self.file_listbox.insert(tk.END, f.name)
            # Też .xades
            pattern_xades = pattern.replace('.xml', '.xades')
            for f in folder_path.glob(pattern_xades):
                if str(f) not in self.files_to_process:
                    self.files_to_process.append(str(f))
                    self.file_listbox.insert(tk.END, f.name)

    def _select_output(self):
        folder = filedialog.askdirectory(title="Wybierz folder wyjściowy")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder)

    def _remove_selected(self):
        selected = self.file_listbox.curselection()
        for i in reversed(selected):
            self.file_listbox.delete(i)
            del self.files_to_process[i]

    def _clear_list(self):
        self.file_listbox.delete(0, tk.END)
        self.files_to_process.clear()

    def _log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def _convert(self):
        if not self.files_to_process:
            self._log("Brak plików do przetworzenia!")
            return

        # Uruchom konwersję w osobnym wątku (żeby GUI się nie zawieszało)
        thread = threading.Thread(target=self._convert_thread)
        thread.start()

    def _convert_thread(self):
        success = 0
        errors = []

        for file_path in self.files_to_process:
            path = Path(file_path)
            output_dir = Path(self.output_dir) if self.output_dir else path.parent

            try:
                self._log(f"Przetwarzanie: {path.name}")
                sprawozdanie = self.sf_parser.parse(path)
                output_path = self.converter.convert(sprawozdanie, output_dir)
                self._log(f"  ✓ Zapisano: {output_path.name}")
                success += 1
            except Exception as e:
                self._log(f"  ✗ Błąd: {e}")
                errors.append((path, str(e)))

        self._log(f"\n=== Przetworzono: {success}/{len(self.files_to_process)} plików ===")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SFConverterGUI()
    app.run()
```

---

## Użycie

### Uruchomienie GUI

```bash
python gui.py
```

Interfejs pozwala na:
1. Wybranie pojedynczych plików lub całego folderu
2. Opcjonalne przeszukiwanie podfolderów
3. Wybór folderu wyjściowego
4. Podgląd listy plików do przetworzenia
5. Usuwanie wybranych plików z listy
6. Konwersję z logiem postępu

---

## Decyzje projektowe

| Kwestia | Decyzja |
|---------|---------|
| Interfejs | GUI (tkinter) |
| Podpisy XAdES | Ignorowane (pomijamy ds:Signature) |
| Załączniki binarne | Ignorowane (pomijamy Zalacznik*, TrescZalacznika) |
| Nazwa pliku wyjściowego | Automatyczna: `{od}_{do}_e-sprawozdanie_{firma}.xlsx` |
| Weryfikacja sum | Tak - sprawdzenie Aktywa = Pasywa, wynik w arkuszu |
| Formatowanie XLSX | Proste - bez kolorów i ozdobników |
| Arkusz "Wartość udziału" | Pomijamy (niestandardowe pole) |
| Formaty wyjściowe | 3 formaty: czytelny + surowe + analityczny |
| Identyfikacja pozycji | Pełny kod: `{typ}_{wersja}_{sekcja}_{kod}` |
| Nota podatkowa | Uwzględniona (jeśli występuje w XML) |

---

## Kolejność implementacji

1. `models.py` - struktury danych (z metodą `kod_pelny`)
2. `mappings.py` - mapowania pozycji dla wszystkich sekcji i typów jednostek
3. `parser.py` - parser XML z obsługą namespace'ów i wszystkich sekcji
4. `converter.py` - konwerter XLSX (5 arkuszy)
5. `gui.py` - interfejs graficzny
6. Testy na przykładach z folderów 0, 3, 4, 6, 7

---

## Pliki testowe

| Folder | Typ jednostki | Uwagi |
|--------|---------------|-------|
| 0 | Mikro | Syndyk Surwiło-Rutkowska |
| 3 | Mikro | SAN-AT INVESTMENTS |
| 4 | Inna | PRESTIGE MEDICAL SERVICES |
| 6 | Inna | SUN STONE INTERNATIONAL |
| 7 | Inna | SUN STONE INTERNATIONAL 2021 |

---

## Wymagane biblioteki

```bash
pip install lxml openpyxl
```

`openpyxl` już jest zainstalowana, potrzebna tylko `lxml`.
