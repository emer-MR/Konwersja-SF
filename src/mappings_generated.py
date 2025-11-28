"""\nMapowania pozycji finansowych - wygenerowane z plików XSD.\n\nTen plik zawiera słowniki mapujące kody pozycji XML na opisy czytelne dla człowieka.\nWygenerowano automatycznie na podstawie schematów XSD Ministerstwa Finansów.\n"""\n\nfrom typing import Optional\n\n# =============================================================================\n# JEDNOSTKA INNA\n# =============================================================================\n\nBILANS_INNA = {\n    # AKTYWA\n    "Aktywa": "Aktywa razem",\n    "Aktywa_A": "A. Aktywa trwałe",\n    "Aktywa_A_I": "A.I. Wartości niematerialne i prawne",\n    "Aktywa_A_I_1": "A.I.1. Koszty zakończonych prac rozwojowych",\n    "Aktywa_A_I_2": "A.I.2. Wartość firmy",\n    "Aktywa_A_I_3": "A.I.3. Inne wartości niematerialne i prawne",\n    "Aktywa_A_I_4": "A.I.4. Zaliczki na wartości niematerialne i prawne",\n}\n\nRZIS_INNA_KALKULACYJNY = {\n    "A": "A. Przychody netto ze sprzedaży produktów, towarów i materiałów, w tym:",\n    "B": "B. Koszty sprzedanych produktów, towarów i materiałów, w tym:",\n    "C": "C. Zysk (strata) brutto ze sprzedaży (A–B)",\n    "D": "D. Koszty sprzedaży",\n    "E": "E. Koszty ogólnego zarządu",\n    "F": "F. Zysk (strata) ze sprzedaży (C–D–E)",\n    "G": "G. Pozostałe przychody operacyjne",\n    "H": "H. Pozostałe koszty operacyjne",\n    "I": "I. Zysk (strata) z działalności operacyjnej (F+G–H)",\n    "J": ". Przychody finansowe",\n    "K": "K. Koszty finansowe",\n    "L": "L. Zysk (strata) brutto (I+J–K)",\n    "M": "M. Podatek dochodowy",\n    "N": "N. Pozostałe obowiązkowe zmniejszenia zysku (zwiększenia straty)",\n    "O": "O. Zysk (strata) netto (L–M–N)",\n    "A_I": "A.I. Przychody netto ze sprzedaży produktów",\n    "A_J": "A. – od jednostek powiązanych",\n    "B_I": "B.I. Koszt wytworzenia sprzedanych produktów",\n    "B_J": "B. – jednostkom powiązanym",\n    "G_I": "G.I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych",\n    "H_I": "H.I. Strata z tytułu rozchodu niefinansowych aktywów trwałych",\n    "J_I": ".I. Dywidendy i udziały w zyskach, w tym:",\n    "J_V": ".V. Inne",\n    "K_I": "K.I. Odsetki, w tym:",\n    "A_II": "A.II. Przychody netto ze sprzedaży towarów i materiałów",\n    "B_II": "B.II. Wartość sprzedanych towarów i materiałów",\n    "G_II": "G.II. Dotacje",\n    "G_IV": "G.IV. Inne przychody operacyjne",\n    "H_II": "H.II. Aktualizacja wartości aktywów niefinansowych",\n    "J_II": ".II. Odsetki, w tym:",\n    "J_IV": ".IV. Aktualizacja wartości aktywów finansowych",\n    "K_II": "K.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",\n    "K_IV": "K.IV. Inne",\n    "G_III": "G.III. Aktualizacja wartości aktywów niefinansowych",\n    "H_III": "H.III. Inne koszty operacyjne",\n    "J_III": ".III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",\n    "J_I_A": ".I.A. od jednostek powiązanych, w tym:",\n    "J_I_B": ".I.B. od jednostek pozostałych, w tym:",\n    "K_III": "K.III. Aktualizacja wartości aktywów finansowych",\n    "K_I_J": "K.I. – dla jednostek powiązanych",\n    "J_II_J": ".II. – od jednostek powiązanych",\n    "K_II_J": "K.II. – w jednostkach powiązanych",\n    "J_III_J": ".III. – w jednostkach powiązanych",\n    "J_I_A_1": ".I.A.1. – w których jednostka posiada zaangażowanie w kapitale",\n    "J_I_B_1": ".I.B.1. – w których jednostka posiada zaangażowanie w kapitale",\n}\n\n# =============================================================================\n# JEDNOSTKA MALA\n# =============================================================================\n\nBILANS_MALA = {\n    # AKTYWA\n    "Aktywa": "Aktywa razem",\n    "Aktywa_A": "A. Aktywa trwałe",\n    "Aktywa_A_I": "A.I. Wartości niematerialne i prawne",\n    "Aktywa_A_II": "A.II. Rzeczowe aktywa trwałe, w tym:",\n    "Aktywa_A_II_1": "A.II.1. – środki trwałe",\n    "Aktywa_A_II_2": "A.II.2. – środki trwałe w budowie",\n}\n\nRZIS_MALA_KALKULACYJNY = {\n    "A": "A. Przychody netto ze sprzedaży produktów, towarów i materiałów",\n    "B": "B. Koszty sprzedanych produktów, towarów i materiałów",\n    "C": "C. Koszty sprzedaży",\n    "D": "D. Koszty ogólnego zarządu",\n    "E": "E. Zysk (strata) ze sprzedaży (A - B - C - D)",\n    "F": "F. Pozostałe przychody operacyjne, w tym:",\n    "G": "G. Pozostałe koszty operacyjne, w tym:",\n    "H": "H. Przychody finansowe, w tym:",\n    "I": "I. Koszty finansowe, w tym:",\n    "J": ". Zysk (strata) brutto (E + F - G + H - I)",\n    "K": "K. Podatek dochodowy",\n    "L": "L. Zysk (strata) netto (J - K)",\n    "F_1": "F.1. – aktualizacja wartości aktywów niefinansowych",\n    "G_1": "G.1. – aktualizacja wartości aktywów niefinansowych",\n    "H_I": "H.I. Dywidendy i udziały w zyskach od jednostek, w których jednostka posiada zaangażowanie w kapitale, w tym:",\n    "I_I": "I.I. Odsetki, w tym:",\n    "H_II": "H.II. Odsetki, w tym:",\n    "H_IV": "H.IV. Aktualizacja wartości aktywów finansowych",\n    "I_II": "I.II. Strata z tytułu rozchodu aktywów finansowych, w tym:",\n    "H_III": "H.III. Zysk z tytułu rozchodu aktywów finansowych, w tym:",\n    "H_I_1": "H.I.1. – od jednostek powiązanych, w których jednostka posiada zaangażowanie w kapitale",\n    "I_III": "I.III. Aktualizacja wartości aktywów finansowych",\n    "I_I_1": "I.I.1. – dla jednostek powiązanych",\n    "H_II_1": "H.II.1. – od jednostek powiązanych",\n    "I_II_1": "I.II.1. – w jednostkach powiązanych",\n    "H_III_1": "H.III.1. – w jednostkach powiązanych",\n}\n\n# =============================================================================\n# JEDNOSTKA MIKRO\n# =============================================================================\n\nBILANS_MIKRO = {\n    # AKTYWA\n    "Aktywa": "Aktywa razem",\n    "Aktywa_A": "A. Aktywa trwałe, w tym środki trwałe",\n    "Aktywa_B": "B. Aktywa obrotowe, w tym:",\n    "Aktywa_B_1": "B.1. - zapasy",\n    "Aktywa_B_2": "B.2. - należności krótkoterminowe",\n}\n\n# =============================================================================\n# NOTA PODATKOWA\n# =============================================================================\n\nNOTA_PODATKOWA = {\n    "P_ID_1": "Różnica między podstawą opodatkowania podatkiem dochodowym a wynikiem finansowym (zyskiem, stratą) brutto",\n    "P_ID_2": "Inne zmiany podstawy opodatkowania",\n    "P_ID_3": "Podstawa opodatkowania podatkiem dochodowym",\n    "P_ID_4": "Podatek dochodowy",\n}\n\n# =============================================================================\n# FUNKCJE POMOCNICZE\n# =============================================================================\n\n
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
                "Mikro": RZIS_MIKRO_KALKULACYJNY if 'RZIS_MIKRO_KALKULACYJNY' in dir() else {},
                "Mala": RZIS_MALA_KALKULACYJNY,
                "Inna": RZIS_INNA_KALKULACYJNY,
            }
        else:
            mappings = {
                "Mikro": RZIS_MIKRO_POROWNAWCZY if 'RZIS_MIKRO_POROWNAWCZY' in dir() else {},
                "Mala": RZIS_MALA_POROWNAWCZY,
                "Inna": RZIS_INNA_POROWNAWCZY,
            }
    elif sekcja == "Nota":
        return NOTA_PODATKOWA.get(kod, kod)
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
