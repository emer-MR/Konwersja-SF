"""
Mapowania pozycji finansowych - wygenerowane z plików XSD.

Ten plik zawiera słowniki mapujące kody pozycji XML na opisy czytelne dla człowieka.
Wygenerowano automatycznie na podstawie schematów XSD Ministerstwa Finansów.
"""

from typing import Optional

# =============================================================================
# JEDNOSTKA INNA
# =============================================================================

BILANS_INNA = {
    # AKTYWA
    "Aktywa_A": "A. Aktywa trwałe",
    "Aktywa_A_I": "A.I. Wartości niematerialne i prawne",
    "Aktywa_A_I_1": "A.I.1. Koszty zakończonych prac rozwojowych",
    "Aktywa_A_I_2": "A.I.2. Wartość firmy",
    "Aktywa_A_I_3": "A.I.3. Inne wartości niematerialne i prawne",
    "Aktywa_A_I_4": "A.I.4. Zaliczki na wartości niematerialne i prawne",
    "Aktywa_A_II": "A.II. Rzeczowe aktywa trwałe",
    "Aktywa_A_II_1": "A.II.1. Środki trwałe",
    "Aktywa_A_II_1_A": "A.II.1.A. grunty (w tym prawo użytkowania wieczystego gruntu)",
    "Aktywa_A_II_1_B": "A.II.1.B. budynki, lokale, prawa do lokali i obiekty inżynierii lądowej i wodnej",
    "Aktywa_A_II_1_C": "A.II.1.C. urządzenia techniczne i maszyny",
    "Aktywa_A_II_1_D": "A.II.1.D. środki transportu",
    "Aktywa_A_II_1_E": "A.II.1.E. inne środki trwałe",
    "Aktywa_A_II_2": "A.II.2. Środki trwałe w budowie",
    "Aktywa_A_II_3": "A.II.3. Zaliczki na środki trwałe w budowie",
    "Aktywa_A_III": "A.III. Należności długoterminowe",
    "Aktywa_A_III_1": "A.III.1. Od jednostek powiązanych",
    "Aktywa_A_III_2": "A.III.2. Od pozostałych jednostek, w których jednostka posiada zaangażowanie w kapitale",
    "Aktywa_A_III_3": "A.III.3. Od pozostałych jednostek",
    "Aktywa_A_IV": "A.IV. Inwestycje długoterminowe",
    "Aktywa_A_IV_1": "A.IV.1. Nieruchomości",
    "Aktywa_A_IV_2": "A.IV.2. Wartości niematerialne i prawne",
    "Aktywa_A_IV_3": "A.IV.3. Długoterminowe aktywa finansowe",
    "Aktywa_A_IV_3_A": "A.IV.3.A. w jednostkach powiązanych",
    "Aktywa_A_IV_3_A_1": "A.IV.3.A.1. – udziały lub akcje",
    "Aktywa_A_IV_3_A_2": "A.IV.3.A.2. – inne papiery wartościowe",
    "Aktywa_A_IV_3_A_3": "A.IV.3.A.3. – udzielone pożyczki",
    "Aktywa_A_IV_3_A_4": "A.IV.3.A.4. – inne długoterminowe aktywa finansowe",
    "Aktywa_A_IV_3_B": "A.IV.3.B. w pozostałych jednostkach, w których jednostka posiada zaangażowanie w kapitale",
    "Aktywa_A_IV_3_B_1": "A.IV.3.B.1. – udziały lub akcje",
    "Aktywa_A_IV_3_B_2": "A.IV.3.B.2. – inne papiery wartościowe",
    "Aktywa_A_IV_3_B_3": "A.IV.3.B.3. – udzielone pożyczki",
    "Aktywa_A_IV_3_B_4": "A.IV.3.B.4. – inne długoterminowe aktywa finansowe",
    "Aktywa_A_IV_3_C": "A.IV.3.C. w pozostałych jednostkach",
    "Aktywa_A_IV_3_C_1": "A.IV.3.C.1. – udziały lub akcje",
    "Aktywa_A_IV_3_C_2": "A.IV.3.C.2. – inne papiery wartościowe",
    "Aktywa_A_IV_3_C_3": "A.IV.3.C.3. – udzielone pożyczki",
    "Aktywa_A_IV_3_C_4": "A.IV.3.C.4. – inne długoterminowe aktywa finansowe",
    "Aktywa_A_IV_4": "A.IV.4. Inne inwestycje długoterminowe",
    "Aktywa_A_V": "A.V. Długoterminowe rozliczenia międzyokresowe",
    "Aktywa_A_V_1": "A.V.1. Aktywa z tytułu odroczonego podatku dochodowego",
    "Aktywa_A_V_2": "A.V.2. Inne rozliczenia międzyokresowe",
    "Aktywa": "Aktywa razem",
    "Aktywa_B": "B. Aktywa obrotowe",
    "Aktywa_B_I": "B.I. Zapasy",
    "Aktywa_B_I_1": "B.I.1. Materiały",
    "Aktywa_B_I_2": "B.I.2. Półprodukty i produkty w toku",
    "Aktywa_B_I_3": "B.I.3. Produkty gotowe",
    "Aktywa_B_I_4": "B.I.4. Towary",
    "Aktywa_B_I_5": "B.I.5. Zaliczki na dostawy i usługi",
    "Aktywa_B_II": "B.II. Należności krótkoterminowe",
    "Aktywa_B_II_1": "B.II.1. Należności od jednostek powiązanych",
    "Aktywa_B_II_1_A": "B.II.1.A. z tytułu dostaw i usług, o okresie spłaty:",
    "Aktywa_B_II_1_A_1": "B.II.1.A.1. – do 12 miesięcy",
    "Aktywa_B_II_1_A_2": "B.II.1.A.2. – powyżej 12 miesięcy",
    "Aktywa_B_II_1_B": "B.II.1.B. inne",
    "Aktywa_B_II_2": "B.II.2. Należności od pozostałych jednostek, w których jednostka posiada zaangażowanie w kapitale",
    "Aktywa_B_II_2_A": "B.II.2.A. z tytułu dostaw i usług, o okresie spłaty:",
    "Aktywa_B_II_2_A_1": "B.II.2.A.1. – do 12 miesięcy",
    "Aktywa_B_II_2_A_2": "B.II.2.A.2. – powyżej 12 miesięcy",
    "Aktywa_B_II_2_B": "B.II.2.B. inne",
    "Aktywa_B_II_3": "B.II.3. Należności od pozostałych jednostek",
    "Aktywa_B_II_3_A": "B.II.3.A. z tytułu dostaw i usług, o okresie spłaty:",
    "Aktywa_B_II_3_A_1": "B.II.3.A.1. – do 12 miesięcy",
    "Aktywa_B_II_3_A_2": "B.II.3.A.2. – powyżej 12 miesięcy",
    "Aktywa_B_II_3_B": "B.II.3.B. z tytułu podatków, dotacji, ceł, ubezpieczeń społecznych i zdrowotnych oraz innych tytułów publicznoprawnych",
    "Aktywa_B_II_3_C": "B.II.3.C. inne",
    "Aktywa_B_II_3_D": "B.II.3.D. dochodzone na drodze sądowej",
    "Aktywa_B_III": "B.III. Inwestycje krótkoterminowe",
    "Aktywa_B_III_1": "B.III.1. Krótkoterminowe aktywa finansowe",
    "Aktywa_B_III_1_A": "B.III.1.A. w jednostkach powiązanych",
    "Aktywa_B_III_1_A_1": "B.III.1.A.1. – udziały lub akcje",
    "Aktywa_B_III_1_A_2": "B.III.1.A.2. – inne papiery wartościowe",
    "Aktywa_B_III_1_A_3": "B.III.1.A.3. – udzielone pożyczki",
    "Aktywa_B_III_1_A_4": "B.III.1.A.4. – inne krótkoterminowe aktywa finansowe",
    "Aktywa_B_III_1_B": "B.III.1.B. w pozostałych jednostkach",
    "Aktywa_B_III_1_B_1": "B.III.1.B.1. – udziały lub akcje",
    "Aktywa_B_III_1_B_2": "B.III.1.B.2. – inne papiery wartościowe",
    "Aktywa_B_III_1_B_3": "B.III.1.B.3. – udzielone pożyczki",
    "Aktywa_B_III_1_B_4": "B.III.1.B.4. – inne krótkoterminowe aktywa finansowe",
    "Aktywa_B_III_1_C": "B.III.1.C. Środki pieniężne i inne aktywa pieniężne",
    "Aktywa_B_III_1_C_1": "B.III.1.C.1. – środki pieniężne w kasie i na rachunkach",
    "Aktywa_B_III_1_C_2": "B.III.1.C.2. – inne środki pieniężne",
    "Aktywa_B_III_1_C_3": "B.III.1.C.3. – inne aktywa pieniężne",
    "Aktywa_B_III_2": "B.III.2. Inne inwestycje krótkoterminowe",
    "Aktywa_B_IV": "B.IV. Krótkoterminowe rozliczenia międzyokresowe",
    "Aktywa_C": "C. Należne wpłaty na kapitał (fundusz) podstawowy",
    "Aktywa_D": "D. Udziały (akcje) własne",

    # PASYWA
    "Pasywa_A": "A. Kapitał (fundusz) własny",
    "Pasywa_A_I": "A.I. Kapitał (fundusz) podstawowy",
    "Pasywa_A_II": "A.II. Kapitał (fundusz) zapasowy, w tym:",
    "Pasywa_A_II_1": "A.II.1. – nadwyżka wartości sprzedaży (wartości emisyjnej) nad wartością nominalną udziałów (akcji)",
    "Pasywa_A_III": "A.III. Kapitał (fundusz) z aktualizacji wyceny, w tym:",
    "Pasywa_A_III_1": "A.III.1. – z tytułu aktualizacji wartości godziwej",
    "Pasywa_A_IV": "A.IV. Pozostałe kapitały (fundusze) rezerwowe, w tym:",
    "Pasywa_A_IV_1": "A.IV.1. – tworzone zgodnie z umową (statutem) spółki",
    "Pasywa_A_IV_2": "A.IV.2. – na udziały (akcje) własne",
    "Pasywa_A_V": "A.V. Zysk (strata) z lat ubiegłych",
    "Pasywa_A_VI": "A.VI. Zysk (strata) netto",
    "Pasywa_A_VII": "A.VII. Odpisy z zysku netto w ciągu roku obrotowego (wielkość ujemna)",
    "Pasywa_B": "B. Zobowiązania i rezerwy na zobowiązania",
    "Pasywa_B_I": "B.I. Rezerwy na zobowiązania",
    "Pasywa_B_I_1": "B.I.1. Rezerwa z tytułu odroczonego podatku dochodowego",
    "Pasywa_B_I_2": "B.I.2. Rezerwa na świadczenia emerytalne i podobne",
    "Pasywa_B_I_2_1": "B.I.2.1. – długoterminowa",
    "Pasywa_B_I_2_2": "B.I.2.2. – krótkoterminowa",
    "Pasywa_B_I_3": "B.I.3. Pozostałe rezerwy",
    "Pasywa_B_I_3_1": "B.I.3.1. – długoterminowe",
    "Pasywa_B_I_3_2": "B.I.3.2. – krótkoterminowe",
    "Pasywa_B_II": "B.II. Zobowiązania długoterminowe",
    "Pasywa_B_II_1": "B.II.1. Wobec jednostek powiązanych",
    "Pasywa_B_II_2": "B.II.2. Wobec pozostałych jednostek, w których jednostka posiada zaangażowanie w kapitale",
    "Pasywa_B_II_3": "B.II.3. Wobec pozostałych jednostek",
    "Pasywa_B_II_3_A": "B.II.3.A. kredyty i pożyczki",
    "Pasywa_B_II_3_B": "B.II.3.B. z tytułu emisji dłużnych papierów wartościowych",
    "Pasywa_B_II_3_C": "B.II.3.C. inne zobowiązania finansowe",
    "Pasywa_B_II_3_D": "B.II.3.D. zobowiązania wekslowe",
    "Pasywa_B_II_3_E": "B.II.3.E. inne",
    "Pasywa_B_III": "B.III. Zobowiązania krótkoterminowe",
    "Pasywa_B_III_1": "B.III.1. Zobowiązania wobec jednostek powiązanych",
    "Pasywa_B_III_1_A": "B.III.1.A. z tytułu dostaw i usług, o okresie wymagalności:",
    "Pasywa_B_III_1_A_1": "B.III.1.A.1. – do 12 miesięcy",
    "Pasywa_B_III_1_A_2": "B.III.1.A.2. – powyżej 12 miesięcy",
    "Pasywa_B_III_1_B": "B.III.1.B. inne",
    "Pasywa_B_III_2": "B.III.2. Zobowiązania wobec pozostałych jednostek, w których jednostka posiada zaangażowanie w kapitale",
    "Pasywa_B_III_2_A": "B.III.2.A. z tytułu dostaw i usług, o okresie wymagalności:",
    "Pasywa_B_III_2_A_1": "B.III.2.A.1. – do 12 miesięcy",
    "Pasywa_B_III_2_A_2": "B.III.2.A.2. – powyżej 12 miesięcy",
    "Pasywa_B_III_2_B": "B.III.2.B. inne",
    "Pasywa_B_III_3": "B.III.3. Zobowiązania wobec pozostałych jednostek",
    "Pasywa_B_III_3_A": "B.III.3.A. kredyty i pożyczki",
    "Pasywa_B_III_3_B": "B.III.3.B. z tytułu emisji dłużnych papierów wartościowych",
    "Pasywa_B_III_3_C": "B.III.3.C. inne zobowiązania finansowe",
    "Pasywa_B_III_3_D": "B.III.3.D. z tytułu dostaw i usług, o okresie wymagalności:",
    "Pasywa_B_III_3_D_1": "B.III.3.D.1. – do 12 miesięcy",
    "Pasywa_B_III_3_D_2": "B.III.3.D.2. – powyżej 12 miesięcy",
    "Pasywa_B_III_3_E": "B.III.3.E. zaliczki otrzymane na dostawy i usługi",
    "Pasywa_B_III_3_F": "B.III.3.F. zobowiązania wekslowe",
    "Pasywa_B_III_3_G": "B.III.3.G. z tytułu podatków, ceł, ubezpieczeń społecznych i zdrowotnych oraz innych tytułów publicznoprawnych",
    "Pasywa_B_III_3_H": "B.III.3.H. z tytułu wynagrodzeń",
    "Pasywa_B_III_3_I": "B.III.3.I. inne",
    "Pasywa_B_III_4": "B.III.4. Fundusze specjalne",
    "Pasywa_B_IV": "B.IV. Rozliczenia międzyokresowe",
    "Pasywa_B_IV_1": "B.IV.1. Ujemna wartość firmy",
    "Pasywa_B_IV_2": "B.IV.2. Inne rozliczenia międzyokresowe",
    "Pasywa_B_IV_2_1": "B.IV.2.1. – długoterminowe",
    "Pasywa_B_IV_2_2": "B.IV.2.2. – krótkoterminowe",
    "Pasywa": "Pasywa razem",
}

