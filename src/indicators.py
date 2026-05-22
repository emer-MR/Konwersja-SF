"""
Kalkulator wskaźników finansowych do analizy niewypłacalności.

Na podstawie:
1. M. Kubiczek, B. Sokół: Metodyka badania płynnościowej przesłanki niewypłacalności (Doradca 03/2016)
2. M. Kubiczek, B. Sokół: Metodyka badania majątkowej przesłanki niewypłacalności (Doradca 05/2016)
3. J. Michalak, B. Sokół: Zagrożenie niewypłacalnością (Doradca 32/2023)
4. K. Prędkiewicz: Uwarunkowania i metody zarządzania wypłacalnością MSP (2007)
5. Meritum. Postępowanie restrukturyzacyjne. Postępowanie upadłościowe (C.H. Beck)
6. E.I. Altman: Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy (1968)
7. A. Hołda: Prognozowanie bankructwa jednostki w warunkach gospodarki polskiej (2001)
8. J. Gajdka, D. Stos: Wykorzystanie analizy dyskryminacyjnej w ocenie kondycji finansowej przedsiębiorstw (1996)
9. D. Hadasik: Upadłość przedsiębiorstw w Polsce i metody jej prognozowania (1998)
10. E. Mączyńska: Ocena kondycji przedsiębiorstwa (1994)
11. D. Wierzba: Wczesne wykrywanie przedsiębiorstw zagrożonych upadłością (2000)

UWAGA: Ten moduł jest dostępny TYLKO w wersji lokalnej aplikacji (nie w wersji web).
"""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, DivisionByZero
from typing import Optional, Dict, List, Any
from enum import Enum


class OcenaWskaznika(Enum):
    """Ocena wartości wskaźnika."""
    OPTYMALNA = "optymalna"
    AKCEPTOWALNA = "akceptowalna"
    OSTRZEGAWCZA = "ostrzegawcza"
    KRYTYCZNA = "krytyczna"
    BRAK_DANYCH = "brak_danych"


