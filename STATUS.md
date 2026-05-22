# Status projektu

## Aktualny stan

**Etap:** Konwerter desktopowy (src/) - naprawa modułu analizy wskaźnikowej oraz kontrola równowagi bilansu. Tryb wsadowy i wieloletni gotowe.
**Postęp:** Naprawiono 3 błędy ekstrakcji danych do wskaźników (dotyczyły Jednostki Małej). Konwerter wykrywa i sygnalizuje niezbilansowane sprawozdania. Zmiany w `src/` niezacommitowane.

### Co działa
- **Konwerter desktopowy** (`src/`) - parser XML/XAdES, konwersja do XLSX, GUI tkinter, CLI (`run.py`)
- **Tryb wsadowy drag & drop** - przeciąganie plików XML/XAdES na `Konwertuj SF.bat`, grupowanie po podmiocie (NIP/KRS/nazwa), pojedyncze sprawozdanie -> XLSX 8-arkuszowy, 2+ -> XLSX wieloletni
- **Analiza wskaźnikowa** - kalkulator wskaźników niewypłacalności i modeli dyskryminacyjnych; po naprawie poprawnie liczy ROA/ROS/ROE/ROp/CaR/PZN także dla Jednostki Małej (wcześniej „b/d")
- **Kontrola równowagi bilansu** - konwerter wieloletni ostrzega, gdy Pasywa A + Pasywa B != suma bilansowa (defekt danych źródłowych)
- **Konwerter wieloletni** - 9 arkuszy: Podsumowanie, Bilans, RZiS, Nota podatkowa, Zest. zmian w kapitale, Rach. przepływów, Analiza wskaźnikowa, Dane surowe, Dane analityczne
- **Aplikacja webowa** (`web/`) - FastAPI, Docker, czytnik.analizy.io; używa `converter_simple.py` (bez wskaźników) - niezależna od zmian z tej sesji

### Co jest w trakcie
- Brak aktywnych prac - naprawa zakończona i zweryfikowana (Mała naprawiona, Inna i Mikro bez regresji).

### Następne kroki (priorytet)
1. Zacommitować zmiany: `src/indicators.py`, `src/multi_converter.py` (git status: oba `M`)
2. Rozważyć: ekstrakcja amortyzacji dla wariantu kalkulacyjnego RZiS (obecnie tylko porównawczy - poz. B.I)
3. Rozważyć: model D. Hadasik (FD_HD) nadal pokazuje „b/d" - sprawdzić brakujące dane wejściowe
4. Testy użytkownika trybu wsadowego na własnym zbiorze sprawozdań (z poprzedniej sesji, w toku)
5. Rozważyć: brak testów automatycznych (unit tests) dla całego projektu

### Otwarte problemy
- Brak testów automatycznych (unit tests).
- Modele dyskryminacyjne w arkuszu mają wartości liczone wewnętrznie (na sztywno, nie formułami) - do opinii prawnej zaleca się przeliczenie w pliku wzorcowym Kancelarii (`modele dyskryminacyjne dla sprawozdań od 2016 roku.xlsx`).
- Amortyzacja ekstrahowana tylko dla wariantu porównawczego RZiS; dla kalkulacyjnego pozostaje `None`.
- Parser czyta rok kolumny z `okres_do` XML - okresy nietypowe (np. 2023-2024) trafiają do kolumny roku końcowego.
- Przeciągnięcie wielu plików naraz ograniczone limitem długości polecenia Windows - przy dużych partiach przeciągać folder.

### Zmienione pliki w tej sesji
- `src/indicators.py` - 3 poprawki w `extract_financial_data_from_sprawozdanie`:
  1. RZiS Jednostki Małej (10-pozycyjny A-J) czytany był schematem Jednostki Innej (11-pozycyjny A-K) -> dodano osobną gałąź `Mala` (zysk netto = poz. J, brutto = H, podatek = I; wynik operacyjny liczony C+D-E)
  2. Zły klucz środków pieniężnych Małej -> `Aktywa_B_III_A_1`
  3. Pole `amortyzacja` nigdy nie wypełniane -> ekstrakcja poz. B.I RZiS (wariant porównawczy, dotyczy Małej i Innej)
- `src/multi_converter.py` - kontrola równowagi bilansu w `_zbierz_ostrzezenia` (ostrzeżenie przy niezbilansowanym rozbiciu pasywów)
- `korekta_kapitalu_wlasnego.py` (nowy, w folderze danych klienta `Fundacja VIS Salutis/SF-XML/`) - skrypt nakładający udokumentowaną korektę kapitału własnego na wynikowy XLSX; zapis audytowy, odtwarzalny po regeneracji

---

## Historia sesji

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