RZIS_INNA_POROWNAWCZY = {
    "A": "A. Przychody netto ze sprzedaży i zrównane z nimi, w tym:",
    "A_I": "A.I. Przychody netto ze sprzedaży produktów",
    "A_II": "A.II. Zmiana stanu produktów (zwiększenie – wartość dodatnia, zmniejszenie – wartość ujemna)",
    "A_III": "A.III. Koszt wytworzenia produktów na własne potrzeby jednostki",
    "A_IV": "A.IV. Przychody netto ze sprzedaży towarów i materiałów",
    "A_J": "A.J. – od jednostek powiązanych",
    "B": "B. Koszty działalności operacyjnej",
    "B_I": "B.I. Amortyzacja",
    "B_II": "B.II. Zużycie materiałów i energii",
    "B_III": "B.III. Usługi obce",
    "B_IV": "B.IV. Podatki i opłaty, w tym:",
    "B_IV_1": "B.IV.1. – podatek akcyzowy",
    "B_V": "B.V. Wynagrodzenia",
    "B_VI": "B.VI. Ubezpieczenia społeczne i inne świadczenia, w tym:",
    "B_VI_1": "B.VI.1. – emerytalne",
    "B_VII": "B.VII. Pozostałe koszty rodzajowe",
    "B_VIII": "B.VIII. Wartość sprzedanych towarów i materiałów",
    "C": "C. Zysk (strata) ze sprzedaży (A–B)",
    "D": "D. Pozostałe przychody operacyjne",
    "D_I": "D.I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych",
    "D_II": "D.II. Dotacje",
    "D_III": "D.III. Aktualizacja wartości aktywów niefinansowych",
    "D_IV": "D.IV. Inne przychody operacyjne",
    "E": "E. Pozostałe koszty operacyjne",
    "E_I": "E.I. Strata z tytułu rozchodu niefinansowych aktywów trwałych",
    "E_II": "E.II. Aktualizacja wartości aktywów niefinansowych",
    "E_III": "E.III. Inne koszty operacyjne",
    "F": "F. Zysk (strata) z działalności operacyjnej (C+D–E)",
    "G": "G. Przychody finansowe",
    "G_I": "G.I. Dywidendy i udziały w zyskach, w tym:",
    "G_I_A": "G.I.A. Od jednostek powiązanych, w tym:",
    "G_I_A_1": "G.I.A.1. – w których jednostka posiada zaangażowanie w kapitale",
    "G_I_B": "G.I.B. Od jednostek pozostałych, w tym:",
    "G_I_B_1": "G.I.B.1. – w których jednostka posiada zaangażowanie w kapitale",
    "G_II": "G.II. Odsetki, w tym:",
    "G_II_J": "G.II.J. – od jednostek powiązanych",
    "G_III": "G.III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",
    "G_III_J": "G.III.J. – w jednostkach powiązanych",
    "G_IV": "G.IV. Aktualizacja wartości aktywów finansowych",
    "G_V": "G.V. Inne",
    "H": "H. Koszty finansowe",
    "H_I": "H.I. Odsetki, w tym:",
    "H_I_J": "H.I.J. – dla jednostek powiązanych",
    "H_II": "H.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",
    "H_II_J": "H.II.J. – w jednostkach powiązanych",
    "H_III": "H.III. Aktualizacja wartości aktywów finansowych",
    "H_IV": "H.IV. Inne",
    "I": "I. Zysk (strata) brutto (F+G–H)",
    "J": "J. Podatek dochodowy",
    "K": "K. Pozostałe obowiązkowe zmniejszenia zysku (zwiększenia straty)",
    "L": "L. Zysk (strata) netto (I–J–K)",
    "RZiSPor": "RZiSPor. Rachunek zysków i strat (wariant porównawczy)",
}

