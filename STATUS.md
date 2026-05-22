# Status projektu

## Aktualny stan

**Etap:** Konwerter desktopowy (src/) - dodano tryb wsadowy "przeciągnij i upuść" z konsolidacją wieloletnią.
**Postęp:** Funkcja drag & drop ukończona i przetestowana na prawdziwych sprawozdaniach. Aplikacja webowa (web/) bez zmian, wdrożona produkcyjnie (czytnik.analizy.io).

### Co działa
- **Konwerter desktopowy** (`src/`) - parser XML/XAdES, konwersja do XLSX, GUI tkinter, CLI (`run.py`), kalkulator wskaźników niewypłacalności (`indicators.py`)
- **Tryb wsadowy drag & drop** - przeciągnięcie plików XML/XAdES na `Konwertuj SF.bat`:
  - grupowanie sprawozdań po podmiocie (NIP, awaryjnie KRS, awaryjnie nazwa)
  - 1 sprawozdanie podmiotu -> klasyczny XLSX 8-arkuszowy (`converter.py`)
  - 2+ sprawozdania podmiotu -> jeden XLSX wieloletni z kolumnami lat (`multi_converter.py`)
  - różne podmioty naraz -> osobny plik dla każdego
  - wyniki w podfolderze `_Konwersja_SF` obok plików źródłowych
  - załączniki binarne (PDF z XAdES) wypakowywane do `zalaczniki_<nazwa>/<rok>/`
- **Konwerter wieloletni** generuje arkusze: Podsumowanie, Bilans, RZiS, Nota podatkowa, Zest. zmian w kapitale, Rach. przepływów, Analiza wskaźnikowa (wskaźniki rok po roku, kolorowane oceną), Dane surowe, Dane analityczne
- **Aplikacja webowa** (`web/`) - FastAPI, Docker, deployment Hostinger/Mikrus

### Co jest w trakcie
- Brak aktywnych prac - tryb wsadowy zakończony i przetestowany.

### Następne kroki (priorytet)
1. Testy użytkownika trybu wsadowego na własnym zbiorze sprawozdań (w toku po stronie użytkownika)
2. Ewentualne poprawki na podstawie zgłoszeń z testów
3. Rozważyć: rekurencyjne przeszukiwanie podfolderów przy przeciągnięciu folderu (obecnie tylko płaski poziom)
4. Rozważyć: brak testów automatycznych (unit tests) dla całego projektu

### Otwarte problemy
- Brak testów automatycznych (unit tests).
- Parser czyta rok kolumny z `okres_do` XML - jeśli sprawozdanie obejmuje okres nietypowy (np. EKOMEL: `2023-01-01 - 2024-12-31`), kolumna otrzymuje rok 2024. Pełny okres widoczny w arkuszu "Podsumowanie" - zachowanie poprawne, ale warte uwagi przy interpretacji.
- Przeciągnięcie wielu plików naraz ograniczone limitem długości polecenia Windows - przy dużych partiach przeciągać folder.

### Zmienione pliki w tej sesji
- `Konwertuj SF.bat` (nowy) - plik drag & drop, wykrywa `python`/`py`, wywołuje `src/konwertuj.py`
- `src/konwertuj.py` (nowy) - punkt wejścia dla .bat, wymusza UTF-8 na konsoli, przekazuje argv do batch
- `src/batch.py` (nowy) - orkiestrator: zbieranie plików, grupowanie po podmiocie (`_klucz_podmiotu`), wybór konwertera, `run_batch()`
- `src/multi_converter.py` (nowy) - klasa `MultiYearConverter`, łączenie sekcji wielu sprawozdań w kolumny lat (`_merge_section`), 9 arkuszy wynikowych
- `README.md` - dodano sekcję o trybie wsadowym
- `STATUS.md` (nowy) - ten plik

---

## Historia sesji

### 2026-05-22 — Tryb wsadowy drag & drop z konsolidacją wieloletnią
- Ukończone: nowa funkcja - przeciąganie plików XML/XAdES na `Konwertuj SF.bat`. Sprawozdania tego samego podmiotu łączone w jeden Excel z kolumnami kolejnych lat. Utworzono `multi_converter.py`, `batch.py`, `konwertuj.py`, `Konwertuj SF.bat`. Dodano sekcję do `README.md`, utworzono `STATUS.md`.
- Decyzje:
  - Wyniki w podfolderze `_Konwersja_SF` obok plików źródłowych (wybór użytkownika) - czysto, łatwo znaleźć.
  - Pojedyncze sprawozdanie podmiotu używa istniejącego `XLSXConverter` (pełny 8-arkuszowy, wybór użytkownika) - sprawdzony, bogatszy wynik niż format wieloletni dla 1 roku.
  - Grupowanie po znormalizowanym NIP (awaryjnie KRS, nazwa) - NIP jest najpewniejszym identyfikatorem, odporny na rozbieżności KRS/nazwy między latami.
  - Nie modyfikowano `parser.py`, `converter.py`, `indicators.py`, `gui.py`, `run.py` - GUI i dotychczasowe CLI działają bez zmian, mniejsze ryzyko regresji.
  - Konwerter wieloletni odtwarza lata bez własnego sprawozdania z danych porównawczych "rok poprzedni" (`kwota_poprzednia`); dane bieżące mają priorytet nad porównawczymi.
  - Analiza wskaźnikowa w trybie wieloletnim: kolumna tylko dla lat z pełnym sprawozdaniem (wskaźniki wymagają kompletu danych).
- Problemy: brak - wszystkie 4 scenariusze testowe przeszły (multi-year SAN-AT 3 pliki -> 5 kolumn lat, pojedynczy plik -> 8 arkuszy, EKOMEL XAdES + załączniki, dwa różne podmioty naraz).
