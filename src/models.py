"""
Struktury danych dla konwertera sprawozdań finansowych.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class MetadaneSprawozdania:
    """Metadane sprawozdania finansowego."""
    typ_jednostki: str          # "Mikro", "Mala", "Inna"
    wersja_schematu: str        # "1-0", "1-2", "1-3"
    okres_od: date
    okres_do: date
    data_sporzadzenia: Optional[date] = None
    wariant_rzis: str = "porownawczy"  # "porownawczy" lub "kalkulacyjny"
    jednostka_walutowa: str = "PLN"  # "PLN" lub "tys. PLN" (WTysiacach)


@dataclass
class DaneFirmy:
    """Dane identyfikacyjne firmy."""
    nazwa: str
    nip: str
    krs: Optional[str] = None
    regon: Optional[str] = None

    # Adres
    wojewodztwo: Optional[str] = None
    powiat: Optional[str] = None
    gmina: Optional[str] = None
    miejscowosc: Optional[str] = None
    ulica: Optional[str] = None
    nr_domu: Optional[str] = None
    nr_lokalu: Optional[str] = None
    kod_pocztowy: Optional[str] = None
    poczta: Optional[str] = None
    kraj: str = "PL"

    def adres_pelny(self) -> str:
        """Zwraca pełny adres jako string."""
        parts = []
        if self.ulica:
            addr = self.ulica
            if self.nr_domu:
                addr += f" {self.nr_domu}"
            if self.nr_lokalu:
                addr += f"/{self.nr_lokalu}"
            parts.append(addr)
        if self.kod_pocztowy and self.miejscowosc:
            parts.append(f"{self.kod_pocztowy} {self.miejscowosc}")
        elif self.miejscowosc:
            parts.append(self.miejscowosc)
        return ", ".join(parts) if parts else ""


@dataclass
class Zalacznik:
    """Załącznik binarny zawarty w sprawozdaniu finansowym."""
    nazwa_pliku: str              # Oryginalna nazwa pliku (np. "informacja_dodatkowa.pdf")
    zawartosc: bytes              # Zdekodowane dane binarne
    sekcja: str = ""              # Sekcja, z której pochodzi załącznik
    opis: str = ""                # Opis załącznika z XML

    def rozszerzenie(self) -> str:
        """Zwraca rozszerzenie pliku."""
        if "." in self.nazwa_pliku:
            return self.nazwa_pliku.rsplit(".", 1)[-1].lower()
        return ""

    def rozmiar_kb(self) -> float:
        """Zwraca rozmiar w KB."""
        return len(self.zawartosc) / 1024


@dataclass
class PozycjaFinansowa:
    """Pojedyncza pozycja finansowa (bilans, RZiS, nota)."""
    sekcja: str                     # "Bilans", "RZiS", "Nota"
    kod: str                        # np. "Aktywa_A_II_1"
    opis: str                       # np. "A.II.1. Środki trwałe"
    kwota_biezaca: Optional[Decimal] = None
    kwota_poprzednia: Optional[Decimal] = None
    poziom: int = 0                 # głębokość wcięcia dla hierarchii (0, 1, 2...)

    def kod_pelny(self, typ_jednostki: str, wersja: str) -> str:
        """Generuje unikalny identyfikator pozycji.

        Format: {typ_jednostki}_{wersja}_{sekcja}_{kod}
        Przykład: Mikro_1-3_Bilans_Aktywa_A
        """
        return f"{typ_jednostki}_{wersja}_{self.sekcja}_{self.kod}"


@dataclass
class WynikWeryfikacji:
    """Wynik weryfikacji sum bilansu (Aktywa = Pasywa)."""
    aktywa_razem_biezacy: Optional[Decimal] = None
    pasywa_razem_biezacy: Optional[Decimal] = None
    aktywa_razem_poprzedni: Optional[Decimal] = None
    pasywa_razem_poprzedni: Optional[Decimal] = None

    @property
    def aktywa_rowne_pasywom_biezacy(self) -> bool:
        """Sprawdza czy Aktywa = Pasywa dla roku bieżącego."""
        if self.aktywa_razem_biezacy is None or self.pasywa_razem_biezacy is None:
            return False
        return self.aktywa_razem_biezacy == self.pasywa_razem_biezacy

    @property
    def aktywa_rowne_pasywom_poprzedni(self) -> bool:
        """Sprawdza czy Aktywa = Pasywa dla roku poprzedniego."""
        if self.aktywa_razem_poprzedni is None or self.pasywa_razem_poprzedni is None:
            return False
        return self.aktywa_razem_poprzedni == self.pasywa_razem_poprzedni


@dataclass
class Sprawozdanie:
    """Pełne sprawozdanie finansowe."""
    metadane: MetadaneSprawozdania
    dane_firmy: DaneFirmy
    bilans_aktywa: list[PozycjaFinansowa] = field(default_factory=list)
    bilans_pasywa: list[PozycjaFinansowa] = field(default_factory=list)
    rzis: list[PozycjaFinansowa] = field(default_factory=list)
    nota_podatkowa: Optional[list[PozycjaFinansowa]] = None
    zestawienie_zmian_kapital: Optional[list[PozycjaFinansowa]] = None  # Zestawienie zmian w kapitale własnym
    rachunek_przeplywow: Optional[list[PozycjaFinansowa]] = None  # Rachunek przepływów pieniężnych
    wariant_przeplywow: str = "posredni"  # "bezposredni" lub "posredni"
    zalaczniki: list[Zalacznik] = field(default_factory=list)  # Załączniki binarne (PDF, DOC, itp.)
    weryfikacja: Optional[WynikWeryfikacji] = None

    def wszystkie_pozycje(self) -> list[PozycjaFinansowa]:
        """Zwraca wszystkie pozycje finansowe."""
        pozycje = self.bilans_aktywa + self.bilans_pasywa + self.rzis
        if self.nota_podatkowa:
            pozycje += self.nota_podatkowa
        if self.zestawienie_zmian_kapital:
            pozycje += self.zestawienie_zmian_kapital
        if self.rachunek_przeplywow:
            pozycje += self.rachunek_przeplywow
        return pozycje

    def nazwa_pliku(self) -> str:
        """Generuje standardową nazwę pliku wyjściowego.

        Format: {okres_od}_{okres_do}_e-sprawozdanie_{nazwa_firmy}.xlsx
        """
        nazwa = self.dane_firmy.nazwa
        # Usuń znaki niedozwolone w nazwach plików Windows
        niedozwolone = '<>:"/\\|?*'
        nazwa_clean = "".join(c for c in nazwa if c not in niedozwolone)
        # Ogranicz długość nazwy
        if len(nazwa_clean) > 100:
            nazwa_clean = nazwa_clean[:100]
        return f"{self.metadane.okres_od}_{self.metadane.okres_do}_e-sprawozdanie_{nazwa_clean}.xlsx"