RZIS_INNA_KALKULACYJNY = {
    "A": "A. Przychody netto ze sprzedaży produktów, towarów i materiałów, w tym:",
    "A_I": "A.I. Przychody netto ze sprzedaży produktów",
    "A_II": "A.II. Przychody netto ze sprzedaży towarów i materiałów",
    "A_J": "A.J. – od jednostek powiązanych",
    "B": "B. Koszty sprzedanych produktów, towarów i materiałów, w tym:",
    "B_I": "B.I. Koszt wytworzenia sprzedanych produktów",
    "B_II": "B.II. Wartość sprzedanych towarów i materiałów",
    "B_J": "B.J. – jednostkom powiązanym",
    "C": "C. Zysk (strata) brutto ze sprzedaży (A–B)",
    "D": "D. Koszty sprzedaży",
    "E": "E. Koszty ogólnego zarządu",
    "F": "F. Zysk (strata) ze sprzedaży (C–D–E)",
    "G": "G. Pozostałe przychody operacyjne",
    "G_I": "G.I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych",
    "G_II": "G.II. Dotacje",
    "G_III": "G.III. Aktualizacja wartości aktywów niefinansowych",
    "G_IV": "G.IV. Inne przychody operacyjne",
    "H": "H. Pozostałe koszty operacyjne",
    "H_I": "H.I. Strata z tytułu rozchodu niefinansowych aktywów trwałych",
    "H_II": "H.II. Aktualizacja wartości aktywów niefinansowych",
    "H_III": "H.III. Inne koszty operacyjne",
    "I": "I. Zysk (strata) z działalności operacyjnej (F+G–H)",
    "J": "J. Przychody finansowe",
    "J_I": "J.I. Dywidendy i udziały w zyskach, w tym:",
    "J_I_A": "J.I.A. od jednostek powiązanych, w tym:",
    "J_I_A_1": "J.I.A.1. – w których jednostka posiada zaangażowanie w kapitale",
    "J_I_B": "J.I.B. od jednostek pozostałych, w tym:",
    "J_I_B_1": "J.I.B.1. – w których jednostka posiada zaangażowanie w kapitale",
    "J_II": "J.II. Odsetki, w tym:",
    "J_II_J": "J.II.J. – od jednostek powiązanych",
    "J_III": "J.III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",
    "J_III_J": "J.III.J. – w jednostkach powiązanych",
    "J_IV": "J.IV. Aktualizacja wartości aktywów finansowych",
    "J_V": "J.V. Inne",
    "K": "K. Koszty finansowe",
    "K_I": "K.I. Odsetki, w tym:",
    "K_I_J": "K.I.J. – dla jednostek powiązanych",
    "K_II": "K.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",
    "K_II_J": "K.II.J. – w jednostkach powiązanych",
    "K_III": "K.III. Aktualizacja wartości aktywów finansowych",
    "K_IV": "K.IV. Inne",
    "L": "L. Zysk (strata) brutto (I+J–K)",
    "M": "M. Podatek dochodowy",
    "N": "N. Pozostałe obowiązkowe zmniejszenia zysku (zwiększenia straty)",
    "O": "O. Zysk (strata) netto (L–M–N)",
    "RZiSKalk": "RZiSKalk. Rachunek zysków i strat (wariant kalkulacyjny)",
}

