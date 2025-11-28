# Struktura wynikowych plików XLSX

Dokument opisuje strukturę plików Excel generowanych przez konwerter XML → XLSX dla polskich sprawozdań finansowych.

## Przegląd arkuszy

Każdy plik XLSX zawiera **5 arkuszy**:

| Nr | Arkusz | Przeznaczenie |
|----|--------|---------------|
| 1 | Bilans | Tradycyjna prezentacja bilansu |
| 2 | RZiS | Rachunek Zysków i Strat |
| 3 | Nota podatkowa | Informacje podatkowe |
| 4 | Dane surowe | Płaska tabela do analiz |
| 5 | Dane analityczne | Format "long" do agregacji |

---

## 1. Bilans

Tradycyjna prezentacja bilansu z hierarchią wizualną.

### Struktura kolumn

| Kolumna | Szerokość | Zawartość |
|---------|-----------|-----------|
| Kod | 15 | Kod pozycji (np. A, A_I, A_I_1) |
| Opis | 60 | Pełna nazwa pozycji z wcięciem |
| Rok bieżący | 20 | Kwota za rok bieżący |
| Rok poprzedni | 20 | Kwota za rok poprzedni |

### Wcięcia hierarchiczne

Wcięcia w kolumnie "Opis" są proporcjonalne do poziomu zagnieżdżenia:
- Poziom 0: brak wcięcia (np. "A. Aktywa trwałe")
- Poziom 1: 3 spacje (np. "   A.I. Wartości niematerialne i prawne")
- Poziom 2: 6 spacji (np. "      A.I.1. Koszty zakończonych prac rozwojowych")

---

## 2. RZiS (Rachunek Zysków i Strat)

Struktura identyczna jak Bilans.

### Warianty RZiS

W zależności od typu jednostki i wybranego wariantu:

| Typ jednostki | Warianty |
|---------------|----------|
| Inna | Porównawczy (12 głównych pozycji) lub Kalkulacyjny (15 pozycji) |
| Mała | Porównawczy (10 pozycji) lub Kalkulacyjny (12 pozycji) |
| Mikro | Uproszczony (7 głównych pozycji: A-G) |

---

## 3. Nota podatkowa

Zawiera pozycje noty podatkowej (jeśli obecne w źródłowym XML).

| Kod | Opis |
|-----|------|
| P_ID_1 | Różnica między podstawą opodatkowania a wynikiem brutto |
| P_ID_2 | Inne zmiany podstawy opodatkowania |
| P_ID_3 | Podstawa opodatkowania podatkiem dochodowym |
| P_ID_4 | Podatek dochodowy |

---

## 4. Dane surowe

**Cel:** Płaska tabela umożliwiająca łatwe filtrowanie, sortowanie i tworzenie tabel przestawnych (pivot tables).

### Struktura kolumn

| Kolumna | Typ | Opis | Przykład |
|---------|-----|------|----------|
| sekcja | tekst | Sekcja sprawozdania | `Aktywa`, `Pasywa`, `RZiS` |
| kod | tekst | Kod pozycji z XSD | `A`, `A_I`, `A_I_1` |
| opis | tekst | Pełny opis pozycji | `Aktywa trwałe` |
| rok_biezacy | liczba | Kwota za rok bieżący | `1234567.89` |
| rok_poprzedni | liczba | Kwota za rok poprzedni | `1000000.00` |

### Metodyka generowania

```python
for poz in wszystkie_pozycje:
    dane_surowe.append([
        poz.sekcja,           # np. "Aktywa"
        poz.kod,              # np. "A_I_1"
        poz.opis,             # np. "Wartości niematerialne i prawne"
        poz.kwota_biezaca,    # Decimal
        poz.kwota_poprzednia  # Decimal
    ])
```

### Zastosowania

- Filtrowanie po sekcji (np. tylko Aktywa)
- Pivot tables z agregacją
- Szybkie wyszukiwanie pozycji
- Import do innych narzędzi analitycznych

---

## 5. Dane analityczne

**Cel:** Format "long" (tidy data) idealny do agregacji wielu sprawozdań, analiz czasowych i porównań między firmami.

### Struktura kolumn