@dataclass
class WynikWskaznika:
    """Wynik obliczenia pojedynczego wskaźnika."""
    nazwa: str
    skrot: str
    wartosc: Optional[Decimal]
    wartosc_str: str  # Sformatowana wartość (np. "125.5%" lub "1.25")
    ocena: OcenaWskaznika
    interpretacja: str
    wzor: str
    optimum: str = ""
    wartosc_krytyczna: str = ""
    zrodlo: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do słownika."""
        return {
            "nazwa": self.nazwa,
            "skrot": self.skrot,
            "wartosc": float(self.wartosc) if self.wartosc is not None else None,
            "wartosc_str": self.wartosc_str,
            "ocena": self.ocena.value,
            "interpretacja": self.interpretacja,
            "wzor": self.wzor,
            "optimum": self.optimum,
            "wartosc_krytyczna": self.wartosc_krytyczna,
            "zrodlo": self.zrodlo,
        }


@dataclass
class DaneFinansowe:
    """Dane finansowe pobrane ze sprawozdania do obliczeń wskaźników."""

    # AKTYWA
    aktywa_ogolem: Optional[Decimal] = None  # A - Suma bilansowa
    aktywa_trwale: Optional[Decimal] = None  # AT
    rzeczowe_aktywa_trwale: Optional[Decimal] = None  # RAT
    aktywa_obrotowe: Optional[Decimal] = None  # AO
    zapasy: Optional[Decimal] = None  # Zap
    naleznosci_krotkoterminowe: Optional[Decimal] = None  # Nal
    inwestycje_krotkoterminowe: Optional[Decimal] = None  # IK
    srodki_pieniezne: Optional[Decimal] = None  # ŚP
    krotkoterminowe_rmk: Optional[Decimal] = None  # RMK czynne

    # PASYWA
    pasywa_ogolem: Optional[Decimal] = None  # P = A
    kapital_wlasny: Optional[Decimal] = None  # KW
    rezerwy_na_zobowiazania: Optional[Decimal] = None  # Rez
    zobowiazania_ogolem: Optional[Decimal] = None  # ZO = ZD + ZK
    zobowiazania_dlugoterminowe: Optional[Decimal] = None  # ZD
    zobowiazania_krotkoterminowe: Optional[Decimal] = None  # ZK
    zobowiazania_wobec_jedn_powiazanych: Optional[Decimal] = None  # ZJP

    # RZiS
    przychody_netto_ze_sprzedazy: Optional[Decimal] = None  # PS
    koszty_dzialalnosci_operacyjnej: Optional[Decimal] = None  # KDO
    wynik_ze_sprzedazy: Optional[Decimal] = None  # WS
    pozostale_przychody_operacyjne: Optional[Decimal] = None  # PPO
    pozostale_koszty_operacyjne: Optional[Decimal] = None  # PKO
    wynik_z_dzialalnosci_operacyjnej: Optional[Decimal] = None  # WDO (EBIT w przybliżeniu)
    przychody_finansowe: Optional[Decimal] = None  # PF
    koszty_finansowe: Optional[Decimal] = None  # KF (w tym odsetki)
    zysk_strata_brutto: Optional[Decimal] = None  # ZB
    podatek_dochodowy: Optional[Decimal] = None  # PD
    zysk_strata_netto: Optional[Decimal] = None  # ZN
    amortyzacja: Optional[Decimal] = None  # Am (z not)

    # Rachunek przepływów pieniężnych
    przeplywy_operacyjne: Optional[Decimal] = None  # CFO
    przeplywy_inwestycyjne: Optional[Decimal] = None  # CFI
    przeplywy_finansowe: Optional[Decimal] = None  # CFF

    # Dane za poprzedni rok (do modeli dyskryminacyjnych)
    aktywa_ogolem_poprz: Optional[Decimal] = None
    zobowiazania_krotkoterminowe_poprz: Optional[Decimal] = None
    zapasy_poprz: Optional[Decimal] = None
    naleznosci_krotkoterminowe_poprz: Optional[Decimal] = None

    # Dodatkowe dane do modeli dyskryminacyjnych
    zysk_zatrzymany: Optional[Decimal] = None  # Skumulowany zysk zatrzymany (dla Altmana)
    naleznosci_handlowe: Optional[Decimal] = None  # Należności z tytułu dostaw i usług
    zobowiazania_handlowe: Optional[Decimal] = None  # Zobowiązania z tytułu dostaw i usług
    koszt_wytworzenia_sprzedanych: Optional[Decimal] = None  # Koszt wytworzenia sprzedanych produktów
    sprzedaz_produktow: Optional[Decimal] = None  # Przychody ze sprzedaży produktów

    @property
    def kapital_staly(self) -> Optional[Decimal]:
        """Kapitał stały = Kapitał własny + Zobowiązania długoterminowe"""
        if self.kapital_wlasny is None or self.zobowiazania_dlugoterminowe is None:
            return None
        return self.kapital_wlasny + self.zobowiazania_dlugoterminowe

    @property
    def srednia_suma_bilansowa(self) -> Optional[Decimal]:
        """Średnia suma bilansowa = (A_początek + A_koniec) / 2"""
        if self.aktywa_ogolem is None or self.aktywa_ogolem_poprz is None:
            return None
        return (self.aktywa_ogolem + self.aktywa_ogolem_poprz) / 2

    @property
    def srednie_zobowiazania_krotkoterm(self) -> Optional[Decimal]:
        """Średnie zobowiązania krótkoterminowe = (ZK_początek + ZK_koniec) / 2"""
        if self.zobowiazania_krotkoterminowe is None or self.zobowiazania_krotkoterminowe_poprz is None:
            return None
        return (self.zobowiazania_krotkoterminowe + self.zobowiazania_krotkoterminowe_poprz) / 2

    @property
    def kapital_pracujacy(self) -> Optional[Decimal]:
        """Kapitał pracujący (obrotowy netto) = Aktywa obrotowe - Zobowiązania krótkoterminowe"""
        if self.aktywa_obrotowe is None or self.zobowiazania_krotkoterminowe is None:
            return None
        return self.aktywa_obrotowe - self.zobowiazania_krotkoterminowe

    @property
    def srednie_zapasy(self) -> Optional[Decimal]:
        """Średnie zapasy = (Zap_początek + Zap_koniec) / 2"""
        if self.zapasy is None or self.zapasy_poprz is None:
            return None
        return (self.zapasy + self.zapasy_poprz) / 2

    @property
    def srednie_naleznosci_krotkoterm(self) -> Optional[Decimal]:
        """Średnie należności krótkoterminowe = (Nal_początek + Nal_koniec) / 2"""
        if self.naleznosci_krotkoterminowe is None or self.naleznosci_krotkoterminowe_poprz is None:
            return None
        return (self.naleznosci_krotkoterminowe + self.naleznosci_krotkoterminowe_poprz) / 2

    @property
    def nadwyzka_pieniezna(self) -> Optional[Decimal]:
        """Nadwyżka pieniężna (EBITDA przybliżenie) = Zysk netto + Amortyzacja"""
        if self.zysk_strata_netto is None:
            return None
        wynik = self.zysk_strata_netto
        if self.amortyzacja is not None:
            wynik += self.amortyzacja
        return wynik

    @property
    def przychody_ogolem(self) -> Optional[Decimal]:
        """Przychody z ogółu działalności = PS + PPO + PF"""
        if self.przychody_netto_ze_sprzedazy is None:
            return None
        wynik = self.przychody_netto_ze_sprzedazy
        if self.pozostale_przychody_operacyjne is not None:
            wynik += self.pozostale_przychody_operacyjne
        if self.przychody_finansowe is not None:
            wynik += self.przychody_finansowe
        return wynik


class KalkulatorWskaznikow:
    """Kalkulator wskaźników finansowych do analizy niewypłacalności."""

    def __init__(self, dane: DaneFinansowe):
        self.dane = dane
        self.wyniki: List[WynikWskaznika] = []

    def oblicz_wszystkie(self) -> List[WynikWskaznika]:
        """Oblicza wszystkie możliwe wskaźniki na podstawie dostępnych danych."""
        self.wyniki = []

        # WSKAŹNIKI PŁYNNOŚCI
        self._oblicz_plynnosc_biezaca()
        self._oblicz_plynnosc_szybka()
        self._oblicz_plynnosc_natychmiastowa()
        self._oblicz_wystarczalnosc_gotowkowa()
        self._oblicz_plynnosc_gotowkowa_cfo()
        self._oblicz_kapital_pracujacy()

        # WSKAŹNIKI ZADŁUŻENIA
        self._oblicz_zadluzenie_ogolne()
        self._oblicz_zadluzenie_kapitalu_wlasnego()
        self._oblicz_zadluzenie_dlugoterminowe()
        self._oblicz_pokrycie_nadwyzka_finansowa()
        self._oblicz_udzial_kapitalu_wlasnego()

        # WSKAŹNIKI RENTOWNOŚCI
        self._oblicz_roa()
        self._oblicz_ros()
        self._oblicz_roe()
        self._oblicz_rentownosc_operacyjna()

        # WSKAŹNIKI AKTYWNOŚCI I OBROTOWOŚCI
        self._oblicz_cykl_zapasow()
        self._oblicz_cykl_naleznosci()
        self._oblicz_cykl_zobowiazan()
        self._oblicz_cykl_konwersji_gotowki()
        self._oblicz_obrot_aktywami()

        # WSKAŹNIKI STRUKTURALNE
        self._oblicz_zlota_regula_bilansowa()
        self._oblicz_wskaznik_art_11_ust_5()

        # MODELE DYSKRYMINACYJNE - POLSKIE
        self._oblicz_model_poznanski()
        self._oblicz_model_prusaka_1r()
        self._oblicz_model_prusaka_2l()
        self._oblicz_model_prusaka_uproszczony()
        self._oblicz_model_holdy()
        self._oblicz_model_gajdki_stosa()
        self._oblicz_model_hadasik()
        self._oblicz_model_maczynskiej()
        self._oblicz_model_wierzby()

        # MODELE DYSKRYMINACYJNE - ZAGRANICZNE
        self._oblicz_model_altmana()
        self._oblicz_wilcox_gambler()

        return self.wyniki

    def _safe_divide(self, licznik: Optional[Decimal], mianownik: Optional[Decimal]) -> Optional[Decimal]:
        """Bezpieczne dzielenie z obsługą None i dzielenia przez zero."""
        if licznik is None or mianownik is None:
            return None
        if mianownik == 0:
            return None
        try:
            return licznik / mianownik
        except (DivisionByZero, InvalidOperation):
            return None

    def _format_percent(self, value: Optional[Decimal]) -> str:
        """Formatuje wartość jako procent (polski format z przecinkiem)."""
        if value is None:
            return "b/d"
        # Polski format: przecinek jako separator dziesiętny
        formatted = f"{float(value * 100):.2f}".replace(".", ",")
        return f"{formatted}%"

    def _format_ratio(self, value: Optional[Decimal]) -> str:
        """Formatuje wartość jako współczynnik (polski format z przecinkiem)."""
        if value is None:
            return "b/d"
        # Polski format: przecinek jako separator dziesiętny
        return f"{float(value):.2f}".replace(".", ",")

    def _format_currency(self, value: Optional[Decimal]) -> str:
        """Formatuje wartość jako kwotę (polski format)."""
        if value is None:
            return "b/d"
        # Polski format: spacja jako separator tysięcy, przecinek jako separator dziesiętny
        formatted = f"{float(value):,.2f}"
        # Zamień separatory na polskie (kropka->tymczasowy, przecinek->spacja, tymczasowy->przecinek)
        formatted = formatted.replace(",", " ").replace(".", ",")
        return formatted

    # =========================================================================
    # WSKAŹNIKI PŁYNNOŚCI
    # =========================================================================

    def _oblicz_plynnosc_biezaca(self):
        """Wskaźnik bieżącej płynności (Current Ratio)."""
        wartosc = self._safe_divide(
            self.dane.aktywa_obrotowe,
            self.dane.zobowiazania_krotkoterminowe
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia wskaźnika."
        elif wartosc < Decimal("1.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Brak pokrycia zobowiązań bieżących aktywami obrotowymi. Sygnał niewypłacalności."
        elif wartosc < Decimal("1.3"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Duże prawdopodobieństwo utraty wypłacalności (wg B. Prusaka)."
        elif wartosc <= Decimal("2.0"):
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Wartość optymalna. Aktywa obrotowe wystarczająco pokrywają zobowiązania bieżące."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Wysoka płynność. Możliwe nieefektywne wykorzystanie aktywów obrotowych."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik bieżącej płynności",
            skrot="CR",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Aktywa obrotowe / Zobowiązania krótkoterminowe",
            optimum="1,2 - 2,0",
            wartosc_krytyczna="< 1,0 (Meritum); < 1,3 (Prusak)",
            zrodlo="Meritum nb 149; B. Prusak",
        ))

    def _oblicz_plynnosc_szybka(self):
        """Wskaźnik szybkiej płynności (Quick Ratio / Acid Test)."""
        # Wzór: (AO - Zapasy - RMK) / ZK
        if self.dane.aktywa_obrotowe is None or self.dane.zobowiazania_krotkoterminowe is None:
            wartosc = None
        else:
            licznik = self.dane.aktywa_obrotowe
            if self.dane.zapasy is not None:
                licznik -= self.dane.zapasy
            if self.dane.krotkoterminowe_rmk is not None:
                licznik -= self.dane.krotkoterminowe_rmk
            wartosc = self._safe_divide(licznik, self.dane.zobowiazania_krotkoterminowe)

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia wskaźnika."
        elif wartosc < Decimal("1.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Zagrożenie bieżącej zdolności do terminowego regulowania zobowiązań."
        elif wartosc <= Decimal("1.2"):
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Wartość optymalna. Aktywa o wysokiej płynności pokrywają zobowiązania bieżące."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Wysoka płynność szybka."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik szybkiej płynności",
            skrot="QR",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Aktywa obrotowe - Zapasy - RMK) / Zobowiązania krótkoterminowe",
            optimum="1,0 - 1,2",
            wartosc_krytyczna="< 1,0",
            zrodlo="Meritum nb 150; B. Prusak",
        ))

    def _oblicz_plynnosc_natychmiastowa(self):
        """Wskaźnik podwyższonej (natychmiastowej) płynności (Cash Ratio)."""
        wartosc = self._safe_divide(
            self.dane.srodki_pieniezne,
            self.dane.zobowiazania_krotkoterminowe
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia wskaźnika."
        elif wartosc < Decimal("0.1"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "Bardzo niska zdolność do natychmiastowej spłaty zobowiązań."
        elif wartosc < Decimal("0.2"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska zdolność do natychmiastowej spłaty zobowiązań."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna zdolność do natychmiastowej spłaty zobowiązań z gotówki."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik płynności natychmiastowej",
            skrot="CaR",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Środki pieniężne / Zobowiązania krótkoterminowe",
            optimum="0,1 - 0,2 (zależne od branży)",
            wartosc_krytyczna="< 0,1",
            zrodlo="Meritum nb 140-141",
        ))

    def _oblicz_wystarczalnosc_gotowkowa(self):
        """Wskaźnik wystarczalności gotówkowej na spłatę zobowiązań."""
        wartosc = self._safe_divide(
            self.dane.przeplywy_operacyjne,
            self.dane.zobowiazania_ogolem
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak danych o przepływach pieniężnych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemne przepływy operacyjne - brak zdolności do obsługi zobowiązań z działalności."
        elif wartosc < Decimal("0.2"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska zdolność do obsługi zobowiązań z przepływów operacyjnych."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna zdolność do obsługi zobowiązań z przepływów operacyjnych."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik wystarczalności gotówkowej",
            skrot="WG",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Przepływy operacyjne (CFO) / Zobowiązania ogółem",
            optimum="Im wyższy, tym lepiej",
            wartosc_krytyczna="< 0",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_plynnosc_gotowkowa_cfo(self):
        """Wskaźnik płynności gotówkowej z przepływów."""
        wartosc = self._safe_divide(
            self.dane.przeplywy_operacyjne,
            self.dane.zobowiazania_krotkoterminowe
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak danych o przepływach pieniężnych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemne przepływy operacyjne."
        elif wartosc < Decimal("0.4"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska płynność z przepływów operacyjnych."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna płynność z przepływów operacyjnych."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik płynności gotówkowej (CFO)",
            skrot="PG",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Przepływy operacyjne (CFO) / Zobowiązania krótkoterminowe",
            optimum="> 0,4",
            wartosc_krytyczna="< 0",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_kapital_pracujacy(self):
        """Kapitał pracujący (obrotowy netto)."""
        wartosc = self.dane.kapital_pracujacy

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemny kapitał pracujący - zobowiązania krótkoterminowe przewyższają aktywa obrotowe."
        elif wartosc == Decimal("0"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Kapitał pracujący zerowy - brak buforu bezpieczeństwa."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Dodatni kapitał pracujący - przedsiębiorstwo ma bufor bezpieczeństwa płynności."

        self.wyniki.append(WynikWskaznika(
            nazwa="Kapitał pracujący",
            skrot="KP",
            wartosc=wartosc,
            wartosc_str=self._format_currency(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Aktywa obrotowe - Zobowiązania krótkoterminowe",
            optimum="> 0",
            wartosc_krytyczna="< 0",
            zrodlo="Literatura finansowa",
        ))

    # =========================================================================
    # WSKAŹNIKI ZADŁUŻENIA
    # =========================================================================

    def _oblicz_zadluzenie_ogolne(self):
        """Wskaźnik ogólnego zadłużenia."""
        wartosc = self._safe_divide(
            self.dane.zobowiazania_ogolem,
            self.dane.aktywa_ogolem
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("0.80"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Bardzo wysokie zadłużenie. Duże ryzyko finansowe."
        elif wartosc > Decimal("0.67"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Wysokie zadłużenie - powyżej zalecanego poziomu."
        elif wartosc >= Decimal("0.57"):
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Poziom zadłużenia w granicach optymalnych."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Niskie zadłużenie. Bezpieczna struktura finansowania."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik ogólnego zadłużenia",
            skrot="WOZ",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zobowiązania ogółem / Aktywa ogółem × 100%",
            optimum="57% - 67%",
            wartosc_krytyczna="> 67%",
            zrodlo="Meritum nb 155",
        ))

    def _oblicz_zadluzenie_kapitalu_wlasnego(self):
        """Wskaźnik zadłużenia kapitału własnego."""
        wartosc = self._safe_divide(
            self.dane.zobowiazania_ogolem,
            self.dane.kapital_wlasny
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif self.dane.kapital_wlasny is not None and self.dane.kapital_wlasny < 0:
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemny kapitał własny! Zobowiązania przewyższają aktywa."
        elif wartosc > Decimal("3.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Bardzo wysokie ryzyko niewypłacalności (wg Prędkiewicz dla polskich MSP)."
        elif wartosc > Decimal("1.0"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Kapitał obcy przewyższa kapitał własny."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Bezpieczna relacja kapitału obcego do własnego."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik zadłużenia kapitału własnego",
            skrot="WZK",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zobowiązania ogółem / Kapitał własny",
            optimum="< 1:1 (duże firmy); < 3:1 (MSP)",
            wartosc_krytyczna="> 3:1 (duże ryzyko dla polskich MSP)",
            zrodlo="Meritum nb 155; K. Prędkiewicz",
        ))

    def _oblicz_zadluzenie_dlugoterminowe(self):
        """Wskaźnik zadłużenia długoterminowego."""
        wartosc = self._safe_divide(
            self.dane.zobowiazania_dlugoterminowe,
            self.dane.kapital_wlasny
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("1.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Zobowiązania długoterminowe przewyższają kapitał własny."
        elif wartosc > Decimal("0.5"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Podwyższony poziom zadłużenia długoterminowego."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Bezpieczny poziom zadłużenia długoterminowego."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik zadłużenia długoterminowego",
            skrot="WZD",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zobowiązania długoterminowe / Kapitał własny",
            optimum="0,5 - 1,0",
            wartosc_krytyczna="> 1,0",
            zrodlo="Meritum nb 155",
        ))

    def _oblicz_pokrycie_nadwyzka_finansowa(self):
        """Wskaźnik pokrycia zobowiązań uproszczoną nadwyżką finansową."""
        if self.dane.zysk_strata_netto is None or self.dane.zobowiazania_ogolem is None:
            wartosc = None
        else:
            licznik = self.dane.zysk_strata_netto
            if self.dane.amortyzacja is not None:
                licznik += self.dane.amortyzacja
            wartosc = self._safe_divide(licznik, self.dane.zobowiazania_ogolem)

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych (brak amortyzacji lub zysku netto)."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemna nadwyżka finansowa - strata netto przewyższa amortyzację."
        elif wartosc < Decimal("0.1"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Wartość < 0,1 może oznaczać kłopoty finansowe (wg B. Prusaka)."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna zdolność do obsługi zobowiązań z nadwyżki finansowej."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik pokrycia zobowiązań nadwyżką finansową",
            skrot="PZN",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Zysk netto + Amortyzacja) / Zobowiązania ogółem",
            optimum="> 0,1",
            wartosc_krytyczna="< 0,1",
            zrodlo="B. Prusak",
        ))

    def _oblicz_udzial_kapitalu_wlasnego(self):
        """Wskaźnik udziału kapitału własnego w finansowaniu majątku."""
        wartosc = self._safe_divide(
            self.dane.kapital_wlasny,
            self.dane.aktywa_ogolem
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemny kapitał własny - aktywa nie pokrywają zobowiązań."
        elif wartosc < Decimal("0.20"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "Bardzo niski udział kapitału własnego - wysokie ryzyko finansowe."
        elif wartosc < Decimal("0.33"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niski udział kapitału własnego."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalny udział kapitału własnego w finansowaniu."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik udziału kapitału własnego",
            skrot="UKW",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Kapitał własny / Aktywa ogółem × 100%",
            optimum="> 33%",
            wartosc_krytyczna="< 20%",
            zrodlo="Literatura finansowa",
        ))

    # =========================================================================
    # WSKAŹNIKI RENTOWNOŚCI
    # =========================================================================

    def _oblicz_roa(self):
        """Rentowność aktywów (ROA)."""
        wartosc = self._safe_divide(
            self.dane.zysk_strata_netto,
            self.dane.aktywa_ogolem
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemna rentowność aktywów - przedsiębiorstwo generuje straty."
        elif wartosc < Decimal("0.02"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska rentowność aktywów."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna efektywność wykorzystania majątku."

        self.wyniki.append(WynikWskaznika(
            nazwa="Rentowność aktywów",
            skrot="ROA",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zysk netto / Aktywa ogółem × 100%",
            optimum="Zależne od branży",
            wartosc_krytyczna="< 0% (przez kilka lat)",
            zrodlo="Meritum nb 152; B. Prusak",
        ))

    def _oblicz_ros(self):
        """Rentowność sprzedaży (ROS)."""
        wartosc = self._safe_divide(
            self.dane.zysk_strata_netto,
            self.dane.przychody_netto_ze_sprzedazy
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemna rentowność sprzedaży - sprzedaż generuje straty."
        elif wartosc < Decimal("0.02"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska rentowność sprzedaży."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna rentowność sprzedaży."

        self.wyniki.append(WynikWskaznika(
            nazwa="Rentowność sprzedaży",
            skrot="ROS",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zysk netto / Przychody ze sprzedaży × 100%",
            optimum="Zależne od branży",
            wartosc_krytyczna="< 0%",
            zrodlo="Meritum nb 152",
        ))

    def _oblicz_roe(self):
        """Rentowność kapitału własnego (ROE)."""
        wartosc = self._safe_divide(
            self.dane.zysk_strata_netto,
            self.dane.kapital_wlasny
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif self.dane.kapital_wlasny is not None and self.dane.kapital_wlasny < 0:
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemny kapitał własny - wskaźnik nieinterpretowalny."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemna rentowność kapitału własnego - straty dla właścicieli."
        elif wartosc < Decimal("0.05"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska rentowność kapitału własnego."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna rentowność kapitału własnego."

        self.wyniki.append(WynikWskaznika(
            nazwa="Rentowność kapitału własnego",
            skrot="ROE",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Zysk netto / Kapitał własny × 100%",
            optimum="Zależne od branży, > stopa wolna od ryzyka",
            wartosc_krytyczna="< 0% lub spadkowy trend",
            zrodlo="Meritum nb 153",
        ))

    def _oblicz_rentownosc_operacyjna(self):
        """Rentowność operacyjna sprzedaży."""
        # Licznik: Wynik z działalności operacyjnej
        # Mianownik: Przychody netto ze sprzedaży + Pozostałe przychody operacyjne
        if self.dane.wynik_z_dzialalnosci_operacyjnej is None:
            wartosc = None
        else:
            mianownik = self.dane.przychody_netto_ze_sprzedazy or Decimal("0")
            if self.dane.pozostale_przychody_operacyjne is not None:
                mianownik += self.dane.pozostale_przychody_operacyjne
            wartosc = self._safe_divide(self.dane.wynik_z_dzialalnosci_operacyjnej, mianownik)

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Ujemna rentowność operacyjna - działalność operacyjna generuje straty."
        elif wartosc < Decimal("0.05"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska rentowność operacyjna."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Akceptowalna rentowność operacyjna."

        self.wyniki.append(WynikWskaznika(
            nazwa="Rentowność operacyjna sprzedaży",
            skrot="ROp",
            wartosc=wartosc,
            wartosc_str=self._format_percent(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Wynik z działalności operacyjnej / (PS + PPO) × 100%",
            optimum="Zależne od branży",
            wartosc_krytyczna="< 0%",
            zrodlo="Literatura finansowa",
        ))

    # =========================================================================
    # WSKAŹNIKI AKTYWNOŚCI I OBROTOWOŚCI
    # =========================================================================

    def _oblicz_cykl_zapasow(self):
        """Wskaźnik cyklu zapasów (w dniach)."""
        # Cykl zapasów = (Średnie zapasy / Przychody netto ze sprzedaży) × 365
        if self.dane.srednie_zapasy is not None:
            wartosc = self._safe_divide(
                self.dane.srednie_zapasy * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        elif self.dane.zapasy is not None:
            # Fallback - użyj bieżących zapasów
            wartosc = self._safe_divide(
                self.dane.zapasy * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        else:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("90"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Długi cykl zapasów - kapitał zamrożony w zapasach."
        elif wartosc > Decimal("60"):
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Umiarkowany cykl zapasów."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Krótki cykl zapasów - efektywne zarządzanie."

        self.wyniki.append(WynikWskaznika(
            nazwa="Cykl zapasów",
            skrot="CZ",
            wartosc=wartosc,
            wartosc_str=f"{float(wartosc):.1f}".replace(".", ",") + " dni" if wartosc else "b/d",
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Średnie zapasy / Przychody netto ze sprzedaży) × 365 dni",
            optimum="Zależne od branży, im krótszy tym lepiej",
            wartosc_krytyczna="> 90 dni",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_cykl_naleznosci(self):
        """Wskaźnik cyklu należności (w dniach)."""
        # Cykl należności = (Średnie należności / Przychody netto ze sprzedaży) × 365
        if self.dane.srednie_naleznosci_krotkoterm is not None:
            wartosc = self._safe_divide(
                self.dane.srednie_naleznosci_krotkoterm * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        elif self.dane.naleznosci_krotkoterminowe is not None:
            wartosc = self._safe_divide(
                self.dane.naleznosci_krotkoterminowe * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        else:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("90"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Bardzo długi cykl należności - problemy ze ściągalnością."
        elif wartosc > Decimal("60"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Długi cykl należności."
        elif wartosc > Decimal("30"):
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Umiarkowany cykl należności."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Krótki cykl należności - efektywne windykowanie."

        self.wyniki.append(WynikWskaznika(
            nazwa="Cykl należności",
            skrot="CN",
            wartosc=wartosc,
            wartosc_str=f"{float(wartosc):.1f}".replace(".", ",") + " dni" if wartosc else "b/d",
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Średnie należności / Przychody netto ze sprzedaży) × 365 dni",
            optimum="< 60 dni",
            wartosc_krytyczna="> 90 dni",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_cykl_zobowiazan(self):
        """Wskaźnik cyklu zobowiązań (w dniach)."""
        # Cykl zobowiązań = (Średnie zobowiązania krótkoterm. / Przychody netto ze sprzedaży) × 365
        if self.dane.srednie_zobowiazania_krotkoterm is not None:
            wartosc = self._safe_divide(
                self.dane.srednie_zobowiazania_krotkoterm * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        elif self.dane.zobowiazania_krotkoterminowe is not None:
            wartosc = self._safe_divide(
                self.dane.zobowiazania_krotkoterminowe * Decimal("365"),
                self.dane.przychody_netto_ze_sprzedazy
            )
        else:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("90"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Bardzo długi cykl zobowiązań - może wskazywać na problemy z płynnością."
        elif wartosc < Decimal("30"):
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Krótki cykl zobowiązań - szybka spłata dostawców."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Umiarkowany cykl zobowiązań."

        self.wyniki.append(WynikWskaznika(
            nazwa="Cykl zobowiązań",
            skrot="CZob",
            wartosc=wartosc,
            wartosc_str=f"{float(wartosc):.1f}".replace(".", ",") + " dni" if wartosc else "b/d",
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Średnie zobowiązania krótkoterm. / Przychody netto ze sprzedaży) × 365 dni",
            optimum="30-60 dni",
            wartosc_krytyczna="> 90 dni (może oznaczać problemy)",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_cykl_konwersji_gotowki(self):
        """Cykl konwersji gotówki (Cash Conversion Cycle)."""
        # CKG = Cykl zapasów + Cykl należności - Cykl zobowiązań
        # Obliczamy składniki
        cykl_zap = None
        cykl_nal = None
        cykl_zob = None

        if self.dane.zapasy is not None and self.dane.przychody_netto_ze_sprzedazy:
            zap = self.dane.srednie_zapasy if self.dane.srednie_zapasy else self.dane.zapasy
            cykl_zap = self._safe_divide(zap * Decimal("365"), self.dane.przychody_netto_ze_sprzedazy)

        if self.dane.naleznosci_krotkoterminowe is not None and self.dane.przychody_netto_ze_sprzedazy:
            nal = self.dane.srednie_naleznosci_krotkoterm if self.dane.srednie_naleznosci_krotkoterm else self.dane.naleznosci_krotkoterminowe
            cykl_nal = self._safe_divide(nal * Decimal("365"), self.dane.przychody_netto_ze_sprzedazy)

        if self.dane.zobowiazania_krotkoterminowe is not None and self.dane.przychody_netto_ze_sprzedazy:
            zob = self.dane.srednie_zobowiazania_krotkoterm if self.dane.srednie_zobowiazania_krotkoterm else self.dane.zobowiazania_krotkoterminowe
            cykl_zob = self._safe_divide(zob * Decimal("365"), self.dane.przychody_netto_ze_sprzedazy)

        if cykl_zap is not None and cykl_nal is not None and cykl_zob is not None:
            wartosc = cykl_zap + cykl_nal - cykl_zob
        else:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Ujemny cykl konwersji - przedsiębiorstwo finansuje się ze środków dostawców."
        elif wartosc < Decimal("30"):
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Krótki cykl konwersji gotówki."
        elif wartosc < Decimal("60"):
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Umiarkowany cykl konwersji gotówki."
        else:
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Długi cykl konwersji - duże zapotrzebowanie na kapitał obrotowy."

        self.wyniki.append(WynikWskaznika(
            nazwa="Cykl konwersji gotówki",
            skrot="CKG",
            wartosc=wartosc,
            wartosc_str=f"{float(wartosc):.1f}".replace(".", ",") + " dni" if wartosc else "b/d",
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Cykl zapasów + Cykl należności - Cykl zobowiązań",
            optimum="Im krótszy, tym lepiej (ujemny = bardzo dobry)",
            wartosc_krytyczna="> 60 dni",
            zrodlo="Literatura finansowa",
        ))

    def _oblicz_obrot_aktywami(self):
        """Wskaźnik obrotu aktywami."""
        if self.dane.srednia_suma_bilansowa is not None:
            wartosc = self._safe_divide(
                self.dane.przychody_netto_ze_sprzedazy,
                self.dane.srednia_suma_bilansowa
            )
        else:
            wartosc = self._safe_divide(
                self.dane.przychody_netto_ze_sprzedazy,
                self.dane.aktywa_ogolem
            )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("0.5"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Niska rotacja aktywów - nieefektywne wykorzystanie majątku."
        elif wartosc < Decimal("1.0"):
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Umiarkowana rotacja aktywów."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Wysoka rotacja aktywów - efektywne wykorzystanie majątku."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik obrotu aktywami",
            skrot="OA",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Przychody netto ze sprzedaży / Średni stan aktywów",
            optimum="> 1,0 (zależne od branży)",
            wartosc_krytyczna="< 0,5",
            zrodlo="Literatura finansowa",
        ))

    # =========================================================================
    # WSKAŹNIKI STRUKTURALNE
    # =========================================================================

    def _oblicz_zlota_regula_bilansowa(self):
        """Złota reguła bilansowa."""
        wartosc = self._safe_divide(
            self.dane.kapital_wlasny,
            self.dane.aktywa_trwale
        )

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc < Decimal("1.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Naruszenie złotej reguły bilansowej. Aktywa trwałe finansowane kapitałem obcym."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Złota reguła bilansowa spełniona. Aktywa trwałe w pełni finansowane kapitałem własnym."

        self.wyniki.append(WynikWskaznika(
            nazwa="Złota reguła bilansowa",
            skrot="ZRB",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="Kapitał własny / Aktywa trwałe",
            optimum="≥ 1,0",
            wartosc_krytyczna="< 1,0",
            zrodlo="Meritum nb 153",
        ))

    def _oblicz_wskaznik_art_11_ust_5(self):
        """Wskaźnik pokrycia zobowiązań wg art. 11 ust. 5 PrUpad."""
        # Wzór: (ZO - Rez - ZJP) / (A - składniki wyłączone)
        # Uproszczenie: używamy dostępnych danych
        if self.dane.zobowiazania_ogolem is None or self.dane.aktywa_ogolem is None:
            wartosc = None
        else:
            licznik = self.dane.zobowiazania_ogolem
            if self.dane.rezerwy_na_zobowiazania is not None:
                licznik -= self.dane.rezerwy_na_zobowiazania
            if self.dane.zobowiazania_wobec_jedn_powiazanych is not None:
                licznik -= self.dane.zobowiazania_wobec_jedn_powiazanych
            wartosc = self._safe_divide(licznik, self.dane.aktywa_ogolem)

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc > Decimal("1.0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Zobowiązania przewyższają aktywa! Jeśli stan trwa > 24 miesięcy = niewypłacalność zadłużeniowa (art. 11 ust. 2 PrUpad)."
        else:
            ocena = OcenaWskaznika.AKCEPTOWALNA
            interpretacja = "Aktywa pokrywają zobowiązania. Brak przesłanki majątkowej niewypłacalności."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wskaźnik pokrycia zobowiązań (art. 11 ust. 5 PrUpad)",
            skrot="WPZ",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="(Zobowiązania - Rezerwy - Zob. wobec jedn. powiązanych) / Aktywa",
            optimum="< 1,0",
            wartosc_krytyczna="> 1,0 przez ponad 24 miesiące",
            zrodlo="Art. 11 ust. 2 i 5 PrUpad",
        ))

    # =========================================================================
    # MODELE DYSKRYMINACYJNE
    # =========================================================================

    def _oblicz_model_poznanski(self):
        """Model poznański (Hamrol, Czajka, Piechocki, 2004)."""
        # FD = 3,562 × X₁ + 1,588 × X₂ + 4,288 × X₃ + 6,719 × X₄ - 2,368
        # X₁ = Zysk netto / Suma bilansowa
        # X₂ = (AO - Zapasy) / ZK
        # X₃ = Kapitał stały / Suma bilansowa
        # X₄ = Wynik ze sprzedaży / Przychody ze sprzedaży

        try:
            x1 = self._safe_divide(self.dane.zysk_strata_netto, self.dane.aktywa_ogolem)

            if self.dane.aktywa_obrotowe is not None and self.dane.zobowiazania_krotkoterminowe is not None:
                ao_bez_zapasow = self.dane.aktywa_obrotowe
                if self.dane.zapasy is not None:
                    ao_bez_zapasow -= self.dane.zapasy
                x2 = self._safe_divide(ao_bez_zapasow, self.dane.zobowiazania_krotkoterminowe)
            else:
                x2 = None

            x3 = self._safe_divide(self.dane.kapital_staly, self.dane.aktywa_ogolem)
            x4 = self._safe_divide(self.dane.wynik_ze_sprzedazy, self.dane.przychody_netto_ze_sprzedazy)

            if all(v is not None for v in [x1, x2, x3, x4]):
                wartosc = (Decimal("3.562") * x1 +
                          Decimal("1.588") * x2 +
                          Decimal("4.288") * x3 +
                          Decimal("6.719") * x4 -
                          Decimal("2.368"))
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie upadłością (FD < 0)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na brak zagrożenia upadłością (FD > 0)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model poznański",
            skrot="FD_P",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="3,562×X₁ + 1,588×X₂ + 4,288×X₃ + 6,719×X₄ - 2,368",
            optimum="> 0",
            wartosc_krytyczna="< 0",
            zrodlo="Hamrol, Czajka, Piechocki (2004); trafność 96%",
        ))

    def _oblicz_model_prusaka_1r(self):
        """Model B. Prusaka - wyprzedzenie 1 rok (dedykowany MSP)."""
        # FD = 6,9973 × X₁ + 0,1191 × X₂ + 0,1932 × X₃ - 1,1760
        # X₁ = Wynik ze sprzedaży / Średnia suma bilansowa
        # X₂ = Koszty operacyjne / Średnie zobowiązania krótkoterm.
        # X₃ = Aktywa obrotowe / Zobowiązania krótkoterminowe

        try:
            x1 = self._safe_divide(self.dane.wynik_ze_sprzedazy, self.dane.srednia_suma_bilansowa)
            x2 = self._safe_divide(self.dane.koszty_dzialalnosci_operacyjnej, self.dane.srednie_zobowiazania_krotkoterm)
            x3 = self._safe_divide(self.dane.aktywa_obrotowe, self.dane.zobowiazania_krotkoterminowe)

            if all(v is not None for v in [x1, x2, x3]):
                wartosc = (Decimal("6.9973") * x1 +
                          Decimal("0.1191") * x2 +
                          Decimal("0.1932") * x3 -
                          Decimal("1.1760"))
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak danych (model wymaga danych za 2 lata)."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie w perspektywie 1 roku."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na brak zagrożenia w perspektywie 1 roku."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model Prusaka (1 rok)",
            skrot="FD_PR1",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="6,9973×X₁ + 0,1191×X₂ + 0,1932×X₃ - 1,1760",
            optimum="> 0",
            wartosc_krytyczna="< 0",
            zrodlo="B. Prusak; dedykowany MSP produkcyjne",
        ))

    def _oblicz_model_prusaka_2l(self):
        """Model B. Prusaka - wyprzedzenie 2 lata (dedykowany MSP)."""
        # FD = 3,7657 × X₁ + 0,1049 × X₂ - 1,6765 × X₃ + 3,5230 × X₄ - 0,3758
        # X₁ = Wynik ze sprzedaży / Średnia suma bilansowa
        # X₂ = Koszty operacyjne / Średnie zobowiązania krótkoterm.
        # X₃ = Zobowiązania krótkoterminowe / Suma bilansowa
        # X₄ = Wynik z działalności operacyjnej / Średnia suma bilansowa

        try:
            x1 = self._safe_divide(self.dane.wynik_ze_sprzedazy, self.dane.srednia_suma_bilansowa)
            x2 = self._safe_divide(self.dane.koszty_dzialalnosci_operacyjnej, self.dane.srednie_zobowiazania_krotkoterm)
            x3 = self._safe_divide(self.dane.zobowiazania_krotkoterminowe, self.dane.aktywa_ogolem)
            x4 = self._safe_divide(self.dane.wynik_z_dzialalnosci_operacyjnej, self.dane.srednia_suma_bilansowa)

            if all(v is not None for v in [x1, x2, x3, x4]):
                wartosc = (Decimal("3.7657") * x1 +
                          Decimal("0.1049") * x2 -
                          Decimal("1.6765") * x3 +
                          Decimal("3.5230") * x4 -
                          Decimal("0.3758"))
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak danych (model wymaga danych za 2 lata)."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie w perspektywie 2 lat."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na brak zagrożenia w perspektywie 2 lat."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model Prusaka (2 lata)",
            skrot="FD_PR2",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="3,7657×X₁ + 0,1049×X₂ - 1,6765×X₃ + 3,5230×X₄ - 0,3758",
            optimum="> 0",
            wartosc_krytyczna="< 0",
            zrodlo="B. Prusak; dedykowany MSP produkcyjne",
        ))

    def _oblicz_model_prusaka_uproszczony(self):
        """Model B. Prusaka - wersja uproszczona (alternatywna)."""
        # Z = 1,438 × X₁ + 0,188 × X₂ + 5,023 × X₃ - 1,871
        # X₁ = (Zysk netto + Amortyzacja) / Zobowiązania ogółem
        # X₂ = Koszty operacyjne / Zobowiązania krótkoterminowe
        # X₃ = Zysk ze sprzedaży / Suma bilansowa

        try:
            x1 = self._safe_divide(self.dane.nadwyzka_pieniezna, self.dane.zobowiazania_ogolem)
            x2 = self._safe_divide(self.dane.koszty_dzialalnosci_operacyjnej, self.dane.zobowiazania_krotkoterminowe)
            x3 = self._safe_divide(self.dane.wynik_ze_sprzedazy, self.dane.aktywa_ogolem)

            if all(v is not None for v in [x1, x2, x3]):
                wartosc = (Decimal("1.438") * x1 +
                          Decimal("0.188") * x2 +
                          Decimal("5.023") * x3 -
                          Decimal("1.871"))
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc < Decimal("-0.7"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie upadłością (Z < -0,7)."
        elif wartosc <= Decimal("0.2"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Strefa szara - nieokreślone ryzyko (-0,7 ≤ Z ≤ 0,2)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na brak zagrożenia upadłością (Z > 0,2)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model Prusaka (uproszczony)",
            skrot="FD_PRU",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="1,438×X₁ + 0,188×X₂ + 5,023×X₃ - 1,871",
            optimum="> 0,2",
            wartosc_krytyczna="< -0,7",
            zrodlo="B. Prusak (wersja alternatywna)",
        ))

    def _oblicz_model_holdy(self):
        """Model A. Hołdy (2001)."""
        # Z = 0,605 + 0,681×X₁ - 0,0196×X₂ + 0,157×X₃ + 0,00969×X₄ + 0,000672×X₅
        # X₁ = Aktywa obrotowe / Zobowiązania krótkoterminowe
        # X₂ = (Zobowiązania ogółem / Aktywa ogółem) × 100
        # X₃ = Przychody z ogółu działalności / Średni stan aktywów
        # X₄ = (Zysk netto / Średni stan aktywów) × 100
        # X₅ = (Średnie zobowiązania krótkoterm. / Koszt wytworzenia) × 360

        try:
            x1 = self._safe_divide(self.dane.aktywa_obrotowe, self.dane.zobowiazania_krotkoterminowe)
            x2 = self._safe_divide(self.dane.zobowiazania_ogolem, self.dane.aktywa_ogolem)
            if x2 is not None:
                x2 = x2 * Decimal("100")

            srednie_aktywa = self.dane.srednia_suma_bilansowa or self.dane.aktywa_ogolem
            x3 = self._safe_divide(self.dane.przychody_ogolem, srednie_aktywa)

            x4 = self._safe_divide(self.dane.zysk_strata_netto, srednie_aktywa)
            if x4 is not None:
                x4 = x4 * Decimal("100")

            # X₅ - uproszczenie: używamy kosztów działalności operacyjnej
            srednie_zk = self.dane.srednie_zobowiazania_krotkoterm or self.dane.zobowiazania_krotkoterminowe
            koszt = self.dane.koszt_wytworzenia_sprzedanych or self.dane.koszty_dzialalnosci_operacyjnej
            x5 = self._safe_divide(srednie_zk, koszt)
            if x5 is not None:
                x5 = x5 * Decimal("360")

            if all(v is not None for v in [x1, x2, x3, x4, x5]):
                wartosc = (Decimal("0.605") +
                          Decimal("0.681") * x1 -
                          Decimal("0.0196") * x2 +
                          Decimal("0.157") * x3 +
                          Decimal("0.00969") * x4 +
                          Decimal("0.000672") * x5)
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc <= Decimal("-0.3"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Wysokie zagrożenie upadłością (Z ≤ -0,3)."
        elif wartosc < Decimal("0.1"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Strefa szara - nieokreślone ryzyko (-0,3 < Z < 0,1)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na niewielkie zagrożenie upadłością (Z ≥ 0,1)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model A. Hołdy",
            skrot="FD_H",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="0,605 + 0,681×X₁ - 0,0196×X₂ + 0,157×X₃ + 0,00969×X₄ + 0,000672×X₅",
            optimum="≥ 0,1",
            wartosc_krytyczna="≤ -0,3",
            zrodlo="A. Hołda (2001)",
        ))

    def _oblicz_model_gajdki_stosa(self):
        """Model J. Gajdki i D. Stosa (1996)."""
        # Z = 0,7732059 - 0,0856425×X₁ - 0,0007747×X₂ + 0,9220985×X₃ + 0,6535995×X₄ - 0,594687×X₅
        # X₁ = Przychody ze sprzedaży / Aktywa ogółem
        # X₂ = (Zobowiązania krótkoterminowe / Koszt wytworzenia) × 360
        # X₃ = Zysk netto / Aktywa ogółem
        # X₄ = Zysk netto / Przychody ze sprzedaży
        # X₅ = Zobowiązania ogółem / Aktywa ogółem

        try:
            x1 = self._safe_divide(self.dane.przychody_netto_ze_sprzedazy, self.dane.aktywa_ogolem)

            koszt = self.dane.koszt_wytworzenia_sprzedanych or self.dane.koszty_dzialalnosci_operacyjnej
            x2 = self._safe_divide(self.dane.zobowiazania_krotkoterminowe, koszt)
            if x2 is not None:
                x2 = x2 * Decimal("360")

            x3 = self._safe_divide(self.dane.zysk_strata_netto, self.dane.aktywa_ogolem)
            x4 = self._safe_divide(self.dane.zysk_strata_netto, self.dane.przychody_netto_ze_sprzedazy)
            x5 = self._safe_divide(self.dane.zobowiazania_ogolem, self.dane.aktywa_ogolem)

            if all(v is not None for v in [x1, x2, x3, x4, x5]):
                wartosc = (Decimal("0.7732059") -
                          Decimal("0.0856425") * x1 -
                          Decimal("0.0007747") * x2 +
                          Decimal("0.9220985") * x3 +
                          Decimal("0.6535995") * x4 -
                          Decimal("0.594687") * x5)
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc <= Decimal("0.45"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie upadłością (Z ≤ 0,45)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na dobrą kondycję finansową (Z > 0,45)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model Gajdki-Stosa",
            skrot="FD_GS",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="0,773 - 0,086×X₁ - 0,0008×X₂ + 0,922×X₃ + 0,654×X₄ - 0,595×X₅",
            optimum="> 0,45",
            wartosc_krytyczna="≤ 0,45",
            zrodlo="J. Gajdka, D. Stos (1996)",
        ))

    def _oblicz_model_hadasik(self):
        """Model D. Hadasik (1998)."""
        # Z = 0,335969×X₁ - 0,71245×X₂ - 2,4716×X₃ + 1,46434×X₄ + 0,00246069×X₅ - 0,0138937×X₆ + 0,00243387×X₇ + 2,59323
        # X₁ = Aktywa obrotowe / Zobowiązania krótkoterminowe
        # X₂ = (Aktywa obrotowe - Zapasy) / Zobowiązania krótkoterminowe
        # X₃ = Zobowiązania ogółem / Aktywa ogółem
        # X₄ = (Aktywa obrotowe - Zobowiązania krótkoterminowe) / Aktywa ogółem
        # X₅ = (Należności krótkoterminowe / Przychody ze sprzedaży) × 365
        # X₆ = (Zapasy / Przychody ze sprzedaży) × 365
        # X₇ = Zysk netto / Zapasy

        try:
            x1 = self._safe_divide(self.dane.aktywa_obrotowe, self.dane.zobowiazania_krotkoterminowe)

            ao_bez_zap = self.dane.aktywa_obrotowe
            if self.dane.zapasy is not None and ao_bez_zap is not None:
                ao_bez_zap -= self.dane.zapasy
            x2 = self._safe_divide(ao_bez_zap, self.dane.zobowiazania_krotkoterminowe)

            x3 = self._safe_divide(self.dane.zobowiazania_ogolem, self.dane.aktywa_ogolem)
            x4 = self._safe_divide(self.dane.kapital_pracujacy, self.dane.aktywa_ogolem)

            x5 = self._safe_divide(self.dane.naleznosci_krotkoterminowe, self.dane.przychody_netto_ze_sprzedazy)
            if x5 is not None:
                x5 = x5 * Decimal("365")

            x6 = self._safe_divide(self.dane.zapasy, self.dane.przychody_netto_ze_sprzedazy)
            if x6 is not None:
                x6 = x6 * Decimal("365")

            x7 = self._safe_divide(self.dane.zysk_strata_netto, self.dane.zapasy)

            if all(v is not None for v in [x1, x2, x3, x4, x5, x6, x7]):
                wartosc = (Decimal("0.335969") * x1 -
                          Decimal("0.71245") * x2 -
                          Decimal("2.4716") * x3 +
                          Decimal("1.46434") * x4 +
                          Decimal("0.00246069") * x5 -
                          Decimal("0.0138937") * x6 +
                          Decimal("0.00243387") * x7 +
                          Decimal("2.59323"))
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc < Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Model wskazuje na zagrożenie upadłością (Z < 0)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na brak zagrożenia upadłością (Z ≥ 0)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model D. Hadasik",
            skrot="FD_HD",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="0,336×X₁ - 0,712×X₂ - 2,472×X₃ + 1,464×X₄ + 0,002×X₅ - 0,014×X₆ + 0,002×X₇ + 2,593",
            optimum="≥ 0",
            wartosc_krytyczna="< 0",
            zrodlo="D. Hadasik (1998)",
        ))

    def _oblicz_model_maczynskiej(self):
        """Model E. Mączyńskiej (1994)."""
        # Z = 1,50×X₁ + 0,08×X₂ + 10,00×X₃ + 5,00×X₄ + 0,30×X₅ + 0,10×X₆
        # X₁ = Nadwyżka pieniężna / Zobowiązania ogółem
        # X₂ = Aktywa ogółem / Zobowiązania ogółem
        # X₃ = Zysk brutto / Aktywa ogółem
        # X₄ = Zysk brutto / Przychody ze sprzedaży
        # X₅ = Zapasy / Przychody ze sprzedaży
        # X₆ = Przychody ze sprzedaży / Aktywa ogółem

        try:
            x1 = self._safe_divide(self.dane.nadwyzka_pieniezna, self.dane.zobowiazania_ogolem)
            x2 = self._safe_divide(self.dane.aktywa_ogolem, self.dane.zobowiazania_ogolem)
            x3 = self._safe_divide(self.dane.zysk_strata_brutto, self.dane.aktywa_ogolem)
            x4 = self._safe_divide(self.dane.zysk_strata_brutto, self.dane.przychody_netto_ze_sprzedazy)
            x5 = self._safe_divide(self.dane.zapasy, self.dane.przychody_netto_ze_sprzedazy)
            x6 = self._safe_divide(self.dane.przychody_netto_ze_sprzedazy, self.dane.aktywa_ogolem)

            if all(v is not None for v in [x1, x2, x3, x4, x5, x6]):
                wartosc = (Decimal("1.50") * x1 +
                          Decimal("0.08") * x2 +
                          Decimal("10.00") * x3 +
                          Decimal("5.00") * x4 +
                          Decimal("0.30") * x5 +
                          Decimal("0.10") * x6)
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc <= Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Zagrożenie upadłością (Z ≤ 0)."
        elif wartosc < Decimal("1"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Słaba kondycja finansowa (0 < Z < 1)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Dobra kondycja finansowa (Z ≥ 1)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model E. Mączyńskiej",
            skrot="FD_M",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="1,50×X₁ + 0,08×X₂ + 10,00×X₃ + 5,00×X₄ + 0,30×X₅ + 0,10×X₆",
            optimum="≥ 1",
            wartosc_krytyczna="≤ 0",
            zrodlo="E. Mączyńska (1994)",
        ))

    def _oblicz_model_wierzby(self):
        """Model D. Wierzby (2000)."""
        # Z = 3,26×X₁ + 2,16×X₂ + 0,30×X₃ + 0,69×X₄
        # X₁ = (Zysk z działalności operacyjnej - Amortyzacja) / Aktywa ogółem
        # X₂ = (Zysk z działalności operacyjnej - Amortyzacja) / Sprzedaż produktów
        # X₃ = Aktywa obrotowe / Zobowiązania ogółem
        # X₄ = Kapitał obrotowy / Aktywa ogółem

        try:
            # Zysk operacyjny - amortyzacja
            wynik_op_am = self.dane.wynik_z_dzialalnosci_operacyjnej
            if wynik_op_am is not None and self.dane.amortyzacja is not None:
                wynik_op_am -= self.dane.amortyzacja

            sprzedaz = self.dane.sprzedaz_produktow or self.dane.przychody_netto_ze_sprzedazy

            x1 = self._safe_divide(wynik_op_am, self.dane.aktywa_ogolem)
            x2 = self._safe_divide(wynik_op_am, sprzedaz)
            x3 = self._safe_divide(self.dane.aktywa_obrotowe, self.dane.zobowiazania_ogolem)
            x4 = self._safe_divide(self.dane.kapital_pracujacy, self.dane.aktywa_ogolem)

            if all(v is not None for v in [x1, x2, x3, x4]):
                wartosc = (Decimal("3.26") * x1 +
                          Decimal("2.16") * x2 +
                          Decimal("0.30") * x3 +
                          Decimal("0.69") * x4)
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc <= Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Zagrożenie upadłością (Z ≤ 0)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Dobra kondycja finansowa (Z > 0)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model D. Wierzby",
            skrot="FD_W",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="3,26×X₁ + 2,16×X₂ + 0,30×X₃ + 0,69×X₄",
            optimum="> 0",
            wartosc_krytyczna="≤ 0",
            zrodlo="D. Wierzba (2000)",
        ))

    def _oblicz_model_altmana(self):
        """Model Altmana (1968) - wersja dla firm nienotowanych."""
        # Z = 1,2×X₁ + 1,4×X₂ + 3,3×X₃ + 0,6×X₄ + 1,0×X₅
        # X₁ = Kapitał pracujący / Aktywa ogółem
        # X₂ = Zysk zatrzymany / Aktywa ogółem (przybliżenie: Kapitał własny - Kapitał podstawowy)
        # X₃ = EBIT / Aktywa ogółem (przybliżenie: Wynik z działalności operacyjnej)
        # X₄ = Kapitał własny / Zobowiązania ogółem
        # X₅ = Przychody ze sprzedaży / Aktywa ogółem

        try:
            x1 = self._safe_divide(self.dane.kapital_pracujacy, self.dane.aktywa_ogolem)

            # X₂ - Zysk zatrzymany: jeśli nie mamy, użyj kapitału własnego jako przybliżenia
            zysk_zatrz = self.dane.zysk_zatrzymany or self.dane.kapital_wlasny
            x2 = self._safe_divide(zysk_zatrz, self.dane.aktywa_ogolem)

            # X₃ - EBIT: używamy wyniku z działalności operacyjnej
            x3 = self._safe_divide(self.dane.wynik_z_dzialalnosci_operacyjnej, self.dane.aktywa_ogolem)

            x4 = self._safe_divide(self.dane.kapital_wlasny, self.dane.zobowiazania_ogolem)
            x5 = self._safe_divide(self.dane.przychody_netto_ze_sprzedazy, self.dane.aktywa_ogolem)

            if all(v is not None for v in [x1, x2, x3, x4, x5]):
                wartosc = (Decimal("1.2") * x1 +
                          Decimal("1.4") * x2 +
                          Decimal("3.3") * x3 +
                          Decimal("0.6") * x4 +
                          Decimal("1.0") * x5)
            else:
                wartosc = None
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych do obliczenia modelu."
        elif wartosc <= Decimal("1.8"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Bardzo wysokie zagrożenie upadłością (Z ≤ 1,8)."
        elif wartosc < Decimal("3.0"):
            ocena = OcenaWskaznika.OSTRZEGAWCZA
            interpretacja = "Strefa szara - nieokreślone ryzyko (1,8 < Z < 3,0)."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Model wskazuje na niewielkie zagrożenie upadłością (Z ≥ 3,0)."

        self.wyniki.append(WynikWskaznika(
            nazwa="Model Altmana",
            skrot="FD_A",
            wartosc=wartosc,
            wartosc_str=self._format_ratio(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="1,2×X₁ + 1,4×X₂ + 3,3×X₃ + 0,6×X₄ + 1,0×X₅",
            optimum="≥ 3,0",
            wartosc_krytyczna="≤ 1,8",
            zrodlo="E.I. Altman (1968)",
        ))

    def _oblicz_wilcox_gambler(self):
        """Metoda wartości likwidacyjnej (Wilcox-Gambler)."""
        # WL = ŚP + 0,70×Nal + 0,50×Zap + 0,50×Inne AO + 0,50×AT - ZK - ZD

        try:
            wl = Decimal("0")

            # Środki pieniężne (100%)
            if self.dane.srodki_pieniezne is not None:
                wl += self.dane.srodki_pieniezne

            # Należności (70%)
            if self.dane.naleznosci_krotkoterminowe is not None:
                wl += Decimal("0.70") * self.dane.naleznosci_krotkoterminowe

            # Zapasy (50%)
            if self.dane.zapasy is not None:
                wl += Decimal("0.50") * self.dane.zapasy

            # Pozostałe aktywa obrotowe (50%) - przybliżenie przez RMK i inwestycje
            if self.dane.krotkoterminowe_rmk is not None:
                wl += Decimal("0.50") * self.dane.krotkoterminowe_rmk
            if self.dane.inwestycje_krotkoterminowe is not None:
                # Inwestycje krótkoterminowe bez środków pieniężnych
                ik_bez_sp = self.dane.inwestycje_krotkoterminowe
                if self.dane.srodki_pieniezne is not None:
                    ik_bez_sp -= self.dane.srodki_pieniezne
                if ik_bez_sp > 0:
                    wl += Decimal("0.50") * ik_bez_sp

            # Majątek trwały (50%)
            if self.dane.aktywa_trwale is not None:
                wl += Decimal("0.50") * self.dane.aktywa_trwale

            # Minus zobowiązania
            if self.dane.zobowiazania_krotkoterminowe is not None:
                wl -= self.dane.zobowiazania_krotkoterminowe
            if self.dane.zobowiazania_dlugoterminowe is not None:
                wl -= self.dane.zobowiazania_dlugoterminowe

            wartosc = wl
        except Exception:
            wartosc = None

        if wartosc is None:
            ocena = OcenaWskaznika.BRAK_DANYCH
            interpretacja = "Brak wystarczających danych."
        elif wartosc <= Decimal("0"):
            ocena = OcenaWskaznika.KRYTYCZNA
            interpretacja = "ALARM: Wartość likwidacyjna ujemna lub zerowa - przedsiębiorstwo niewypłacalne w ujęciu likwidacyjnym."
        else:
            ocena = OcenaWskaznika.OPTYMALNA
            interpretacja = "Wartość likwidacyjna dodatnia - przedsiębiorstwo wypłacalne w ujęciu likwidacyjnym."

        self.wyniki.append(WynikWskaznika(
            nazwa="Wartość likwidacyjna (Wilcox-Gambler)",
            skrot="WL",
            wartosc=wartosc,
            wartosc_str=self._format_currency(wartosc),
            ocena=ocena,
            interpretacja=interpretacja,
            wzor="ŚP + 0,70×Nal + 0,50×Zap + 0,50×Inne AO + 0,50×AT - ZK - ZD",
            optimum="> 0",
            wartosc_krytyczna="≤ 0",
            zrodlo="K. Prędkiewicz",
        ))


def extract_financial_data_from_sprawozdanie(sprawozdanie) -> DaneFinansowe:
    """
    Wyciąga dane finansowe ze sprawozdania do struktury DaneFinansowe.

    Mapowanie pozycji XML na dane finansowe jest zależne od typu jednostki
    i struktury sprawozdania (Mikro, Mała, Inna).
    """
    dane = DaneFinansowe()
    typ_jednostki = sprawozdanie.metadane.typ_jednostki

    # Słownik pozycji bilansu i RZiS
    bilans_dict = {}
    bilans_poprz_dict = {}
    rzis_dict = {}

    # Zbierz pozycje bilansu
    for poz in sprawozdanie.bilans_aktywa + sprawozdanie.bilans_pasywa:
        bilans_dict[poz.kod] = poz.kwota_biezaca
        if poz.kwota_poprzednia is not None:
            bilans_poprz_dict[poz.kod] = poz.kwota_poprzednia

    # Zbierz pozycje RZiS
    for poz in sprawozdanie.rzis:
        rzis_dict[poz.kod] = poz.kwota_biezaca

    # =========================================================================
    # MAPOWANIE AKTYWÓW - różne struktury dla różnych typów jednostek
    # =========================================================================
    dane.aktywa_ogolem = bilans_dict.get("Aktywa")
    dane.aktywa_ogolem_poprz = bilans_poprz_dict.get("Aktywa")
    dane.aktywa_trwale = bilans_dict.get("Aktywa_A")

    if typ_jednostki == "Mikro":
        # Jednostka Mikro - uproszczona struktura
        # Aktywa: A (trwałe), B (obrotowe), B_1 (zapasy), B_2 (krótkoterm.), C, D (RMK)
        dane.aktywa_obrotowe = bilans_dict.get("Aktywa_B")
        dane.zapasy = bilans_dict.get("Aktywa_B_1")
        dane.zapasy_poprz = bilans_poprz_dict.get("Aktywa_B_1")
        # B_2 to należności i inwestycje krótkoterminowe razem
        dane.naleznosci_krotkoterminowe = bilans_dict.get("Aktywa_B_2")
        dane.naleznosci_krotkoterminowe_poprz = bilans_poprz_dict.get("Aktywa_B_2")
        dane.krotkoterminowe_rmk = bilans_dict.get("Aktywa_D")
        # Środki pieniężne - przybliżenie (brak osobnej pozycji w Mikro)
        # Użyj części B_2 jako przybliżenia lub None
        dane.srodki_pieniezne = None  # Mikro nie wyodrębnia środków pieniężnych

    elif typ_jednostki == "Mala":
        # Jednostka Mała - pośrednia struktura
        dane.aktywa_obrotowe = bilans_dict.get("Aktywa_B")
        dane.zapasy = bilans_dict.get("Aktywa_B_I")
        dane.zapasy_poprz = bilans_poprz_dict.get("Aktywa_B_I")
        dane.naleznosci_krotkoterminowe = bilans_dict.get("Aktywa_B_II")
        dane.naleznosci_krotkoterminowe_poprz = bilans_poprz_dict.get("Aktywa_B_II")
        dane.inwestycje_krotkoterminowe = bilans_dict.get("Aktywa_B_III")
        dane.srodki_pieniezne = (
            bilans_dict.get("Aktywa_B_III_A_1") or   # środki pieniężne w kasie i na rachunkach
            bilans_dict.get("Aktywa_B_III_c") or
            bilans_dict.get("Aktywa_B_III_1_c")
        )
        dane.krotkoterminowe_rmk = bilans_dict.get("Aktywa_B_IV")

    else:  # Inna
        # Jednostka Inna - pełna struktura
        dane.aktywa_obrotowe = bilans_dict.get("Aktywa_B")
        dane.rzeczowe_aktywa_trwale = bilans_dict.get("Aktywa_A_II")
        dane.zapasy = bilans_dict.get("Aktywa_B_I")
        dane.zapasy_poprz = bilans_poprz_dict.get("Aktywa_B_I")
        dane.naleznosci_krotkoterminowe = bilans_dict.get("Aktywa_B_II")
        dane.naleznosci_krotkoterminowe_poprz = bilans_poprz_dict.get("Aktywa_B_II")
        dane.inwestycje_krotkoterminowe = bilans_dict.get("Aktywa_B_III")
        dane.srodki_pieniezne = (
            bilans_dict.get("Aktywa_B_III_1_c") or
            bilans_dict.get("Aktywa_B_III_c") or
            dane.inwestycje_krotkoterminowe  # fallback
        )
        dane.krotkoterminowe_rmk = bilans_dict.get("Aktywa_B_IV")

    # =========================================================================
    # MAPOWANIE PASYWÓW - różne struktury dla różnych typów jednostek
    # =========================================================================
    dane.pasywa_ogolem = bilans_dict.get("Pasywa")
    dane.kapital_wlasny = bilans_dict.get("Pasywa_A")

    if typ_jednostki == "Mikro":
        # Jednostka Mikro: Pasywa_B = zobowiązania ogółem (bez rozróżnienia)
        dane.zobowiazania_ogolem = bilans_dict.get("Pasywa_B")
        # Mikro nie rozróżnia zobowiązań długo/krótkoterminowych
        # Przyjmujemy wszystkie jako krótkoterminowe (konserwatywne podejście)
        dane.zobowiazania_krotkoterminowe = dane.zobowiazania_ogolem
        dane.zobowiazania_dlugoterminowe = Decimal("0") if dane.zobowiazania_ogolem else None
        dane.zobowiazania_krotkoterminowe_poprz = bilans_poprz_dict.get("Pasywa_B")

    elif typ_jednostki == "Mala":
        # Jednostka Mała
        dane.rezerwy_na_zobowiazania = bilans_dict.get("Pasywa_B_I")
        dane.zobowiazania_dlugoterminowe = bilans_dict.get("Pasywa_B_II")
        dane.zobowiazania_krotkoterminowe = bilans_dict.get("Pasywa_B_III")
        dane.zobowiazania_krotkoterminowe_poprz = bilans_poprz_dict.get("Pasywa_B_III")

        zd = dane.zobowiazania_dlugoterminowe or Decimal("0")
        zk = dane.zobowiazania_krotkoterminowe or Decimal("0")
        dane.zobowiazania_ogolem = zd + zk if (dane.zobowiazania_dlugoterminowe is not None or
                                               dane.zobowiazania_krotkoterminowe is not None) else None

    else:  # Inna
        # Jednostka Inna - pełna struktura
        dane.rezerwy_na_zobowiazania = bilans_dict.get("Pasywa_B_I")
        dane.zobowiazania_dlugoterminowe = bilans_dict.get("Pasywa_B_II")
        dane.zobowiazania_krotkoterminowe = bilans_dict.get("Pasywa_B_III")
        dane.zobowiazania_krotkoterminowe_poprz = bilans_poprz_dict.get("Pasywa_B_III")

        # Zobowiązania wobec jednostek powiązanych
        zjp_dt = bilans_dict.get("Pasywa_B_III_1_a") or Decimal("0")
        zjp_kt = bilans_dict.get("Pasywa_B_III_2_a") or Decimal("0")
        dane.zobowiazania_wobec_jedn_powiazanych = zjp_dt + zjp_kt if (
            bilans_dict.get("Pasywa_B_III_1_a") is not None or
            bilans_dict.get("Pasywa_B_III_2_a") is not None
        ) else None

        zd = dane.zobowiazania_dlugoterminowe or Decimal("0")
        zk = dane.zobowiazania_krotkoterminowe or Decimal("0")
        dane.zobowiazania_ogolem = zd + zk if (dane.zobowiazania_dlugoterminowe is not None or
                                               dane.zobowiazania_krotkoterminowe is not None) else None

    # =========================================================================
    # MAPOWANIE RZiS - różne struktury dla różnych typów jednostek
    # =========================================================================
    if typ_jednostki == "Mikro":
        # Jednostka Mikro - uproszczony RZiS
        # A = Przychody, B = Koszty, C = Pozostałe przychody, D = Pozostałe koszty
        # E = Podatek dochodowy, F = Zysk/strata netto
        dane.przychody_netto_ze_sprzedazy = rzis_dict.get("A")
        dane.koszty_dzialalnosci_operacyjnej = rzis_dict.get("B")
        # Dla Mikro wynik ze sprzedaży = A + B (B jest ujemne w XML)
        if dane.przychody_netto_ze_sprzedazy is not None and dane.koszty_dzialalnosci_operacyjnej is not None:
            dane.wynik_ze_sprzedazy = dane.przychody_netto_ze_sprzedazy + dane.koszty_dzialalnosci_operacyjnej
        dane.pozostale_przychody_operacyjne = rzis_dict.get("C")
        dane.pozostale_koszty_operacyjne = rzis_dict.get("D")
        dane.podatek_dochodowy = rzis_dict.get("E")
        dane.zysk_strata_netto = rzis_dict.get("F")
        # Wynik z działalności operacyjnej (przybliżenie)
        if all(v is not None for v in [dane.wynik_ze_sprzedazy, dane.pozostale_przychody_operacyjne, dane.pozostale_koszty_operacyjne]):
            dane.wynik_z_dzialalnosci_operacyjnej = (
                dane.wynik_ze_sprzedazy +
                dane.pozostale_przychody_operacyjne +
                dane.pozostale_koszty_operacyjne  # już ujemne
            )

    elif typ_jednostki == "Mala":
        # Jednostka Mała - RZiS 10-pozycyjny (A-J). W odróżnieniu od Jednostki
        # Innej NIE ma osobnej pozycji "zysk z działalności operacyjnej": po
        # poz. C (zysk ze sprzedaży) następują od razu D/E (pozostała działalność
        # operacyjna), F/G (działalność finansowa), a zysk brutto to poz. H.
        dane.przychody_netto_ze_sprzedazy = rzis_dict.get("A")
        dane.koszty_dzialalnosci_operacyjnej = rzis_dict.get("B")
        dane.wynik_ze_sprzedazy = rzis_dict.get("C")
        dane.pozostale_przychody_operacyjne = rzis_dict.get("D")
        dane.pozostale_koszty_operacyjne = rzis_dict.get("E")
        dane.przychody_finansowe = rzis_dict.get("F")
        dane.koszty_finansowe = rzis_dict.get("G")
        dane.zysk_strata_brutto = rzis_dict.get("H")
        dane.podatek_dochodowy = rzis_dict.get("I")
        dane.zysk_strata_netto = rzis_dict.get("J")

        # Wynik z działalności operacyjnej nie jest osobną pozycją RZiS Małej -
        # liczymy go: zysk ze sprzedaży + pozostałe przychody operacyjne
        # - pozostałe koszty operacyjne (kwoty kosztów są dodatnie w XML).
        if dane.wynik_ze_sprzedazy is not None:
            wdo = dane.wynik_ze_sprzedazy
            if dane.pozostale_przychody_operacyjne is not None:
                wdo += dane.pozostale_przychody_operacyjne
            if dane.pozostale_koszty_operacyjne is not None:
                wdo -= dane.pozostale_koszty_operacyjne
            dane.wynik_z_dzialalnosci_operacyjnej = wdo

        # Awaryjnie: zysk netto w innych wariantach (kalkulacyjny / z notą).
        if dane.zysk_strata_netto is None:
            dane.zysk_strata_netto = (
                rzis_dict.get("L") or rzis_dict.get("N") or rzis_dict.get("O")
            )

    else:  # Inna - RZiS 11-pozycyjny (A-K) z osobną poz. F "zysk z działalności
        # operacyjnej"; zysk brutto = poz. I, podatek = J, zysk netto = K.
        dane.przychody_netto_ze_sprzedazy = rzis_dict.get("A")
        dane.koszty_dzialalnosci_operacyjnej = rzis_dict.get("B")
        dane.wynik_ze_sprzedazy = rzis_dict.get("C")
        dane.pozostale_przychody_operacyjne = rzis_dict.get("D")
        dane.pozostale_koszty_operacyjne = rzis_dict.get("E")
        dane.wynik_z_dzialalnosci_operacyjnej = rzis_dict.get("F")
        dane.przychody_finansowe = rzis_dict.get("G")
        dane.koszty_finansowe = rzis_dict.get("H")
        dane.zysk_strata_brutto = rzis_dict.get("I")
        dane.podatek_dochodowy = rzis_dict.get("J")
        dane.zysk_strata_netto = rzis_dict.get("K")

        # Alternatywne mapowanie dla wariantu kalkulacyjnego lub innych wariantów
        # Zysk netto może być pod K, L (gdy jest nota podatkowa), N lub O
        if dane.zysk_strata_netto is None:
            dane.zysk_strata_netto = (
                rzis_dict.get("L") or  # z notą podatkową
                rzis_dict.get("O") or  # wariant kalkulacyjny z notą
                rzis_dict.get("N")     # wariant kalkulacyjny
            )

    # =========================================================================
    # AMORTYZACJA
    # =========================================================================
    # Amortyzacja - pozycja B.I rachunku zysków i strat w wariancie
    # porównawczym (dotyczy Jednostki Małej i Innej). W wariancie
    # kalkulacyjnym amortyzacja nie jest odrębną pozycją RZiS.
    if sprawozdanie.metadane.wariant_rzis == "porownawczy":
        dane.amortyzacja = rzis_dict.get("B_I")

    # =========================================================================
    # RACHUNEK PRZEPŁYWÓW PIENIĘŻNYCH (jeśli dostępny)
    # =========================================================================
    if sprawozdanie.rachunek_przeplywow:
        for poz in sprawozdanie.rachunek_przeplywow:
            kod = poz.kod
            if kod in ("A_III", "A.III"):
                dane.przeplywy_operacyjne = poz.kwota_biezaca
            elif kod in ("B_III", "B.III"):
                dane.przeplywy_inwestycyjne = poz.kwota_biezaca
            elif kod in ("C_III", "C.III"):
                dane.przeplywy_finansowe = poz.kwota_biezaca

    return dane
