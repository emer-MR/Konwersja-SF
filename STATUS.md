# Status projektu

## Aktualny stan

**Etap:** Środowisko uruchomieniowe na Linuksie (Ubuntu 26.04) + aktualizacja dokumentacji. Kod konwertera bez zmian.
**Postęp:** Repozytorium sklonowane na maszynę linuksową, oba komponenty (desktop i web) uruchamiają się z lokalnych środowisk `uv`. README i `web/README.md` opisują ścieżkę linuksową. Brak zmian w logice konwersji.

### Co działa
- **Konwerter desktopowy** (`src/`) - parser XML/XAdES, konwersja do XLSX, GUI tkinter, CLI (`run.py`); wszystkie moduły importują się bez błędu na Pythonie 3.13
- **Tryb wsadowy** - `src/konwertuj.py` przyjmuje ścieżki z wiersza poleceń; grupowanie po podmiocie (NIP/KRS/nazwa), pojedyncze sprawozdanie -> XLSX 8-arkuszowy, 2+ -> XLSX wieloletni
- **Analiza wskaźnikowa** - kalkulator wskaźników niewypłacalności i modeli dyskryminacyjnych (poprawki dla Jednostki Małej w commicie `8e80b41`)
- **Kontrola równowagi bilansu** - konwerter wieloletni ostrzega, gdy Pasywa A + Pasywa B != suma bilansowa
- **Konwerter wieloletni** - 9 arkuszy: Podsumowanie, Bilans, RZiS, Nota podatkowa, Zest. zmian w kapitale, Rach. przepływów, Analiza wskaźnikowa, Dane surowe, Dane analityczne
- **Aplikacja webowa** (`web/`) - FastAPI startuje lokalnie, `GET /` zwraca 200, baza SQLite tworzy się automatycznie; używa `converter_simple.py` (bez wskaźników)
- **Uruchamianie na Linuksie** - `./start.sh` (GUI/CLI) oraz pozycja w menu KDE

### Co jest w trakcie
- Brak aktywnych prac. Środowisko przygotowane, dokumentacja spisana.

