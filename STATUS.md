# Status projektu

## Aktualny stan

**Etap:** Po przeglądzie poprawności wskaźników i mapowań (2026-09-25) - kod konwertera poprawiony, web wdrożony z przypiętymi zależnościami.
**Postęp:** Mapowanie RZiS wszystkich typów i wariantów zgodne z XSD (tabela `RZIS_MAP`), kontrola spójności RZiS w arkuszu, poprawione WPZ (art. 11 ust. 5), CaR Innej, konsolidacja wieloletnia przy zmianie typu jednostki, grupowanie podmiotów. Regresja: 29 próbek Legacy + 5 XML mikro. czytnik.analizy.io działa na `44d453c` (healthy, 200).

### Co działa
- **Konwerter desktopowy** (`src/`, `Konwertuj SF.bat` / `src/konwertuj.py`) - pojedyncze SF -> XLSX 8-arkuszowy, 2+ SF podmiotu -> XLSX wieloletni; grupowanie union-find po NIP/KRS (także schemat 1-0 z KRS w elemencie potomnym) i znormalizowanej nazwie
- **Mapowanie RZiS** - Mikro (A - |B| + C - |D| - E = F), Mała i Inna w wariantach porównawczym i kalkulacyjnym wg XSD 1-0/1-2/1-3 (`indicators.py: RZIS_MAP`)
- **Kontrola spójności RZiS** - rozbieżność > 1 zł -> sekcja „UWAGI DO DANYCH” w arkuszu Analiza wskaźnikowa (czerwone)
- **Wskaźniki i modele** - przy KW < 0 pozytywne wyniki modeli FD_* oznaczane jako ostrzegawcze; WZD/CKG/CZob bez fałszywych ocen „optymalna” (Mikro = b/d); WPZ z ostrożnymi komunikatami (art. 11 ust. 4 i 5 p.u.)
- **Konsolidacja wieloletnia** - przy mieszanych typach jednostki / wariantach RZiS osobne bloki „BLOK: ...” zamiast mieszania wierszy po kodzie
- **Aplikacja webowa** (`web/`, https://czytnik.analizy.io, kontener `czytnik-sf` na VPS Hostinger) - wersje zależności przypięte w `web/requirements.txt`; procedura deployu i kontroli po deployu w `web/CLAUDE.md`

### Co jest w trakcie
- Brak rozpoczętych prac. Pozostałe ustalenia przeglądu (I2, I3, I6, I7, I8, I10, I11) - w następnych krokach.

### Następne kroki (priorytet)
1. **Smoke test webu po deployu:** przepuścić jeden XML przez czytnik.analizy.io i raz zalogować się do panelu admina (nowe wersje pakietów, m.in. `bcrypt` 5.0 - dotąd sprawdzony tylko start aplikacji, `GET /` i `/docs`)
2. **I7:** zweryfikować definicje zmiennych modeli Gajdki-Stosa (znak przy X2, X4 = zysk brutto?), Mączyńskiej (X1 = zysk brutto + amortyzacja?), Prusaka 1r/2l (strefy szare), Hadasik (X7) w źródłach z vaultu Wiedza (`Prawo/Niewypłacalność/04-Modele/`) - dopiero potem poprawiać kod
3. **I6:** Altman - wersja Z' (1983) dla spółek nienotowanych (0,717/0,847/3,107/0,420/0,998, progi 1,23/2,90) zamiast współczynników 1968; zysk zatrzymany = Pasywa_A_V + A_VI
4. **I2:** rozbieżności dane porównawcze vs SF roku poprzedniego -> lista w arkuszu Podsumowanie; obsługa `KwotaB1` (przekształcone)
5. **I3:** dwa SF za jeden rok kalendarzowy (np. otwarcie likwidacji) - klucz kolumny = okres, sortowanie po `data_sporzadzenia`, cykle skalowane do długości okresu
6. **I10 / I11 / I8:** przeliczanie WTysiacach w konsolidacji; `raise` dla JednostkaOp i innych nieobsługiwanych typów; Inna bez `Pasywa_B_II` -> ZD = 0 (model poznański b/d)
7. Testy automatyczne - regresja na próbkach z `[Legacy]\...\Przykłady konwersji` jako pytest (skrypty z sesji 2026-09-25 były jednorazowe, w scratchpadzie)

### Otwarte problemy
- **Arkusze wygenerowane przed 2026-09-25 są niewiarygodne** dla: Mikro (wynik ze sprzedaży, modele), Innej (zysk netto przy poz. K, CaR, WPZ), wariantów kalkulacyjnych, WPZ wszystkich typów, konsolidacji z mieszanymi typami - przegenerować przed użyciem w opinii.
- Brak testów automatycznych (unit tests).
- `CLAUDE.md` w repo (główny) opisuje nieistniejącą już strukturę projektu (katalogi XSD zamiast kodu).
- `src/mappings_generated.py` nie kompiluje się (literalne `\n`) - moduł nieimportowany, stan od pierwszego commita.
- Modele dyskryminacyjne w arkuszu liczone wewnętrznie (nie formułami) - do opinii prawnej przeliczać w pliku wzorcowym kancelarii.
- Limit ścieżki 260 znaków w Windows: przy bardzo długich ścieżkach OneDrive + długich nazwach spółek zapis XLSX może paść z Errno 2 (nie regresja).
- W katalogu nadrzędnym `01 Analiza SF/` leży `20260214/` - stara kopia `src/` poza gitem (z błędem znaku Mikro); do archiwizacji/usunięcia decyzją użytkownika.

### Zmienione pliki w tej sesji
- `src/indicators.py` - `RZIS_MAP`, przepisane `extract_financial_data_from_sprawozdanie` (znak kosztów Mikro, mapowanie Mała/Inna × porównawczy/kalkulacyjny, środki pieniężne Innej, zob. wobec powiązanych, zob. handlowe, kontrola spójności -> `uwagi`), `_oznacz_modele_przy_ujemnym_kapitale`, `_oblicz_wskaznik_art_11_ust_5`, `_oblicz_zadluzenie_dlugoterminowe`, cykle (`_zobowiazania_do_cyklu`, `_format_dni`), Wilcox-Gambler Mikro
- `src/converter.py` - sekcja „UWAGI DO DANYCH” w arkuszu wskaźników, zaktualizowane objaśnienia
- `src/multi_converter.py` - segmenty (typ, wariant) w `_merge_section`, bloki „BLOK: ...”, uwagi scalane po latach
- `src/parser.py` - KRS/NIP z elementów potomnych (schemat 1-0)
- `src/batch.py` - `_normalizuj_nazwe`, `_grupuj_podmioty` (union-find)
- `web/requirements.txt` - `sqlalchemy[asyncio]`, jawny `greenlet`, wszystkie wersje przypięte `==`
- `web/CLAUDE.md` - deploy: pełna komenda SSH, lokalna zmiana compose na VPS, obowiązkowa kontrola po deployu, sekcja o przypiętych zależnościach
- `STATUS.md` - ten plik

---

## Historia sesji

### 2026-09-25 — Przegląd poprawności wskaźników, poprawki mapowań, awaria i naprawa webu
- Ukończone:
  - Błąd znaku kosztów Mikro wykryty przy opinii biegłego (arkusz dawał ROp +226% i dodatnie modele u spółki ze stratami) - poprawka `02176e6`.
  - Pełny przegląd kodu (agent, 20+ próbek XML Mikro/Mała/Inna, oba warianty RZiS, XSD 1-0/1-2/1-3) - 6 błędów krytycznych (K1-K6) i 11 istotnych (I1-I11); wdrożone K1-K6, I1, I4, I5 (`b006bd1`), regresja przed/po na 34 plikach, tryb wsadowy 16 podmiotów / 0 błędów.
  - Deploy webu (`b006bd1`) -> kontener w pętli restartów (SQLAlchemy 2.1.0 bez `greenlet`), strona 404; diagnoza z logów, weryfikacja poprawki na zbudowanym obrazie w tymczasowym kontenerze, `0b2bf40` (`sqlalchemy[asyncio]`) + `44d453c` (przypięcie wszystkich wersji); strona przywrócona (healthy, `GET /` 200).
- Decyzje:
  - **Jedna tabela mapowania `RZIS_MAP` (typ, wariant)** zamiast rozgałęzień if/elif - poprzednie błędy (Mała w `8e80b41`, Mikro, Inna, kalkulacyjny) brały się z ręcznego przepisywania liter pozycji; tabela jest sprawdzalna wprost z XSD.
  - **Kontrola spójności RZiS jako uwaga w arkuszu, nie wyjątek** - defekty danych źródłowych (np. SF Fundacji Vis Salutis) muszą być widoczne, ale nie mogą blokować konwersji.
  - **WPZ z ostrożnym komunikatem** - wskaźnik bilansowy nie wyłącza pożyczek wspólników (art. 11 ust. 4 p.u.), a u spółek finansowanych przez wspólników to przesądza o wyniku; arkusz nie może sugerować „niewypłacalności zadłużeniowej” bez tego zastrzeżenia.
  - **Grupowanie union-find** zamiast hierarchii NIP > KRS > nazwa - SF ze schematu 1-0 mają tylko KRS, późniejsze NIP; nazwa zmienia się („w likwidacji”).
  - **Przypięte wersje weba** - `>=` bez przebudowy przez 2 miesiące dawało złudzenie stabilności; każda przebudowa to loteria zależności.
  - I6/I7 odłożone - poprawianie wzorów modeli wymaga źródeł, nie pamięci.
- Problemy:
  - Przestój czytnik.analizy.io ok. 15 min (od 10:42 UTC) po przebudowie obrazu - przyczyna w zależnościach, nie w kodzie konwertera.
  - Skrypt LibreOffice nie działa na Windows; długie ścieżki OneDrive (>260 znaków) wymagały prefiksu `\\?\` lub `subst` przy testach.

#### Szczegóły: poprawka znaku kosztów Mikro (`02176e6`)
- `extract_financial_data_from_sprawozdanie` liczyła dla Mikro wynik ze sprzedaży jako A + B, zakładając ujemne B - w XML koszty (B, D) są dodatnie. Skutek: wynik ze sprzedaży zawyżony o dwukrotność kosztów, ROp > 200% przy stratach, fałszywie dobre modele (poznański, Prusak, Wierzba, Altman). Teraz WS = A - |B|, WDO = WS + C - |D|.
- Nowe `_oznacz_modele_przy_ujemnym_kapitale`: przy KW < 0 pozytywny wynik modelu (FD_*) dostaje ocenę ostrzegawczą z uwagą o nieinterpretowalności.
- Regresja na realnych XML (Strefa Klasyka, mikro 2018-2022, sprawa XII GC 90/26): ROp 2019 -26,18% (było +226%), FD_P -12,56 (było +4,35), FD_A -4,65 (było +7,75). **Arkusze mikro wygenerowane przed tą poprawką należy przegenerować.**

#### Szczegóły: przegląd mapowań i wskaźników (`b006bd1`)
Wynik przeglądu kodu pod kątem błędów analogicznych do znaku kosztów Mikro. Regresja: 29 próbek z `[Legacy]\...\Przykłady konwersji`, `Przykłady sprawozdań`, `Test`, `Test 2`, `Error - Lavinia` + 5 XML Strefa Klasyka; tryb wsadowy (16 podmiotów, 16 XLSX, 0 błędów) i pojedynczy bez wyjątków. **Arkusze Jednostek Innych (zwłaszcza z poz. K w RZiS) i wariantów kalkulacyjnych wygenerowane wcześniej należy przegenerować.**
- **K1+K2 `indicators.py` - tabela `RZIS_MAP` (typ, wariant) wg XSD.** Inna porównawczy: zysk netto = L (wcześniej K = „pozostałe obowiązkowe zmniejszenia” -> zysk netto 0 w 5 próbkach, np. SUN STONE 2022 -2 293 954,16 zł jako 0). Wariant kalkulacyjny Małej (E/F-G/H-I/J/K/L) i Innej (F/G-H/I/J-K/L/M/N/O) nie jest już mapowany jak porównawczy (MIFLEX: WS -1 882 700,11 zamiast +62 898,85; AMONTEX: ZN -313 826,55 zamiast 0). Zysk netto bez łańcucha `or`. Koszty operacyjne kalkulacyjne = suma B+C+D (Mała) / B+D+E (Inna).
- **Kontrola spójności RZiS** (brutto - podatek - obowiązkowe zmniejszenia = netto; Mikro: A - |B| + C - |D| - E = F; tolerancja 1 zł) -> `DaneFinansowe.uwagi`, wyświetlane jako „UWAGI DO DANYCH” w arkuszu Analiza wskaźnikowa (pojedynczy i wieloletni). Brak wyjątków.
- **K3 WPZ (art. 11 ust. 5)** - Mikro: odejmowane rezerwy `Pasywa_B_1`; Mała/Inna: rezerwy nie są odejmowane drugi raz (ZO = ZD + ZK już bez rezerw); Inna: zob. wobec jedn. powiązanych = `Pasywa_B_II_1` + `Pasywa_B_III_1` (wcześniej nieistniejące kody z małą literą). Nowe komunikaty: wzruszalne domniemanie bilansowe, brak wyłączenia pożyczek wspólników / zobowiązań przyszłych (art. 11 ust. 4), dla Mikro/Małej zob. wobec powiązanych niewyłączone, ≤ 1 nie przesądza o braku przesłanki z ust. 2.
- **K4** - środki pieniężne Innej = `Aktywa_B_III_1_C` (awaryjnie `_C_1`), bez fallbacku na całe inwestycje KT (SUN STONE CaR 0,32 -> 0,06). Mała bez zmian (`Aktywa_B_III_A_1`).
- **K5 `multi_converter.py`** - przy różnych typach jednostki (bilans, RZiS, noty) lub wariantach RZiS wiersze łączone tylko w obrębie segmentu (typ[, wariant]) i prezentowane w osobnych blokach z nagłówkiem „BLOK: ...”; także w Dane surowe (etykieta sekcji z typem/wariantem). Grupy jednorodne - bez zmian. Uwagi do danych w arkuszu wskaźników wieloletnich.
- **K6** - `DaneFinansowe.typ_jednostki`; WZD: Mikro = brak danych, KW ≤ 0 = krytyczna/nieinterpretowalny; CZob z zobowiązań z tyt. dostaw i usług (Mała `Pasywa_B_III_B`, Inna `B_III_1_A + B_III_2_A + B_III_3_D`, awaryjnie ZK z adnotacją), Mikro = brak danych; CKG: Mikro = brak danych, nigdy „optymalna” przy CZob > 90 dni lub CR < 1.
- **I1** - `parser.py`: KRS/NIP z elementów potomnych (schemat 1-0); `batch.py`: grupowanie union-find po NIP/KRS, sprawozdania bez identyfikatorów po znormalizowanej nazwie (bez „w likwidacji/upadłości”, form sp. z o.o./S.A.; formy komandytowe zachowane). Strefa 2018 trafia teraz do grupy 2018-2022.
- **I4** - Mikro: `krotkoterminowe_rmk = None` (Aktywa_D to udziały własne), inne AO = B - B_1 - B_2 w WL jako „Inne AO” 50%, `zysk_strata_brutto = F + E`, nota o ograniczeniach Mikro w arkuszu. **I5** - `abs()` na amortyzacji Mikro. Kosmetyka: wartość 0 dni nie jest już wyświetlana jako „b/d”.
- **Web:** `parser.py` jest współdzielony z `web/` (zmiana KRS/NIP) - przy najbliższym deployu przebudować obraz; `web/` nie był modyfikowany.
- **Pozostało z przeglądu:** I2 (rozbieżności dane porównawcze vs SF roku poprzedniego, ignorowane KwotaB1), I3 (duplikaty roku / okresy niepełne, sortowanie po `data_sporzadzenia`, 365 dni dla okresów < 12 mies.), I6 (Altman - współczynniki wersji 1968 zamiast Z' dla nienotowanych), I7 (weryfikacja definicji Gajdki-Stosa, Mączyńskiej, Prusaka 1r/2l, Hadasik w źródłach), I10 (brak przeliczania WTysiacach w konsolidacji), I11 (JednostkaOp po cichu jako „Inna” z pustymi danymi). Ponadto: `src/mappings_generated.py` nie kompiluje się (literalne `\n` - stan sprzed tej sesji, moduł nieimportowany); Inna bez poz. `Pasywa_B_II` -> ZD None -> model poznański b/d.

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