ZESTAWIENIE_ZMIAN_W_KAPITALE = {
    "I": "I. Kapitał (fundusz) własny na początek okresu (BO)",
    "I_1": "I.1. – zmiany przyjętych zasad (polityki) rachunkowości",
    "I_2": "I.2. – korekty błędów",
    "IA": "IA. Kapitał (fundusz) własny na początek okresu (BO), po korektach",
    "IA_1": "IA.1. Kapitał (fundusz) podstawowy na początek okresu",
    "IA_1_1": "IA.1.1. Zmiany kapitału (funduszu) podstawowego",
    "IA_1_1_A": "IA.1.1.A. zwiększenie (z tytułu)",
    "IA_1_1_A_1": "IA.1.1.A.1. – wydania udziałów (emisji akcji)",
    "IA_1_1_B": "IA.1.1.B. zmniejszenie (z tytułu)",
    "IA_1_1_B_1": "IA.1.1.B.1. – umorzenia udziałów (akcji)",
    "IA_1_2": "IA.1.2. Kapitał (fundusz) podstawowy na koniec okresu",
    "IA_2": "IA.2. Kapitał (fundusz) zapasowy na początek okresu",
    "IA_2_1": "IA.2.1. Zmiany kapitału (funduszu) zapasowego",
    "IA_2_1_A": "IA.2.1.A. zwiększenie (z tytułu)",
    "IA_2_1_A_1": "IA.2.1.A.1. – emisji akcji powyżej wartości nominalnej",
    "IA_2_1_A_2": "IA.2.1.A.2. – podziału zysku (ustawowo)",
    "IA_2_1_A_3": "IA.2.1.A.3. – podziału zysku (ponad wymaganą ustawowo minimalną wartość)",
    "IA_2_1_B": "IA.2.1.B. zmniejszenie (z tytułu)",
    "IA_2_1_B_1": "IA.2.1.B.1. – pokrycia straty",
    "IA_2_2": "IA.2.2. Stan kapitału (funduszu) zapasowego na koniec okresu",
    "IA_3": "IA.3. Kapitał (fundusz) z aktualizacji wyceny na początek okresu – zmiany przyjętych zasad (polityki) rachunkowości",
    "IA_3_1": "IA.3.1. Zmiany kapitału (funduszu) z aktualizacji wyceny",
    "IA_3_1_A": "IA.3.1.A. zwiększenie (z tytułu)",
    "IA_3_1_B": "IA.3.1.B. zmniejszenie (z tytułu)",
    "IA_3_1_B_1": "IA.3.1.B.1. – zbycia środków trwałych",
    "IA_3_2": "IA.3.2. Kapitał (fundusz) z aktualizacji wyceny na koniec okresu",
    "IA_4": "IA.4. Pozostałe kapitały (fundusze) rezerwowe na początek okresu",
    "IA_4_1": "IA.4.1. Zmiany pozostałych kapitałów (funduszy) rezerwowych",
    "IA_4_1_A": "IA.4.1.A. zwiększenie (z tytułu)",
    "IA_4_1_B": "IA.4.1.B. zmniejszenie (z tytułu)",
    "IA_4_2": "IA.4.2. Pozostałe kapitały (fundusze) rezerwowe na koniec okresu",
    "IA_5": "IA.5. Zysk (strata) z lat ubiegłych na początek okresu",
    "IA_5_1": "IA.5.1. Zysk z lat ubiegłych na początek okresu",
    "IA_5_1_1": "IA.5.1.1. – zmiany przyjętych zasad (polityki) rachunkowości",
    "IA_5_1_2": "IA.5.1.2. – korekty błędów",
    "IA_5_2": "IA.5.2. Zysk z lat ubiegłych na początek okresu, po korektach",
    "IA_5_2_A": "IA.5.2.A. zwiększenie (z tytułu)",
    "IA_5_2_A_1": "IA.5.2.A.1. – podziału zysku z lat ubiegłych",
    "IA_5_2_B": "IA.5.2.B. zmniejszenie (z tytułu)",
    "IA_5_3": "IA.5.3. Zysk z lat ubiegłych na koniec okresu",
    "IA_5_4": "IA.5.4. Strata z lat ubiegłych na początek okresu",
    "IA_5_4_1": "IA.5.4.1. – zmiany przyjętych zasad (polityki) rachunkowości",
    "IA_5_4_2": "IA.5.4.2. – korekty błędów",
    "IA_5_5": "IA.5.5. Strata z lat ubiegłych na początek okresu, po korektach",
    "IA_5_5_A": "IA.5.5.A. zwiększenie (z tytułu)",
    "IA_5_5_A_1": "IA.5.5.A.1. – przeniesienia straty z lat ubiegłych do pokrycia",
    "IA_5_5_B": "IA.5.5.B. zmniejszenie (z tytułu)",
    "IA_5_6": "IA.5.6. Strata z lat ubiegłych na koniec okresu",
    "IA_5_7": "IA.5.7. Zysk (strata) z lat ubiegłych na koniec okresu",
    "IA_6": "IA.6. Wynik netto",
    "IA_6_A": "IA.6.A. zysk netto",
    "IA_6_B": "IA.6.B. strata netto",
    "IA_6_C": "IA.6.C. odpisy z zysku",
    "II": "II. Kapitał (fundusz) własny na koniec okresu (BZ)",
    "III": "III. Kapitał (fundusz) własny, po uwzględnieniu proponowanego podziału zysku (pokrycia straty)",
}

