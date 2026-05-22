# Konwerter Sprawozdań Finansowych XML → XLSX

Narzędzie do konwersji polskich sprawozdań finansowych z formatu XML/XAdES (e-Sprawozdania) do formatu Excel (XLSX).

## Funkcjonalności

- **Parsowanie XML/XAdES** - obsługa podpisanych elektronicznie sprawozdań
- **Wszystkie typy jednostek** - Mikro, Mała, Inna (pełna)
- **Wszystkie wersje schematów** - 1-0, 1-2, 1-3
- **Warianty RZiS** - porównawczy i kalkulacyjny
- **5 arkuszy wyjściowych**:
  1. Bilans - format czytelny
  2. RZiS - format czytelny
  3. Nota podatkowa (jeśli dostępna)
  4. Dane surowe - z kodami pozycji
  5. Dane analityczne - format "długi" do analizy

## Instalacja

```bash
# Sklonuj repozytorium
git clone https://github.com/emer-MR/Konwersja-SF.git
cd Konwersja-SF

# Zainstaluj zależności
pip install -r src/requirements.txt
```

### Wymagania
- Python 3.10+
- lxml >= 4.9.0
- openpyxl >= 3.1.0

## Użycie

### Interfejs graficzny (GUI)

```bash
python src/run.py
```

Lub bezpośrednio:
```bash
python src/gui.py
```

### Wiersz poleceń (CLI)

```bash
# Konwertuj pojedynczy plik
python src/run.py sprawozdanie.xml

# Konwertuj folder
python src/run.py folder/ -o output/

# Rekurencyjnie przeszukuj podfoldery
python src/run.py folder/ -r

# Pomoc
python src/run.py --help
```

### Tryb wsadowy — przeciągnij i upuść (`Konwertuj SF.bat`)

Najszybszy sposób przetworzenia wielu sprawozdań: zaznacz pliki XML/XAdES
i **przeciągnij je na ikonę `Konwertuj SF.bat`** (w katalogu głównym projektu).

Działanie:

- **Sprawozdania tego samego podmiotu** (rozpoznawane po NIP, a w razie braku
  po KRS lub nazwie) trafiają do **jednego pliku Excel z kolumnami kolejnych
  lat** — `RRRR-RRRR_analiza-wieloletnia_Nazwa.xlsx`. Umożliwia to analizę
  porównawczą „rok obok roku". Lata bez własnego sprawozdania są odtwarzane
  z danych porównawczych („rok poprzedni") zawartych w pozostałych plikach.
- **Pojedyncze sprawozdanie** podmiotu → klasyczny plik 8-arkuszowy.
- **Różne podmioty naraz** → osobny plik dla każdego.
- **Załączniki** binarne (PDF z XAdES) są wypakowywane do podfolderów rocznych.

Pliki wynikowe zapisywane są w podfolderze **`_Konwersja_SF`** obok plików
źródłowych. Można też przeciągnąć cały folder (brane są pliki z jego
płaskiego poziomu, bez podfolderów).

Arkusze pliku wieloletniego: Podsumowanie, Bilans, RZiS, Nota podatkowa,
Zest. zmian w kapitale, Rach. przepływów, Analiza wskaźnikowa (wskaźniki
niewypłacalności rok po roku, kolorowane oceną), Dane surowe, Dane analityczne.

## Struktura projektu

```
Konwersja-SF/
├── Konwertuj SF.bat      # Tryb wsadowy — przeciągnij i upuść
├── src/
│   ├── run.py            # Punkt wejścia (GUI/CLI)
│   ├── konwertuj.py      # Punkt wejścia trybu wsadowego (dla .bat)
│   ├── batch.py          # Orkiestrator wsadowy (grupowanie po podmiocie)
│   ├── multi_converter.py # Konwerter wieloletni (kolumny lat)
│   ├── gui.py            # Interfejs graficzny (tkinter)
│   ├── parser.py         # Parser XML sprawozdań
│   ├── converter.py      # Konwerter do XLSX (pojedyncze sprawozdanie)
│   ├── models.py         # Struktury danych
│   ├── mappings.py       # Mapowania kodów → opisy polskie
│   ├── indicators.py     # Kalkulator wskaźników niewypłacalności
│   └── requirements.txt  # Zależności
├── docs/
│   └── struktura_xlsx.md
├── CLAUDE.md             # Instrukcje dla Claude Code
├── PLAN_IMPLEMENTACJI.md
├── STATUS.md             # Stan prac między sesjami
└── README.md
```

## Format wyjściowy

### Nazwa pliku
```
{okres_od}_{okres_do}_e-sprawozdanie_{nazwa_firmy}.xlsx
```
Przykład: `2023-01-01_2023-12-31_e-sprawozdanie_FIRMA SP. Z O.O..xlsx`

### Arkusz "Dane analityczne" (format długi)

Idealny do analizy porównawczej wielu firm:

| firma | nip | krs | typ_jednostki | wersja | okres | sekcja | kod | opis | kwota |
|-------|-----|-----|---------------|--------|-------|--------|-----|------|-------|
| FIRMA | 123... | 000... | Mikro | 1-3 | 2023-12-31 | Bilans | Aktywa | Aktywa razem | 755584.15 |

## Obsługiwane formaty XML

- **Jednostka Mikro** - uproszczone sprawozdanie (~15 pozycji bilansu)
- **Jednostka Mała** - średnia złożoność
- **Jednostka Inna** - pełne sprawozdanie (~100+ pozycji bilansu)

Schematy XML zgodne z wymogami Ministerstwa Finansów (KSeF/e-Sprawozdania).

## Licencja

MIT License

## Autor

Projekt stworzony z pomocą Claude Code.