### Następne kroki (priorytet)
1. Test konwersji na realnym pliku XML na maszynie linuksowej - klon nie zawiera przykładów (`Przykłady konwersji/`, `Przykłady sprawozdań/` są w `.gitignore`), więc ścieżka XML -> XLSX nie została jeszcze przejechana end-to-end na tym systemie
2. Rozważyć: ekstrakcja amortyzacji dla wariantu kalkulacyjnego RZiS (obecnie tylko porównawczy - poz. B.I)
3. Rozważyć: model D. Hadasik (FD_HD) nadal pokazuje „b/d" - sprawdzić brakujące dane wejściowe
4. Rozważyć: brak testów automatycznych (unit tests) dla całego projektu
5. Rozważyć aktualizację `CLAUDE.md` w repo - opisuje projekt jako zbiór schematów XSD („data structure project, not a software project"), co jest nieaktualne od czasu powstania `src/` i `web/`

### Otwarte problemy
- Brak testów automatycznych (unit tests).
- `CLAUDE.md` w repo opisuje nieistniejącą już strukturę projektu (katalogi XSD zamiast kodu).
- Modele dyskryminacyjne w arkuszu mają wartości liczone wewnętrznie (na sztywno, nie formułami) - do opinii prawnej zaleca się przeliczenie w pliku wzorcowym Kancelarii (`modele dyskryminacyjne dla sprawozdań od 2016 roku.xlsx`).
- Amortyzacja ekstrahowana tylko dla wariantu porównawczego RZiS; dla kalkulacyjnego pozostaje `None`.
- Parser czyta rok kolumny z `okres_do` XML - okresy nietypowe (np. 2023-2024) trafiają do kolumny roku końcowego.
- Przeciągnięcie wielu plików naraz ograniczone limitem długości polecenia Windows - przy dużych partiach przeciągać folder.
- `Konwertuj SF.bat` działa wyłącznie na Windowsie; na Linuksie odpowiednikiem jest wywołanie `src/konwertuj.py` z listą ścieżek (drag & drop pod KDE świadomie nieodwzorowany).

### Zmienione pliki w tej sesji
- `start.sh` (nowy) - uruchamia `src/run.py` przez `.venv`, sam wykrywa katalog repo, przekazuje argumenty do CLI, czytelny błąd gdy brak `.venv`
- `README.md` - sekcja „Instalacja na Linuksie" (uv, powód: brak `pip`/`tkinter`), opis `start.sh`, równoważnik trybu wsadowego na Linuksie, `start.sh` w drzewie projektu
- `web/README.md` - wariant uruchomienia lokalnego przez `uv` w odrębnym środowisku (pin `starlette<0.46`)
- Poza repo (środowisko lokalne, nieśledzone): `.venv/`, `web/.venv/`, `web/.env`, `~/.local/share/applications/konwersja-sf.desktop`

---

## Historia sesji

### 2026-09-07 — Klon na Linuksa, środowiska uv, skróty uruchamiania
- Ukończone:
  - Sklonowano repo do `~/repos/konwersja-sf` (HEAD `8e80b41`, zgodny z `origin/main`).
  - Utworzono dwa środowiska `uv` z Pythonem 3.13: `.venv` (lxml, openpyxl) dla `src/` oraz `web/.venv` (FastAPI, starlette 0.45.3) dla `web/`.
  - Zweryfikowano: `src/run.py --help` działa, wszystkie 9 modułów `src/` importuje się bez błędu, tkinter tworzy okno (XWayland), serwer web zwraca 200 na `GET /` i zakłada bazę SQLite.
  - Utworzono `web/.env` z `.env.example` (własny `SECRET_KEY`, `DEBUG=true`, `RECAPTCHA_ENABLED=false`).
  - Dodano `start.sh` oraz wpis menu KDE `~/.local/share/applications/konwersja-sf.desktop` (walidacja `desktop-file-validate` OK).
  - Zaktualizowano `README.md` i `web/README.md` o ścieżkę linuksową.
- Decyzje:
  - **`uv` zamiast `pip`** - systemowy Python 3.14 w Ubuntu 26.04 nie ma modułu `pip` ani `tkinter`, więc instrukcja z README nie zadziała, a GUI nie wystartuje. Python pobierany przez `uv` ma tkinter wbudowany, co omija `sudo apt install python3-tk`.
  - **Dwa osobne środowiska zamiast jednego** - web pinuje `starlette<0.46`; trzymanie tego pinu z dala od konwertera desktopowego zapobiega przypadkowemu wiązaniu wersji.
  - **Nie odwzorowano drag & drop pod KDE** (service menu Dolphina) - Michał uznał wywołanie `src/konwertuj.py` z listą ścieżek za wystarczające.
  - **Nie przepisano `CLAUDE.md`** mimo nieaktualności - poza zakresem tej sesji, zgłoszone jako otwarty problem.
- Problemy:
  - Konwersji nie przetestowano na realnym pliku - klon nie zawiera żadnego XML-a (katalogi z przykładami są w `.gitignore`). Weryfikacja ograniczyła się do importów, uruchomienia CLI i startu serwera.

### 2026-05-22 (sesja 2) — Naprawa modułu wskaźników + korekta SF Fundacji Vis Salutis
- Ukończone:
  - Test użytkownika ujawnił, że dla Jednostki Małej wskaźniki ROA/ROS/ROE/CaR/PZN pokazywały „b/d", a ROp był błędny. Diagnoza: 3 błędy w ekstraktorze danych `indicators.py`.
  - Naprawiono błąd 1: RZiS Małej (A-J) czytany schematem liter Innej (A-K) - `zysk_strata_netto = rzis_dict.get("K")` zwracało `None`. Rozdzielono gałąź `Mala` od `Inna`.
  - Naprawiono błąd 2: zły klucz środków pieniężnych Małej (`Aktywa_B_III_A_1`) - przywrócił CaR i poprawił wartość likwidacyjną.
  - Naprawiono błąd 3: pole `amortyzacja` nigdy nie ustawiane - dodano ekstrakcję poz. B.I RZiS porównawczego (naprawia też PZN i modele Prusaka/Wierzby/Mączyńskiej; korzysta z tego również Jednostka Inna).
  - Dodano kontrolę równowagi bilansu w konwerterze wieloletnim - automatycznie ostrzega o niezbilansowanych sprawozdaniach.
  - Regeneracja XLSX dla SF Fundacji Vis Salutis 2020/2022/2024; weryfikacja na przykładach Legacy potwierdziła brak regresji dla Innej i Mikro.
  - Nałożono udokumentowaną korektę kapitału własnego (skrypt `korekta_kapitalu_wlasnego.py`) - 14 komórek; bilans równoważy się teraz we wszystkich latach 2019-2024; wskaźniki zgadzają się z briefem QA.
- Decyzje:
  - Wybrano naprawę kodu konwertera + regenerację zamiast jednorazowej łatki XLSX - błąd dotyczy każdej konwersji Jednostki Małej, naprawa w kodzie służy wszystkim przyszłym konwersjom.
  - Korekta kapitału własnego: skorygowano wyłącznie kwotę zbiorczą metodą rezydualną (Aktywa - Zobowiązania), potwierdzoną informacją dodatkową PDF. NIE sfabrykowano rozbicia A.I-A.VII - brief QA proponował A.I = 102 554,48, ale informacja dodatkowa podaje fundusz podstawowy 2 500,00 zł.
  - Kontrola bilansu tylko sygnalizuje defekt, nie koryguje automatycznie - auto-korekta maskowałaby realne błędy danych innych podmiotów (istotne dla analizy niewypłacalności).
  - Deploy webu (czytnik.analizy.io) NIE jest wymagany - `converter_simple.py` zależy tylko od `parser.py`/`models.py` (nietknięte); `indicators.py`/`multi_converter.py` używa wyłącznie konwerter desktopowy.
- Problemy:
  - Sprawozdania XML Fundacji Vis Salutis za 2022 i 2024 mają zaniżoną pozycję zbiorczą „A. Kapitał (fundusz) własny" - defekt danych źródłowych (nie konwertera); bilans nie równoważy się w rozbiciu.
  - Nota podatkowa w SF 2020 ma niespójny zysk brutto (774 578,28 vs 240 101,50 z RZiS) - również defekt źródła.

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