RACHUNEK_PRZEPLYWOW_BEZPOSREDNI = {
    "A": "A. Przepływy środków pieniężnych z działalności operacyjnej",
    "A_I": "A.I. Wpływy",
    "A_I_1": "A.I.1. Sprzedaż",
    "A_I_2": "A.I.2. Inne wpływy z działalności operacyjnej",
    "A_II": "A.II. Wydatki",
    "A_II_1": "A.II.1. Dostawy i usługi",
    "A_II_2": "A.II.2. Wynagrodzenia netto",
    "A_II_3": "A.II.3. Ubezpieczenia społeczne i zdrowotne oraz inne świadczenia",
    "A_II_4": "A.II.4. Podatki i opłaty o charakterze publicznoprawnym",
    "A_II_5": "A.II.5. Inne wydatki operacyjne",
    "A_III": "A.III. Przepływy pieniężne netto z działalności operacyjnej (I–II)",
    "B": "B. Przepływy środków pieniężnych z działalności inwestycyjnej",
    "B_I": "B.I. Wpływy",
    "B_I_1": "B.I.1. Zbycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych",
    "B_I_2": "B.I.2. Zbycie inwestycji w nieruchomości oraz wartości niematerialne i prawne",
    "B_I_3": "B.I.3. Z aktywów finansowych, w tym:",
    "B_I_3_A": "B.I.3.A. w jednostkach powiązanych",
    "B_I_3_B": "B.I.3.B. w pozostałych jednostkach",
    "B_I_3_B_1": "B.I.3.B.1. – zbycie aktywów finansowych",
    "B_I_3_B_2": "B.I.3.B.2. – dywidendy i udziały w zyskach",
    "B_I_3_B_3": "B.I.3.B.3. – spłata udzielonych pożyczek długoterminowych",
    "B_I_3_B_4": "B.I.3.B.4. – odsetki",
    "B_I_3_B_5": "B.I.3.B.5. – inne wpływy z aktywów finansowych",
    "B_I_4": "B.I.4. Inne wpływy inwestycyjne",
    "B_II": "B.II. Wydatki",
    "B_II_1": "B.II.1. Nabycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych",
    "B_II_2": "B.II.2. Inwestycje w nieruchomości oraz wartości niematerialne i prawne",
    "B_II_3": "B.II.3. Na aktywa finansowe, w tym:",
    "B_II_3_A": "B.II.3.A. w jednostkach powiązanych",
    "B_II_3_B": "B.II.3.B. w pozostałych jednostkach",
    "B_II_3_B_1": "B.II.3.B.1. – nabycie aktywów finansowych",
    "B_II_3_B_2": "B.II.3.B.2. – udzielone pożyczki długoterminowe",
    "B_II_4": "B.II.4. Inne wydatki inwestycyjne",
    "B_III": "B.III. Przepływy pieniężne netto z działalności inwestycyjnej (I–II)",
    "C": "C. Przepływy środków pieniężnych z działalności finansowej",
    "C_I": "C.I. Wpływy",
    "C_I_1": "C.I.1. Wpływy netto z wydania udziałów (emisji akcji) i innych instrumentów kapitałowych oraz dopłat do kapitału",
    "C_I_2": "C.I.2. Kredyty i pożyczki",
    "C_I_3": "C.I.3. Emisja dłużnych papierów wartościowych",
    "C_I_4": "C.I.4. Inne wpływy finansowe",
    "C_II": "C.II. Wydatki",
    "C_II_1": "C.II.1. Nabycie udziałów (akcji) własnych",
    "C_II_2": "C.II.2. Dywidendy i inne wypłaty na rzecz właścicieli",
    "C_II_3": "C.II.3. Inne, niż wypłaty na rzecz właścicieli, wydatki z tytułu podziału zysku",
    "C_II_4": "C.II.4. Spłaty kredytów i pożyczek",
    "C_II_5": "C.II.5. Wykup dłużnych papierów wartościowych",
    "C_II_6": "C.II.6. Z tytułu innych zobowiązań finansowych",
    "C_II_7": "C.II.7. Płatności zobowiązań z tytułu umów leasingu finansowego",
    "C_II_8": "C.II.8. Odsetki",
    "C_II_9": "C.II.9. Inne wydatki finansowe",
    "C_III": "C.III. Przepływy pieniężne netto z działalności finansowej (I–II)",
    "D": "D. Przepływy pieniężne netto, razem (A.III±B.III±C.III)",
    "E": "E. Bilansowa zmiana stanu środków pieniężnych, w tym:",
    "E_1": "E.1. – zmiana stanu środków pieniężnych z tytułu różnic kursowych",
    "F": "F. Środki pieniężne na początek okresu",
    "G": "G. Środki pieniężne na koniec okresu (F±D), w tym:",
    "G_1": "G.1. – o ograniczonej możliwości dysponowania",
    "PrzeplywyBezp": "PrzeplywyBezp. Rachunek przepływów pieniężnych (metoda bezpośrednia)",
    "PrzeplywyPosr": "PrzeplywyPosr. Rachunek przepływów pieniężnych (metoda pośrednia)",
}