| Kolumna | Typ | Opis | Przykład |
|---------|-----|------|----------|
| firma | tekst | Nazwa firmy | `QUICK SOLUTIONS SP. Z O.O.` |
| nip | tekst | NIP firmy | `5213760852` |
| krs | tekst | Numer KRS | `0000574402` |
| typ_jednostki | tekst | Typ jednostki | `JednostkaMikro`, `JednostkaMala`, `JednostkaInna` |
| wersja | tekst | Wersja schematu | `1-2` |
| okres | tekst | Rok sprawozdawczy | `2023`, `2022` |
| sekcja | tekst | Sekcja | `Aktywa`, `RZiS` |
| kod | tekst | Kod pozycji | `A_I` |
| kod_pelny | tekst | Unikalny identyfikator | `JednostkaMikro_1-2_Aktywa_A_I` |
| opis | tekst | Opis pozycji | `Aktywa trwałe` |
| kwota | liczba | Wartość | `500000.00` |

### Metodyka generowania

Każda pozycja finansowa generuje **2 wiersze** (rok bieżący + rok poprzedni):

```python
for poz in wszystkie_pozycje:
    # Wiersz dla roku bieżącego
    dane.append([
        firma, nip, krs, typ_jednostki, wersja,
        rok_biezacy,                    # np. "2023"
        poz.sekcja, poz.kod,
        poz.kod_pelny(),                # unikalny klucz
        poz.opis,
        poz.kwota_biezaca
    ])

    # Wiersz dla roku poprzedniego
    dane.append([
        firma, nip, krs, typ_jednostki, wersja,
        rok_poprzedni,                  # np. "2022"
        poz.sekcja, poz.kod,
        poz.kod_pelny(),
        poz.opis,
        poz.kwota_poprzednia
    ])
```

### Klucz `kod_pelny`

Unikalny identyfikator pozycji uwzględniający kontekst:

```python
def kod_pelny(self) -> str:
    return f"{self.typ_jednostki}_{self.wersja}_{self.sekcja}_{self.kod}"
```

**Przykłady:**
- `JednostkaMikro_1-2_Aktywa_A`
- `JednostkaInna_1-3_RZiS_B_I`
- `JednostkaMala_1-2_Pasywa_B_III_3_A`

### Zastosowania

- **Łączenie wielu sprawozdań** - format umożliwia proste dołączanie kolejnych wierszy
- **Analizy czasowe** - kolumna `okres` pozwala na śledzenie zmian rok do roku
- **Porównania między firmami** - kolumny identyfikacyjne (firma, nip, krs)
- **Agregacje** - łatwe sumowanie po sekcjach, typach jednostek
- **Power BI / Tableau** - format idealny do narzędzi BI

---

## Typy jednostek i ich złożoność

| Typ | Bilans (pozycje) | RZiS (pozycje) | Przeznaczenie |
|-----|------------------|----------------|---------------|
| Mikro | ~13 | ~16 | Najmniejsze podmioty |
| Mała | ~46 | ~20-25 | Małe przedsiębiorstwa |
| Inna | ~148 | ~35-45 | Średnie i duże podmioty |

---

## Sugestie dla dalszej rozbudowy

### Proponowane dodatkowe arkusze

1. **Wskaźniki** - obliczone wskaźniki finansowe:
   - Rentowność (ROA, ROE, ROS)
   - Płynność (bieżąca, szybka, gotówkowa)
   - Zadłużenie (ogólne, kapitału własnego)
   - Sprawność działania (rotacje)

2. **Porównania YoY** - dynamika rok do roku:
   - Zmiana absolutna (rok bieżący - rok poprzedni)
   - Zmiana procentowa
   - Indeksy (rok poprzedni = 100)

3. **Benchmark** - porównanie z grupą:
   - Percentyle branżowe
   - Odchylenia od średniej
   - Ranking w grupie

4. **Dashboard** - podsumowanie wizualne:
   - Kluczowe KPI
   - Wykresy struktury
   - Trend wieloletni

---

## Precyzja danych

- Wszystkie kwoty przechowywane jako `Decimal` (precyzja finansowa)
- Brak zaokrągleń podczas przetwarzania
- Formatowanie w Excel: 2 miejsca po przecinku
- Obsługa kwot w złotych (`WZlotych`) i tysiącach (`WTysiacach`)