RACHUNEK_PRZEPLYWOW_POSREDNI = {
    "A": "A. Przepływy środków pieniężnych z działalności operacyjnej",
    "A_I": "A.I. Zysk (strata) netto",
    "A_II": "A.II. Korekty razem",
    "A_II_1": "A.II.1. Amortyzacja",
    "A_II_2": "A.II.2. Zyski (straty) z tytułu różnic kursowych",
    "A_II_3": "A.II.3. Odsetki i udziały w zyskach (dywidendy)",
    "A_II_4": "A.II.4. Zysk (strata) z działalności inwestycyjnej",
    "A_II_5": "A.II.5. Zmiana stanu rezerw",
    "A_II_6": "A.II.6. Zmiana stanu zapasów",
    "A_II_7": "A.II.7. Zmiana stanu należności",
    "A_II_8": "A.II.8. Zmiana stanu zobowiązań krótkoterminowych, z wyjątkiem pożyczek i kredytów",
    "A_II_9": "A.II.9. Zmiana stanu rozliczeń międzyokresowych",
    "A_II_10": "A.II.10. Inne korekty",
    "A_III": "A.III. Przepływy pieniężne netto z działalności operacyjnej (I±II)",
    "B": "B. Przepływy środków pieniężnych z działalności inwestycyjnej",
    "B_I": "B.I. Wpływy",
    "B_I_1": "B.I.1. Zbycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych",
    "B_I_2": "B.I.2. Zbycie inwestycji w nieruchomości oraz wartości niematerialne i prawne",
    "B_I_3": "B.I.3. Z aktywów finansowych, w tym:",
    "B_I_3_A": "B.I.3.A. w jednostkach powiązanych",
    "B_I_3_B": "B.I.3.B. w pozostałych jednostkach",
    "B_I_3_B_1": "B.I.3.B.1. – zbycie aktywów finansowych",
    "B_I_3_B_2": "B.I.3.B.2. – dywidendy i udziały w zyskach",
    "B_I_3_B_3": "B.I.3.B.3. – spłata udzielonych pożyczek długoterminowych",
    "B_I_3_B_4": "B.I.3.B.4. – odsetki",
    "B_I_3_B_5": "B.I.3.B.5. – inne wpływy z aktywów finansowych",
    "B_I_4": "B.I.4. Inne wpływy inwestycyjne",
    "B_II": "B.II. Wydatki",
    "B_II_1": "B.II.1. Nabycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych",
    "B_II_2": "B.II.2. Inwestycje w nieruchomości oraz wartości niematerialne i prawne",
    "B_II_3": "B.II.3. Na aktywa finansowe, w tym:",
    "B_II_3_A": "B.II.3.A. w jednostkach powiązanych",
    "B_II_3_B": "B.II.3.B. w pozostałych jednostkach",
    "B_II_3_B_1": "B.II.3.B.1. – nabycie aktywów finansowych",
    "B_II_3_B_2": "B.II.3.B.2. – udzielone pożyczki długoterminowe",
    "B_II_4": "B.II.4. Inne wydatki inwestycyjne",
    "B_III": "B.III. Przepływy pieniężne netto z działalności inwestycyjnej (I–II)",
    "C": "C. Przepływy środków pieniężnych z działalności finansowej",
    "C_I": "C.I. Wpływy",
    "C_I_1": "C.I.1. Wpływy netto z wydania udziałów (emisji akcji) i innych instrumentów kapitałowych oraz dopłat do kapitału",
    "C_I_2": "C.I.2. Kredyty i pożyczki",
    "C_I_3": "C.I.3. Emisja dłużnych papierów wartościowych",
    "C_I_4": "C.I.4. Inne wpływy finansowe",
    "C_II": "C.II. Wydatki",
    "C_II_1": "C.II.1. Nabycie udziałów (akcji) własnych",
    "C_II_2": "C.II.2. Dywidendy i inne wypłaty na rzecz właścicieli",
    "C_II_3": "C.II.3. Inne, niż wypłaty na rzecz właścicieli, wydatki z tytułu podziału zysku",
    "C_II_4": "C.II.4. Spłaty kredytów i pożyczek",
    "C_II_5": "C.II.5. Wykup dłużnych papierów wartościowych",
    "C_II_6": "C.II.6. Z tytułu innych zobowiązań finansowych",
    "C_II_7": "C.II.7. Płatności zobowiązań z tytułu umów leasingu finansowego",
    "C_II_8": "C.II.8. Odsetki",
    "C_II_9": "C.II.9. Inne wydatki finansowe",
    "C_III": "C.III. Przepływy pieniężne netto z działalności finansowej (I–II)",
    "D": "D. Przepływy pieniężne netto razem (A.III±B.III±C.III)",
    "E": "E. Bilansowa zmiana stanu środków pieniężnych, w tym:",
    "E_1": "E.1. – zmiana stanu środków pieniężnych z tytułu różnic kursowych",
    "F": "F. Środki pieniężne na początek okresu",
    "G": "G. Środki pieniężne na koniec okresu (F±D), w tym:",
    "G_1": "G.1. – o ograniczonej możliwości dysponowania",
    "PrzeplywyBezp": "PrzeplywyBezp. Rachunek przepływów pieniężnych (metoda bezpośrednia)",
    "PrzeplywyPosr": "PrzeplywyPosr. Rachunek przepływów pieniężnych (metoda pośrednia)",
}

# =============================================================================
# JEDNOSTKA MALA
# =============================================================================

BILANS_MALA = {
    # AKTYWA
    "Aktywa_A": "A. Aktywa trwałe",
    "Aktywa_A_I": "A.I. Wartości niematerialne i prawne",
    "Aktywa_A_II": "A.II. Rzeczowe aktywa trwałe, w tym:",
    "Aktywa_A_II_1": "A.II.1. – środki trwałe",
    "Aktywa_A_II_2": "A.II.2. – środki trwałe w budowie",
    "Aktywa_A_III": "A.III. Należności długoterminowe",
    "Aktywa_A_IV": "A.IV. Inwestycje długoterminowe, w tym:",
    "Aktywa_A_IV_1": "A.IV.1. – nieruchomości",
    "Aktywa_A_IV_2": "A.IV.2. – długoterminowe aktywa finansowe",
    "Aktywa_A_V": "A.V. Długoterminowe rozliczenia międzyokresowe",
    "Aktywa": "Aktywa razem",
    "Aktywa_B": "B. Aktywa obrotowe",
    "Aktywa_B_I": "B.I. Zapasy",
    "Aktywa_B_II": "B.II. Należności krótkoterminowe, w tym:",
    "Aktywa_B_II_A": "B.II.A. a) z tytułu dostaw i usług, w tym:",
    "Aktywa_B_II_A_1": "B.II.A.1. – do 12 miesięcy",
    "Aktywa_B_II_A_2": "B.II.A.2. – powyżej 12 miesięcy",
    "Aktywa_B_III": "B.III. Inwestycje krótkoterminowe, w tym:",
    "Aktywa_B_III_A": "B.III.A. a) krótkoterminowe aktywa finansowe, w tym:",
    "Aktywa_B_III_A_1": "B.III.A.1. – środki pieniężne w kasie i na rachunkach",
    "Aktywa_B_IV": "B.IV. Krótkoterminowe rozliczenia międzyokresowe",
    "Aktywa_C": "C. Należne wpłaty na kapitał (fundusz) podstawowy",
    "Aktywa_D": "D. Udziały (akcje) własne",

    # PASYWA
    "Pasywa_A": "A. Kapitał (fundusz) własny",
    "Pasywa_A_I": "A.I. Kapitał (fundusz) podstawowy",
    "Pasywa_A_II": "A.II. Kapitał (fundusz) zapasowy, w tym:",
    "Pasywa_A_II_1": "A.II.1. – nadwyżka wartości sprzedaży (wartości emisyjnej) nad wartością nominalną udziałów (akcji)",
    "Pasywa_A_III": "A.III. Kapitał (fundusz) z aktualizacji wyceny, w tym:",
    "Pasywa_A_III_1": "A.III.1. – z tytułu aktualizacji wartości godziwej",
    "Pasywa_A_IV": "A.IV. Pozostałe kapitały (fundusze) rezerwowe",
    "Pasywa_A_V": "A.V. Zysk (strata) z lat ubiegłych",
    "Pasywa_A_VI": "A.VI. Zysk (strata) netto",
    "Pasywa_A_VII": "A.VII. Odpisy z zysku netto w ciągu roku obrotowego (wielkość ujemna)",
    "Pasywa_B": "B. Zobowiązania i rezerwy na zobowiązania",
    "Pasywa_B_I": "B.I. Rezerwy na zobowiązania, w tym:",
    "Pasywa_B_I_1": "B.I.1. – rezerwa na świadczenia emerytalne i podobne",
    "Pasywa_B_II": "B.II. Zobowiązania długoterminowe, w tym:",
    "Pasywa_B_II_1": "B.II.1. – z tytułu kredytów i pożyczek",
    "Pasywa_B_III": "B.III. Zobowiązania krótkoterminowe, w tym:",
    "Pasywa_B_III_A": "B.III.A. a) z tytułu kredytów i pożyczek",
    "Pasywa_B_III_B": "B.III.B. b) z tytułu dostaw i usług, w tym:",
    "Pasywa_B_III_B_1": "B.III.B.1. – Do 12 miesięcy",
    "Pasywa_B_III_B_2": "B.III.B.2. – Powyżej 12 miesięcy",
    "Pasywa_B_III_C": "B.III.C. c) fundusze specjalne",
    "Pasywa_B_IV": "B.IV. Rozliczenia międzyokresowe",
    "Pasywa": "Pasywa razem",
}

RZIS_MALA_POROWNAWCZY = {
    "A": "A. Przychody netto ze sprzedaży i zrównane z nimi",
    "A_I": "A.I. Przychody netto ze sprzedaży",
    "A_II": "A.II. Zmiana stanu produktów (zwiększenie – wartość dodatnia, zmniejszenie – wartość ujemna)",
    "A_III": "A.III. Koszt wytworzenia produktów na własne potrzeby jednostki",
    "B": "B. Koszty działalności operacyjnej",
    "B_I": "B.I. Amortyzacja",
    "B_II": "B.II. Zużycie materiałów i energii",
    "B_III": "B.III. Usługi obce",
    "B_IV": "B.IV. Wynagrodzenia",
    "B_V": "B.V. Ubezpieczenia społeczne i inne świadczenia, w tym:",
    "B_V_1": "B.V.1. – emerytalne",
    "B_VI": "B.VI. Pozostałe koszty, w tym:",
    "B_VI_1": "B.VI.1. – wartość sprzedanych towarów i materiałów",
    "C": "C. Zysk (strata) ze sprzedaży (A - B)",
    "D": "D. Pozostałe przychody operacyjne, w tym:",
    "D_1": "D.1. – aktualizacja wartości aktywów niefinansowych",
    "E": "E. Pozostałe koszty operacyjne, w tym:",
    "E_1": "E.1. – aktualizacja wartości aktywów niefinansowych",
    "F": "F. Przychody finansowe, w tym:",
    "F_I": "F.I. Dywidendy i udziały w zyskach od jednostek, w których jednostka posiada zaangażowanie w kapitale, w tym:",
    "F_I_1": "F.I.1. – od jednostek powiązanych, w których jednostka posiada zaangażowanie w kapitale",
    "F_II": "F.II. Odsetki, w tym:",
    "F_II_1": "F.II.1. – od jednostek powiązanych",
    "F_III": "F.III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",
    "F_III_1": "F.III.1. – w jednostkach powiązanych",
    "F_IV": "F.IV. Aktualizacja wartości aktywów finansowych",
    "G": "G. Koszty finansowe, w tym:",
    "G_I": "G.I. Odsetki, w tym:",
    "G_I_1": "G.I.1. – dla jednostek powiązanych",
    "G_II": "G.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",
    "G_II_1": "G.II.1. – w jednostkach powiązanych",
    "G_III": "G.III. Aktualizacja wartości aktywów finansowych",
    "H": "H. Zysk (strata) brutto (C + D - E + F - G)",
    "I": "I. Podatek dochodowy",
    "J": "J. Zysk (strata) netto (H - I)",
    "RZiSPor": "RZiSPor. Rachunek zysków i strat (wariant porównawczy)",
}

RZIS_MALA_KALKULACYJNY = {
    "A": "A. Przychody netto ze sprzedaży produktów, towarów i materiałów",
    "B": "B. Koszty sprzedanych produktów, towarów i materiałów",
    "C": "C. Koszty sprzedaży",
    "D": "D. Koszty ogólnego zarządu",
    "E": "E. Zysk (strata) ze sprzedaży (A - B - C - D)",
    "F": "F. Pozostałe przychody operacyjne, w tym:",
    "F_1": "F.1. – aktualizacja wartości aktywów niefinansowych",
    "G": "G. Pozostałe koszty operacyjne, w tym:",
    "G_1": "G.1. – aktualizacja wartości aktywów niefinansowych",
    "H": "H. Przychody finansowe, w tym:",
    "H_I": "H.I. Dywidendy i udziały w zyskach od jednostek, w których jednostka posiada zaangażowanie w kapitale, w tym:",
    "H_I_1": "H.I.1. – od jednostek powiązanych, w których jednostka posiada zaangażowanie w kapitale",
    "H_II": "H.II. Odsetki, w tym:",
    "H_II_1": "H.II.1. – od jednostek powiązanych",
    "H_III": "H.III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",
    "H_III_1": "H.III.1. – w jednostkach powiązanych",
    "H_IV": "H.IV. Aktualizacja wartości aktywów finansowych",
    "I": "I. Koszty finansowe, w tym:",
    "I_I": "I.I. Odsetki, w tym:",
    "I_I_1": "I.I.1. – dla jednostek powiązanych",
    "I_II": "I.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",
    "I_II_1": "I.II.1. – w jednostkach powiązanych",
    "I_III": "I.III. Aktualizacja wartości aktywów finansowych",
    "J": "J. Zysk (strata) brutto (E + F - G + H - I)",
    "K": "K. Podatek dochodowy",
    "L": "L. Zysk (strata) netto (J - K)",
    "RZiSKalk": "RZiSKalk. Rachunek zysków i strat (wariant kalkulacyjny)",
}

# =============================================================================
# JEDNOSTKA MIKRO
# =============================================================================

BILANS_MIKRO = {
    # AKTYWA
    "Aktywa_A": "A. Aktywa trwałe, w tym środki trwałe",
    "Aktywa": "Aktywa razem",
    "Aktywa_B": "B. Aktywa obrotowe, w tym:",
    "Aktywa_B_1": "B.1. - zapasy",
    "Aktywa_B_2": "B.2. - należności krótkoterminowe",
    "Aktywa_C": "C. Należne wpłaty na kapitał (fundusz) podstawowy",
    "Aktywa_D": "D. Udziały (akcje) własne",

    # PASYWA
    "Pasywa_A": "A. Kapitał (fundusz) własny, w tym:",
    "Pasywa_A_1": "A.1. - kapitał (fundusz) podstawowy",
    "Pasywa_B": "B. Zobowiązania i rezerwy na zobowiązania, w tym:",
    "Pasywa_B_1": "B.1. - rezerwy na zobowiązania",
    "Pasywa_B_2": "B.2. - zobowiązania z tytułu kredytów i pożyczek",
    "Pasywa": "Pasywa razem",
}

RZIS_MIKRO = {
    "A": "A. Przychody podstawowej działalności operacyjnej i zrównane z nimi, w tym:",
    "A_1": "A.1. - zmiana stanu produktów (zwiększenie - wartość dodatnia, zmniejszenie - wartość ujemna)",
    "B": "B. Koszty podstawowej działalności operacyjnej",
    "B_I": "B.I. Amortyzacja",
    "B_II": "B.II. Zużycie materiałów i energii",
    "B_III": "B.III. Wynagrodzenia, ubezpieczenia społeczne i inne świadczenia",
    "B_IV": "B.IV. Pozostałe koszty",
    "C": "C. Pozostałe przychody i zyski, w tym:",
    "C_1": "C.1. - aktualizacja wartości aktywów",
    "D": "D. Pozostałe koszty i straty, w tym:",
    "D_1": "D.1. - aktualizacja wartości aktywów",
    "E": "E. Podatek dochodowy",
    "F": "F. Zysk/strata netto (A-B+C-D-E)  (dla jednostek mikro, o których mowa w art. 3 ust. 1a pkt 1, 3 i 4 oraz ust. 1b ustawy)",
    "G": "G. Wynik finansowy netto ogółem (A-B+C-D-E), w tym:  (dla jednostek mikro, o których mowa w art. 3 ust. 1a pkt 2 ustawy).",
    "G_I": "G.I. Nadwyżka przychodów nad kosztami (wartość dodatnia)",
    "G_II": "G.II. Nadwyżka kosztów nad przychodami (wartość ujemna)",
}

# =============================================================================
# NOTA PODATKOWA
# Rozliczenie różnicy pomiędzy podstawą opodatkowania podatkiem dochodowym
# a wynikiem finansowym (zyskiem, stratą) brutto
# =============================================================================

# Główne pozycje noty podatkowej
NOTA_PODATKOWA = {
    "P_ID_1": "A. Zysk (strata) brutto za dany rok",
    "P_ID_2": "B. Przychody zwolnione z opodatkowania (trwałe różnice pomiędzy zyskiem/stratą dla celów rachunkowych a dochodem/stratą dla celów podatkowych)",
    "P_ID_3": "C. Przychody niepodlegające opodatkowaniu w roku bieżącym",
    "P_ID_4": "D. Przychody podlegające opodatkowaniu w roku bieżącym, ujęte w księgach rachunkowych lat ubiegłych",
    "P_ID_5": "E. Koszty niestanowiące kosztów uzyskania przychodów (trwałe różnice pomiędzy zyskiem/stratą dla celów rachunkowych a dochodem/stratą dla celów podatkowych)",
    "P_ID_6": "F. Koszty nieuznawane za koszty uzyskania przychodów w bieżącym roku",
    "P_ID_7": "G. Koszty uznawane za koszty uzyskania przychodów w roku bieżącym ujęte w księgach lat ubiegłych",
    "P_ID_8": "H. Strata z lat ubiegłych",
    "P_ID_9": "I. Inne zmiany podstawy opodatkowania",
    "P_ID_10": "J. Podstawa opodatkowania podatkiem dochodowym",
    "P_ID_11": "K. Podatek dochodowy",
}

# Suffiksy dla podpozycji (KwotaA, KwotaB, KwotaC)
NOTA_PODATKOWA_SUBKWOTY = {
    "KwotaA": "[wartość łączna]",
    "KwotaB": "[z zysków kapitałowych]",
    "KwotaC": "[z innych źródeł przychodów]",
}

# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================


def get_opis(kod: str, typ_jednostki: str, sekcja: str, wariant_rzis: str = "porownawczy") -> str:
    """
    Zwraca opis pozycji na podstawie kodu, typu jednostki i sekcji.

    Args:
        kod: Kod pozycji (np. "Aktywa_A_I", "A", "Pasywa_B_IV_2_1")
        typ_jednostki: "Mikro", "Mala" lub "Inna"
        sekcja: "Bilans", "RZiS" lub "Nota"
        wariant_rzis: "porownawczy" lub "kalkulacyjny"

    Returns:
        Opis pozycji lub kod jeśli nie znaleziono
    """
    if sekcja == "Bilans":
        mappings = {
            "Mikro": BILANS_MIKRO,
            "Mala": BILANS_MALA,
            "Inna": BILANS_INNA,
        }
    elif sekcja == "RZiS":
        if wariant_rzis == "kalkulacyjny":
            mappings = {
                "Mikro": RZIS_MIKRO if 'RZIS_MIKRO' in globals() else {},  # Mikro ma uproszczony RZiS
                "Mala": RZIS_MALA_KALKULACYJNY,
                "Inna": RZIS_INNA_KALKULACYJNY,
            }
        else:
            mappings = {
                "Mikro": RZIS_MIKRO if 'RZIS_MIKRO' in globals() else {},  # Mikro ma uproszczony RZiS
                "Mala": RZIS_MALA_POROWNAWCZY,
                "Inna": RZIS_INNA_POROWNAWCZY,
            }
    elif sekcja == "Nota":
        return NOTA_PODATKOWA.get(kod, kod)
    elif sekcja == "ZestZmianWKapitale":
        return ZESTAWIENIE_ZMIAN_W_KAPITALE.get(kod, kod)
    elif sekcja == "RachPrzeplywow":
        # Próbuj oba warianty - bezpośredni i pośredni mają wspólne elementy
        result = RACHUNEK_PRZEPLYWOW_POSREDNI.get(kod)
        if result is None:
            result = RACHUNEK_PRZEPLYWOW_BEZPOSREDNI.get(kod, kod)
        return result
    else:
        return kod

    # Spróbuj znaleźć w mapowaniu dla typu jednostki
    mapping = mappings.get(typ_jednostki, {})
    if kod in mapping:
        return mapping[kod]

    # Fallback do INNA (najbardziej kompletny)
    if typ_jednostki != "Inna" and sekcja == "Bilans":
        return BILANS_INNA.get(kod, kod)
    elif typ_jednostki != "Inna" and sekcja == "RZiS":
        if wariant_rzis == "kalkulacyjny":
            return RZIS_INNA_KALKULACYJNY.get(kod, kod)
        else:
            return RZIS_INNA_POROWNAWCZY.get(kod, kod)

    return kod


def calculate_poziom(kod: str) -> int:
    """
    Oblicza poziom zagnieżdżenia pozycji na podstawie kodu.

    Przykłady:
        "Aktywa" -> 0
        "Aktywa_A" -> 0
        "Aktywa_A_I" -> 1
        "Aktywa_A_I_1" -> 2
        "A" -> 0
        "A_I" -> 1
    """
    parts = kod.split('_')

    # Dla Bilans: Aktywa/Pasywa to prefix
    if parts[0] in ('Aktywa', 'Pasywa'):
        return max(0, len(parts) - 2)

    # Dla RZiS: bezpośrednia hierarchia
    return max(0, len(parts) - 1)
