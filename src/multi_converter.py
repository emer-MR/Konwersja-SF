"""
Konwerter wieloletni sprawozdań finansowych.

Łączy kilka sprawozdań tego samego podmiotu (ten sam NIP/KRS) w jeden plik
XLSX, w którym każdy rok jest osobną kolumną - umożliwia analizę porównawczą
"rok obok roku".

Używany przez batch.py, gdy dla jednego podmiotu dostępne są 2 lub więcej
sprawozdania. Dla pojedynczego sprawozdania batch.py korzysta z klasycznego
XLSXConverter (converter.py).

Arkusze pliku wynikowego:
1. Podsumowanie       - dane podmiotu, lista źródłowych sprawozdań, ostrzeżenia
2. Bilans            - aktywa i pasywa, kolumny = lata
3. RZiS              - rachunek zysków i strat, kolumny = lata
4. Nota podatkowa    - jeśli dostępna choć w jednym sprawozdaniu
5. Zest. zmian w kapitale - jeśli dostępne
6. Rach. przepływów  - jeśli dostępny
7. Analiza wskaźnikowa - wskaźniki niewypłacalności w ujęciu wieloletnim
8. Dane surowe       - wszystkie pozycje z kodami, kolumny = lata
9. Dane analityczne  - format długi, wszystkie lata i typy okresów

Kolumny są kluczowane OKRESEM sprawozdawczym (okres_od, okres_do), nie samym
rokiem - dzięki temu okresy niepełne (np. otwarcie likwidacji 01.01-17.07
i 18.07-31.12) i przesunięty rok obrotowy mają własne kolumny. Dla lat
kalendarzowych etykiety kolumn są takie jak dawniej („2022”).
Sprawozdania sporządzone w tysiącach złotych są przeliczane na złote (×1000).
"""

import copy
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

from models import Sprawozdanie
import okresy


def _rok(spr: Sprawozdanie) -> int:
    """Rok sprawozdawczy = rok daty końca okresu."""
    return spr.metadane.okres_do.year


def _okres(spr: Sprawozdanie) -> tuple:
    """Klucz kolumny: (okres_od, okres_do) sprawozdania."""
    return (spr.metadane.okres_od, spr.metadane.okres_do)


def _etykieta(okres: tuple) -> str:
    return okresy.etykieta_okresu(*okres)


def _oczysc_nazwe(nazwa: str, limit: int = 80) -> str:
    """Usuwa znaki niedozwolone w nazwach plików Windows."""
    niedozwolone = '<>:"/\\|?*'
    czysta = "".join(c for c in (nazwa or "") if c not in niedozwolone).strip()
    return czysta[:limit] if czysta else "podmiot"


class MultiYearConverter:
    """Łączy wiele sprawozdań jednego podmiotu w jeden wieloletni plik XLSX."""

    HEADER_FONT = Font(bold=True)
    HEADER_FILL = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    TITLE_FONT = Font(bold=True, size=12)
    SUBTITLE_FONT = Font(bold=True, size=11)
    BIG_TITLE_FONT = Font(bold=True, size=14)
    SECTION_FONT = Font(bold=True, underline="single")
    ITALIC_GREY = Font(italic=True, color="888888")
    WARN_FONT = Font(bold=True, color="CC0000")
    MONEY_FORMAT = '#,##0.00'

    OCENA_FILL = {
        "optymalna": PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid"),
        "akceptowalna": PatternFill(start_color="E0FFE0", end_color="E0FFE0", fill_type="solid"),
        "ostrzegawcza": PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid"),
        "krytyczna": PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid"),
        "brak_danych": PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid"),
    }

    SECTION_LABELS = {
        "plynnosc": "WSKAŹNIKI PŁYNNOŚCI",
        "zadluzenie": "WSKAŹNIKI ZADŁUŻENIA",
        "rentownosc": "WSKAŹNIKI RENTOWNOŚCI",
        "aktywnosc": "WSKAŹNIKI AKTYWNOŚCI I OBROTOWOŚCI",
        "strukturalne": "WSKAŹNIKI STRUKTURALNE",
        "modele": "MODELE DYSKRYMINACYJNE (PROGNOZA BANKRUCTWA)",
    }

    def __init__(self):
        self.wb = None
        self.reports = []       # list[Sprawozdanie] - posortowane rosnąco po roku
        self.sciezki = []       # list[Path] - równolegle do self.reports
        self.ostrzezenia = []   # list[str]
        self.jednostka_label = "PLN"

    # ------------------------------------------------------------------ API

    def convert(self, pary, output_dir) -> tuple:
        """Konwertuje grupę sprawozdań jednego podmiotu do wieloletniego XLSX.

        Args:
            pary: list[tuple[Path, Sprawozdanie]] - pliki źródłowe i sprawozdania
            output_dir: katalog wyjściowy

        Returns:
            tuple (ścieżka_xlsx, lista_ścieżek_załączników)
        """
        pary_sorted = sorted(
            pary,
            key=lambda ps: (ps[1].metadane.okres_do, ps[1].metadane.okres_od,
                            ps[1].metadane.data_sporzadzenia or date.min,
                            ps[1].metadane.wersja_schematu),
        )
        self.ostrzezenia_wstepne = []
        pary_sorted = self._usun_duplikaty_okresow(pary_sorted)
        self.w_tysiacach = set()   # id() sprawozdań przeliczonych z tys. zł
        pary_sorted = [(p, self._przelicz_na_zlote(s)) for p, s in pary_sorted]
        self.reports = [s for _, s in pary_sorted]
        self.sciezki = [p for p, _ in pary_sorted]
        self.jednostka_label = self.reports[-1].metadane.jednostka_walutowa
        self.rozbieznosci, self.przeksztalcone = self._zbierz_rozbieznosci()
        self.ostrzezenia = self.ostrzezenia_wstepne + self._zbierz_ostrzezenia()

        self.wb = Workbook()

        ws_pods = self.wb.active
        ws_pods.title = "Podsumowanie"
        self._create_summary_sheet(ws_pods)

        self._create_financial_sheet(
            self.wb.create_sheet("Bilans"),
            "BILANS - UJĘCIE WIELOLETNIE",
            [("AKTYWA", lambda s: s.bilans_aktywa),
             ("PASYWA", lambda s: s.bilans_pasywa)],
        )

        self._create_financial_sheet(
            self.wb.create_sheet("RZiS"),
            "RACHUNEK ZYSKÓW I STRAT - UJĘCIE WIELOLETNIE",
            [(None, lambda s: s.rzis)],
            rzis=True,
        )

        if any(s.nota_podatkowa for s in self.reports):
            self._create_financial_sheet(
                self.wb.create_sheet("Nota podatkowa"),
                "NOTA PODATKOWA - UJĘCIE WIELOLETNIE",
                [(None, lambda s: s.nota_podatkowa)],
            )

        if any(s.zestawienie_zmian_kapital for s in self.reports):
            self._create_financial_sheet(
                self.wb.create_sheet("Zest. zmian w kapitale"),
                "ZESTAWIENIE ZMIAN W KAPITALE WŁASNYM - UJĘCIE WIELOLETNIE",
                [(None, lambda s: s.zestawienie_zmian_kapital)],
            )

        if any(s.rachunek_przeplywow for s in self.reports):
            self._create_financial_sheet(
                self.wb.create_sheet("Rach. przepływów"),
                "RACHUNEK PRZEPŁYWÓW PIENIĘŻNYCH - UJĘCIE WIELOLETNIE",
                [(None, lambda s: s.rachunek_przeplywow)],
            )

        self._create_indicators_sheet(self.wb.create_sheet("Analiza wskaźnikowa"))
        self._create_raw_sheet(self.wb.create_sheet("Dane surowe"))
        self._create_analytical_sheet(self.wb.create_sheet("Dane analityczne"))

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self._nazwa_pliku()
        self.wb.save(output_path)

        zalaczniki = self._save_attachments(output_dir)
        return output_path, zalaczniki

    # --------------------------------------------- okresy / jednostki / duplikaty

    def _usun_duplikaty_okresow(self, pary_sorted):
        """Kilka sprawozdań za TEN SAM okres (korekta, duplikat pliku): wygrywa
        sprawozdanie z najpóźniejszą datą sporządzenia (przy równych datach -
        ostatnie wg wersji schematu); pozostałe są pomijane z ostrzeżeniem.
        Sprawozdania za różne okresy tego samego roku (okresy niepełne) NIE są
        duplikatami - dostają osobne kolumny."""
        grupy = {}
        for ps in pary_sorted:
            grupy.setdefault(_okres(ps[1]), []).append(ps)
        wynik = []
        for okres, lista in grupy.items():
            if len(lista) == 1:
                wynik.append(lista[0])
                continue
            # lista posortowana rosnąco po (data sporządzenia, wersja schematu)
            zwyciezca = lista[-1]
            data_zw = zwyciezca[1].metadane.data_sporzadzenia
            rowne = sum(1 for _, sp in lista if sp.metadane.data_sporzadzenia == data_zw) > 1
            opis = ", ".join(
                f"{Path(pth).name} (sporządzono {sp.metadane.data_sporzadzenia or 'b/d'})"
                for pth, sp in lista)
            self.ostrzezenia_wstepne.append(
                f"UWAGA: {len(lista)} sprawozdania za ten sam okres {_etykieta(okres)}: {opis}. "
                f"Użyto {Path(zwyciezca[0]).name} - " + (
                    "daty sporządzenia są jednakowe (np. duplikat pliku), wybrano ostatnie wg "
                    "wersji schematu - zweryfikuj." if rowne else
                    "sporządzone najpóźniej (korekta); pozostałe pominięto w arkuszach i wskaźnikach."))
            wynik.append(zwyciezca)
        wynik.sort(key=lambda ps: okresy.klucz_sortowania(_okres(ps[1])))
        return wynik

    def _przelicz_na_zlote(self, spr):
        """Sprawozdanie w tysiącach złotych -> kopia z kwotami w złotych (×1000)."""
        if spr.metadane.jednostka_walutowa != "tys. PLN":
            return spr
        kopia = copy.deepcopy(spr)
        mnoznik = Decimal("1000")
        for poz in kopia.wszystkie_pozycje():
            for pole in ("kwota_biezaca", "kwota_poprzednia", "kwota_przeksztalcona"):
                v = getattr(poz, pole)
                if v is not None:
                    setattr(poz, pole, v * mnoznik)
        kopia.metadane.jednostka_walutowa = "PLN"
        self.w_tysiacach.add(id(kopia))
        self.ostrzezenia_wstepne.append(
            f"INFO: sprawozdanie za okres {_etykieta(_okres(spr))} sporządzono w tysiącach "
            "złotych - wszystkie jego kwoty przeliczono na złote (×1000); dokładność tych "
            "kwot wynika z zaokrąglenia źródłowego (do 10 zł).")
        return kopia

    def _okres_porownawczy(self, spr) -> tuple:
        """Okres, którego dotyczą dane porównawcze (KwotaB) sprawozdania:
        okres sprawozdania kończącego się dzień przed jego początkiem (jeśli jest
        w grupie), w przeciwnym razie poprzednie 12 miesięcy (okres pełny) albo
        okres o nieznanym początku (okres niepełny)."""
        od, do = _okres(spr)
        dzien_przed = od - timedelta(days=1)
        for s in self.reports:
            if s.metadane.okres_do == dzien_przed:
                return _okres(s)
        return okresy.okres_poprzedni(od, do)

    def _zbierz_rozbieznosci(self):
        """Porównuje dane porównawcze (KwotaB) sprawozdania za okres N z danymi
        bieżącymi sprawozdania za okres N-1 oraz zbiera przekształcone dane
        porównawcze (KwotaB1). Kolumn nie zmienia - tylko raportuje."""
        sekcje = [
            ("Bilans", lambda s: s.bilans_aktywa + s.bilans_pasywa, False),
            ("RZiS", lambda s: s.rzis, True),
            ("Zmiany w kapitale", lambda s: s.zestawienie_zmian_kapital or [], False),
            ("Przepływy", lambda s: s.rachunek_przeplywow or [], False),
        ]
        po_okresie = {_okres(s): s for s in self.reports}
        rozbieznosci, przeksztalcone = [], []
        for spr in self.reports:
            kp = self._okres_porownawczy(spr)
            prev = po_okresie.get(kp)
            tol = Decimal("10") if (id(spr) in self.w_tysiacach or
                                    (prev is not None and id(prev) in self.w_tysiacach)) else Decimal("0.01")
            if prev is not None:
                for nazwa, getter, rzis in sekcje:
                    m1, m2 = prev.metadane, spr.metadane
                    if m1.typ_jednostki != m2.typ_jednostki or (rzis and m1.wariant_rzis != m2.wariant_rzis):
                        continue  # różna struktura pozycji - kody nieporównywalne
                    biezace = {q.kod: q for q in getter(prev)}
                    for poz in getter(spr):
                        q = biezace.get(poz.kod)
                        if poz.kwota_poprzednia is None or q is None or q.kwota_biezaca is None:
                            continue
                        roznica = poz.kwota_poprzednia - q.kwota_biezaca
                        if abs(roznica) > tol:
                            rozbieznosci.append(dict(
                                sekcja=nazwa, kod=poz.kod, opis=poz.opis, okres=_etykieta(kp),
                                kwota_sf=q.kwota_biezaca, kwota_porown=poz.kwota_poprzednia,
                                roznica=roznica, zrodlo=_etykieta(_okres(spr))))
            # KwotaB1 - uznajemy za wypełnioną, gdy choć jedna wartość jest niezerowa
            # (część programów wpisuje 0,00 we wszystkich pozycjach).
            pozycje = spr.wszystkie_pozycje()
            if any(pz.kwota_przeksztalcona not in (None, 0) for pz in pozycje):
                for pz in pozycje:
                    if pz.kwota_przeksztalcona is None:
                        continue
                    if pz.kwota_przeksztalcona != (pz.kwota_poprzednia or Decimal("0")):
                        przeksztalcone.append(dict(
                            sekcja=pz.sekcja, kod=pz.kod, opis=pz.opis, okres=_etykieta(kp),
                            kwota_porown=pz.kwota_poprzednia, kwota_przeks=pz.kwota_przeksztalcona,
                            zrodlo=_etykieta(_okres(spr))))
        return rozbieznosci, przeksztalcone

    # ------------------------------------------------------- nazwa / ostrzeżenia

    def _nazwa_pliku(self) -> str:
        lata = [_rok(s) for s in self.reports]
        nazwa = _oczysc_nazwe(self.reports[-1].dane_firmy.nazwa)
        return f"{min(lata)}-{max(lata)}_analiza-wieloletnia_{nazwa}.xlsx"

    def _zbierz_ostrzezenia(self) -> list:
        o = []
        warianty = {s.metadane.wariant_rzis for s in self.reports}
        if len(warianty) > 1:
            o.append(
                "UWAGA: różne warianty RZiS (porównawczy / kalkulacyjny) - "
                "RZiS prezentowany w osobnych blokach dla każdego wariantu; "
                "wiersze bloków nie są porównywalne."
            )
        typy = {s.metadane.typ_jednostki for s in self.reports}
        if len(typy) > 1:
            o.append(
                f"UWAGA: różne typy jednostki ({', '.join(sorted(typy))}) - "
                "bilans, RZiS i pozostałe zestawienia prezentowane w osobnych blokach "
                "dla każdego typu (te same oznaczenia pozycji mają różną treść)."
            )
        if self.rozbieznosci:
            o.append(
                f"UWAGA: {len(self.rozbieznosci)} pozycji danych porównawczych (kolumna „rok "
                "poprzedni” sprawozdania) różni się od danych bieżących sprawozdania za ten okres - "
                "lista poniżej. W kolumnach okresów użyto danych ze sprawozdania ZA DANY OKRES.")
        if self.przeksztalcone:
            o.append(
                f"UWAGA: {len(self.przeksztalcone)} pozycji ma przekształcone dane porównawcze "
                "(KwotaB1) - lista poniżej; wartości kolumn NIE zostały nimi zastąpione.")
        if any(not okresy.czy_pelny_rok(*_okres(s)) for s in self.reports):
            o.append(
                "UWAGA: w grupie są sprawozdania za okres inny niż 12 miesięcy - wartości "
                "przepływowe (RZiS) nie są porównywalne z latami pełnymi; cykle rotacji (dni) "
                "w arkuszu wskaźników przeliczono do długości okresu.")

        # Kontrola rownowagi bilansowej w rozbiciu: pozycja zbiorcza kapitalu
        # wlasnego (Pasywa A) + zobowiazania (Pasywa B) powinny dac sume
        # bilansowa (Pasywa). Rozbieznosc oznacza blad danych zrodlowych XML.
        for spr in self.reports:
            pas = {p.kod: p for p in spr.bilans_pasywa}
            razem, kap, zob = pas.get("Pasywa"), pas.get("Pasywa_A"), pas.get("Pasywa_B")
            if not (razem and kap and zob):
                continue
            r, k, z = razem.kwota_biezaca, kap.kwota_biezaca, zob.kwota_biezaca
            if r is None or k is None or z is None:
                continue
            roznica = float(r) - float(k) - float(z)
            # SF w tysiącach (przeliczone ×1000) - zaokrąglenia źródłowe do 10 zł
            tolerancja = 10.0 if id(spr) in self.w_tysiacach else 0.01
            if abs(roznica) > tolerancja:
                o.append(
                    f"UWAGA: bilans sprawozdania za {_etykieta(_okres(spr))} nie rownowazy sie "
                    f"w rozbiciu - kapital wlasny + zobowiazania roznia sie od sumy "
                    f"bilansowej o {roznica:,.2f}. Mozliwy blad danych zrodlowych "
                    "(pozycja A. Kapital wlasny) - zweryfikuj z informacja dodatkowa."
                )
        return o

    # ----------------------------------------------------------- łączenie danych

    def _merge_section(self, getter, reports=None):
        """Łączy jedną sekcję (np. bilans_aktywa) ze wszystkich sprawozdań.

        Args:
            getter: funkcja Sprawozdanie -> list[PozycjaFinansowa] | None
            reports: podzbiór sprawozdań (domyślnie wszystkie) - używany, gdy
                     grupa ma różne typy jednostek / warianty RZiS (osobne bloki)

        Returns:
            tuple (lata, wiersze):
              lata    - posortowana lista lat, dla których są dane
              wiersze - list[dict] z kluczami: kod, opis, poziom, sekcja,
                        values (dict rok->Decimal), only_old (bool)
        """
        reps = reports if reports is not None else self.reports
        # Kolejność wierszy bierzemy z najnowszego sprawozdania (wzorzec).
        wzorzec = getter(reps[-1]) or []
        kody_wzorca = [p.kod for p in wzorzec]
        widziane = set(kody_wzorca)

        # Pozycje obecne tylko w starszych sprawozdaniach (dopisywane na końcu).
        kody_dodatkowe = []
        for spr in reps:
            for p in getter(spr) or []:
                if p.kod not in widziane:
                    widziane.add(p.kod)
                    kody_dodatkowe.append(p.kod)

        # Opis i poziom - z najnowszego sprawozdania, które zawiera dany kod.
        meta = {}
        for spr in reversed(reps):
            for p in getter(spr) or []:
                if p.kod not in meta:
                    meta[p.kod] = (p.opis, p.poziom, p.sekcja)

        wszystkie_kody = kody_wzorca + kody_dodatkowe
        values = {kod: {} for kod in wszystkie_kody}

        # Najpierw dane porównawcze (okres poprzedni) - niższy priorytet.
        for spr in reps:
            okres_p = self._okres_porownawczy(spr)
            for p in getter(spr) or []:
                if p.kwota_poprzednia is not None:
                    values[p.kod].setdefault(okres_p, p.kwota_poprzednia)

        # Następnie dane bieżące - zawsze nadpisują (rozbieżności: _zbierz_rozbieznosci).
        for spr in reps:
            okres_b = _okres(spr)
            for p in getter(spr) or []:
                if p.kwota_biezaca is not None:
                    values[p.kod][okres_b] = p.kwota_biezaca

        lata = sorted({ok for kod in values for ok in values[kod]}, key=okresy.klucz_sortowania)

        wiersze = []
        for kod in kody_wzorca:
            opis, poziom, sekcja = meta[kod]
            wiersze.append(dict(kod=kod, opis=opis, poziom=poziom,
                                sekcja=sekcja, values=values[kod], only_old=False))
        for kod in kody_dodatkowe:
            opis, poziom, sekcja = meta[kod]
            wiersze.append(dict(kod=kod, opis=opis, poziom=poziom,
                                sekcja=sekcja, values=values[kod], only_old=True))
        return lata, wiersze

    # --------------------------------------------------------------- arkusze

    def _create_summary_sheet(self, ws):
        firma = self.reports[-1].dane_firmy
        lata = [_rok(s) for s in self.reports]

        ws['A1'] = "ANALIZA WIELOLETNIA SPRAWOZDAŃ FINANSOWYCH"
        ws['A1'].font = self.BIG_TITLE_FONT

        row = 3
        dane_podmiotu = [
            ("Podmiot:", firma.nazwa),
            ("NIP:", firma.nip or "-"),
            ("KRS:", firma.krs or "-"),
            ("REGON:", firma.regon or "-"),
            ("Adres:", firma.adres_pelny() or "-"),
            ("Liczba sprawozdań:", str(len(self.reports))),
            ("Zakres lat:", f"{min(lata)} - {max(lata)}"),
        ]
        for etykieta, wartosc in dane_podmiotu:
            ws.cell(row=row, column=1, value=etykieta).font = self.HEADER_FONT
            ws.cell(row=row, column=2, value=wartosc)
            row += 1

        row += 1
        ws.cell(row=row, column=1, value="ŹRÓDŁOWE SPRAWOZDANIA").font = self.SUBTITLE_FONT
        row += 1
        naglowki = ["Rok", "Okres", "Typ jednostki", "Wersja schematu",
                    "Wariant RZiS", "Jednostka walut.", "Plik źródłowy"]
        for col, h in enumerate(naglowki, 1):
            c = ws.cell(row=row, column=col, value=h)
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL
        row += 1
        for spr, sciezka in zip(self.reports, self.sciezki):
            m = spr.metadane
            ws.cell(row=row, column=1, value=_rok(spr))
            ws.cell(row=row, column=2, value=f"{m.okres_od} - {m.okres_do}")
            ws.cell(row=row, column=3, value=m.typ_jednostki)
            ws.cell(row=row, column=4, value=m.wersja_schematu)
            ws.cell(row=row, column=5, value=m.wariant_rzis)
            ws.cell(row=row, column=6, value=(
                "tys. PLN -> PLN (×1000)" if id(spr) in self.w_tysiacach else m.jednostka_walutowa))
            ws.cell(row=row, column=7, value=Path(sciezka).name)
            row += 1

        if self.ostrzezenia:
            row += 1
            ws.cell(row=row, column=1, value="OSTRZEŻENIA").font = self.SUBTITLE_FONT
            row += 1
            for ostrz in self.ostrzezenia:
                c = ws.cell(row=row, column=1, value=ostrz)
                c.font = self.WARN_FONT
                ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
                row += 1

        row += 1
        nota = ws.cell(
            row=row, column=1,
            value=f"Kwoty w arkuszach prezentowane są w: {self.jednostka_label}"
                  + (" (sprawozdania w tysiącach przeliczono na złote)." if self.w_tysiacach else "."),
        )
        nota.font = Font(italic=True, color="666666")

        if self.rozbieznosci:
            row += 2
            ws.cell(row=row, column=1,
                    value="ROZBIEŻNOŚCI: DANE PORÓWNAWCZE vs SPRAWOZDANIE ZA DANY OKRES").font = self.SUBTITLE_FONT
            row += 1
            ws.cell(row=row, column=1, value=(
                "W kolumnach okresów użyto kwot ze sprawozdania za dany okres (kolumna E). "
                "Kolumna F - kwota wykazana jako dane porównawcze w sprawozdaniu za okres następny.")
            ).font = Font(italic=True, color="666666")
            row += 1
            row = self._tabela(ws, row,
                               ["Sekcja", "Kod", "Pozycja", "Okres", "Wg SF za okres (użyta)",
                                "Porównawcza (F)", "Różnica (F - E)", "Dane porównawcze z SF za"],
                               [[r["sekcja"], r["kod"], r["opis"], r["okres"], r["kwota_sf"],
                                 r["kwota_porown"], r["roznica"], r["zrodlo"]] for r in self.rozbieznosci],
                               kolumny_kwot=(5, 6, 7))

        if self.przeksztalcone:
            row += 2
            ws.cell(row=row, column=1,
                    value="DANE PRZEKSZTAŁCONE (KwotaB1) - informacyjnie").font = self.SUBTITLE_FONT
            row += 1
            ws.cell(row=row, column=1, value=(
                "Sprawozdanie zawiera przekształcone dane porównawcze. Kolumn okresów nimi NIE "
                "zastąpiono - w razie potrzeby uwzględnij je ręcznie.")).font = Font(italic=True, color="666666")
            row += 1
            row = self._tabela(ws, row,
                               ["Sekcja", "Kod", "Pozycja", "Okres porównawczy", "Porównawcza (KwotaB)",
                                "Przekształcona (KwotaB1)", "Sprawozdanie za okres"],
                               [[r["sekcja"], r["kod"], r["opis"], r["okres"], r["kwota_porown"],
                                 r["kwota_przeks"], r["zrodlo"]] for r in self.przeksztalcone],
                               kolumny_kwot=(5, 6))

        ws.column_dimensions['A'].width = 22
        ws.column_dimensions['B'].width = 30
        for col in 'CDEFG':
            ws.column_dimensions[col].width = 20
        ws.column_dimensions['G'].width = 48

    def _tabela(self, ws, row, naglowki, wiersze, kolumny_kwot=()):
        """Pomocniczo: tabela z nagłówkiem; zwraca numer następnego wiersza."""
        for col, h in enumerate(naglowki, 1):
            c = ws.cell(row=row, column=col, value=h)
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL
        row += 1
        for w in wiersze:
            for col, v in enumerate(w, 1):
                if col in kolumny_kwot and v is not None:
                    c = ws.cell(row=row, column=col, value=float(v))
                    c.number_format = self.MONEY_FORMAT
                else:
                    ws.cell(row=row, column=col, value=v)
            row += 1
        return row

    TYP_OPIS = {"Mikro": "jednostka mikro", "Mala": "jednostka mała", "Inna": "jednostka inna"}

    def _segmenty(self, rzis: bool = False) -> list:
        """Dzieli sprawozdania na segmenty o jednakowej strukturze pozycji.

        Kody pozycji (np. RZiS "F", bilans "Aktywa_B_1") znaczą co innego
        w różnych typach jednostek, a w RZiS także w różnych wariantach -
        wiersze można łączyć po kodzie tylko w obrębie jednej struktury.

        Returns:
            list[tuple[str|None, list[Sprawozdanie]]] - (nagłówek bloku lub
            None dla grupy jednorodnej, sprawozdania segmentu rosnąco po roku)
        """
        def sygn(s):
            m = s.metadane
            return (m.typ_jednostki, m.wariant_rzis) if rzis else (m.typ_jednostki,)

        segmenty = {}
        for s in self.reports:
            segmenty.setdefault(sygn(s), []).append(s)
        if len(segmenty) == 1:
            return [(None, self.reports)]
        wynik = []
        for syg, reps in segmenty.items():
            lata = [_etykieta(_okres(s)) for s in reps]
            opis = self.TYP_OPIS.get(syg[0], syg[0])
            if rzis:
                opis += f", wariant {'kalkulacyjny' if syg[1] == 'kalkulacyjny' else 'porównawczy'}"
            naglowek = (f"BLOK: {opis} - sprawozdania za okresy {', '.join(lata)} "
                        "(wiersze nieporównywalne z innymi blokami)")
            wynik.append((naglowek, reps))
        return wynik

    def _create_financial_sheet(self, ws, tytul, bloki, rzis: bool = False):
        """Tworzy arkusz finansowy z kolumnami lat.

        Args:
            ws: arkusz
            tytul: tytuł arkusza
            bloki: list[tuple[str|None, getter]] - podtytuł sekcji + funkcja getter
            rzis: True dla RZiS - segmentacja także po wariancie RZiS
        """
        firma = self.reports[-1].dane_firmy

        ws['A1'] = tytul
        ws['A1'].font = self.TITLE_FONT
        ws['A2'] = "Podmiot:"
        ws['A2'].font = self.HEADER_FONT
        ws['B2'] = firma.nazwa
        ws['A3'] = "NIP:"
        ws['A3'].font = self.HEADER_FONT
        ws['B3'] = firma.nip or "-"

        # Grupa jednorodna: jeden segment (bez nagłówka) - wynik jak dotąd.
        # Grupa mieszana: osobny blok wierszy dla każdej struktury pozycji.
        merged = []
        for naglowek, reps in self._segmenty(rzis):
            for i, (sub, getter) in enumerate(bloki):
                lata_b, wiersze = self._merge_section(getter, reps)
                merged.append((sub, lata_b, wiersze, naglowek if i == 0 else None))
        lata = sorted({ok for _, lata_b, _, _ in merged for ok in lata_b}, key=okresy.klucz_sortowania)

        if not lata:
            ws['A5'] = "(brak danych w tej sekcji)"
            return

        header_row = 5
        c = ws.cell(row=header_row, column=1, value="Pozycja")
        c.font = self.HEADER_FONT
        c.fill = self.HEADER_FILL
        for i, rok in enumerate(lata):
            c = ws.cell(row=header_row, column=2 + i,
                        value=f"{_etykieta(rok)} [{self.jednostka_label}]")
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL
            c.alignment = Alignment(horizontal='right')

        row = header_row + 1
        for sub, _lata_b, wiersze, naglowek in merged:
            if naglowek:
                c = ws.cell(row=row, column=1, value=naglowek)
                c.font = self.WARN_FONT
                c.fill = self.HEADER_FILL
                row += 1
            if sub:
                ws.cell(row=row, column=1, value=sub).font = self.SUBTITLE_FONT
                row += 1
            zwykle = [w for w in wiersze if not w['only_old']]
            stare = [w for w in wiersze if w['only_old']]
            for w in zwykle:
                row = self._write_pozycja_row(ws, row, w, lata)
            if stare:
                c = ws.cell(row=row, column=1,
                            value="Pozycje występujące tylko w starszych sprawozdaniach:")
                c.font = self.ITALIC_GREY
                row += 1
                for w in stare:
                    row = self._write_pozycja_row(ws, row, w, lata)
            row += 1

        ws.column_dimensions['A'].width = 65
        for i in range(len(lata)):
            ws.column_dimensions[get_column_letter(2 + i)].width = 18
        ws.freeze_panes = ws.cell(row=header_row + 1, column=2)

    def _write_pozycja_row(self, ws, row, wiersz, lata):
        indent = "  " * wiersz['poziom']
        cell = ws.cell(row=row, column=1, value=f"{indent}{wiersz['opis']}")
        if wiersz['poziom'] == 0:
            cell.font = Font(bold=True)
        for i, rok in enumerate(lata):
            wartosc = wiersz['values'].get(rok)
            if wartosc is not None:
                c = ws.cell(row=row, column=2 + i, value=float(wartosc))
                c.number_format = self.MONEY_FORMAT
                c.alignment = Alignment(horizontal='right')
        return row + 1

    def _create_indicators_sheet(self, ws):
        """Arkusz analizy wskaźnikowej - wskaźniki w kolumnach lat."""
        from indicators import (
            KalkulatorWskaznikow,
            extract_financial_data_from_sprawozdanie,
        )

        per_report = []  # list[tuple[rok, list[WynikWskaznika]]]
        uwagi = []       # list[tuple[rok, str]] - niespójności / ograniczenia danych
        for spr in self.reports:
            try:
                dane = extract_financial_data_from_sprawozdanie(spr)
                wyniki = KalkulatorWskaznikow(dane).oblicz_wszystkie()
                uwagi.extend((_etykieta(_okres(spr)), u) for u in dane.uwagi)
            except Exception as e:
                wyniki = []
                uwagi.append((_etykieta(_okres(spr)), f"NIESPÓJNOŚĆ: nie udało się obliczyć wskaźników ({e})."))
            per_report.append((_etykieta(_okres(spr)), wyniki))

        ws['A1'] = "ANALIZA WSKAŹNIKOWA - UJĘCIE WIELOLETNIE"
        ws['A1'].font = self.BIG_TITLE_FONT
        ws['A2'] = ("Ocena niewypłacalności: płynność, zadłużenie, rentowność, "
                    "aktywność, modele dyskryminacyjne")
        ws['A2'].font = Font(italic=True, size=9)
        ws['A3'] = "Podmiot:"
        ws['A3'].font = self.HEADER_FONT
        ws['B3'] = self.reports[-1].dane_firmy.nazwa
        ws['A4'] = ("UWAGA: wskaźniki pełnią funkcję pomocniczą. Pełna ocena "
                    "wymaga analizy dynamicznej i kontekstu branżowego.")
        ws['A4'].font = Font(italic=True, color="666666")

        # Wzorzec wierszy = najdłuższa lista wyników (zwykle z najnowszego roku).
        wzorzec = max((w for _, w in per_report), key=len, default=[])
        if not wzorzec:
            ws['A6'] = "(nie udało się obliczyć wskaźników - brak danych)"
            return

        mapy = [{w.skrot: w for w in wyniki} for _, wyniki in per_report]
        n = len(per_report)

        header_row = 6
        naglowki = (["Wskaźnik", "Skrót"]
                    + [str(rok) for rok, _ in per_report]
                    + ["Wzór", "Optimum", "Wart. krytyczna", "Źródło"])
        for col, h in enumerate(naglowki, 1):
            c = ws.cell(row=header_row, column=col, value=h)
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL
            if 3 <= col <= 2 + n:
                c.alignment = Alignment(horizontal='right')

        row = header_row + 1
        biezaca_sekcja = None
        for wz in wzorzec:
            sekcja = self._indicator_section(wz.nazwa)
            if sekcja != biezaca_sekcja:
                biezaca_sekcja = sekcja
                ws.cell(row=row, column=1,
                        value=self.SECTION_LABELS.get(sekcja, sekcja)).font = self.SECTION_FONT
                row += 1

            ws.cell(row=row, column=1, value=wz.nazwa)
            ws.cell(row=row, column=2, value=wz.skrot)
            for j in range(n):
                w = mapy[j].get(wz.skrot)
                col = 3 + j
                if w is not None:
                    c = ws.cell(row=row, column=col, value=w.wartosc_str)
                    c.alignment = Alignment(horizontal='right')
                    fill = self.OCENA_FILL.get(w.ocena.value)
                    if fill:
                        c.fill = fill
            ws.cell(row=row, column=3 + n, value=wz.wzor)
            ws.cell(row=row, column=4 + n, value=wz.optimum)
            ws.cell(row=row, column=5 + n, value=wz.wartosc_krytyczna)
            ws.cell(row=row, column=6 + n, value=wz.zrodlo)
            row += 1

        # Uwagi do danych (niespójności RZiS, ograniczenia jednostek mikro) -
        # identyczne uwagi z kilku lat scalane w jeden wiersz.
        if uwagi:
            scalone = {}
            for rok, u in uwagi:
                scalone.setdefault(u, []).append(rok)
            row += 1
            ws.cell(row=row, column=1, value="UWAGI DO DANYCH").font = self.WARN_FONT
            row += 1
            for u, lata_u in scalone.items():
                c = ws.cell(row=row, column=1,
                            value=f"[{', '.join(dict.fromkeys(lata_u))}] {u}")
                c.font = Font(bold=u.startswith("NIESPÓJNOŚĆ"), color="CC0000")
                c.alignment = Alignment(wrap_text=True, vertical="top")
                ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6 + n)
                ws.row_dimensions[row].height = 45
                row += 1

        # Legenda ocen.
        row += 1
        ws.cell(row=row, column=1, value="LEGENDA OCEN").font = self.SUBTITLE_FONT
        row += 1
        legenda = [
            ("optymalna", "wartość optymalna"),
            ("akceptowalna", "wartość akceptowalna"),
            ("ostrzegawcza", "wartość ostrzegawcza - wymaga uwagi"),
            ("krytyczna", "wartość krytyczna - sygnał zagrożenia niewypłacalnością"),
            ("brak_danych", "brak danych do obliczenia"),
        ]
        for ocena, opis in legenda:
            c = ws.cell(row=row, column=1, value=ocena.capitalize())
            c.fill = self.OCENA_FILL.get(ocena, PatternFill())
            ws.cell(row=row, column=2, value=opis)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=min(2 + n, 6))
            row += 1

        ws.column_dimensions['A'].width = 34
        ws.column_dimensions['B'].width = 9
        for j in range(n):
            ws.column_dimensions[get_column_letter(3 + j)].width = 15
        ws.column_dimensions[get_column_letter(3 + n)].width = 50
        ws.column_dimensions[get_column_letter(4 + n)].width = 22
        ws.column_dimensions[get_column_letter(5 + n)].width = 24
        ws.column_dimensions[get_column_letter(6 + n)].width = 28
        ws.freeze_panes = ws.cell(row=header_row + 1, column=3)

    @staticmethod
    def _indicator_section(nazwa: str) -> str:
        n = nazwa.lower()
        if n.startswith("model") or "wilcox" in n:
            return "modele"
        if "rentowność" in n:
            return "rentownosc"
        if ("płynnoś" in n or "gotówk" in n or "wystarczalnoś" in n
                or n.startswith("kapitał pracując")):
            return "plynnosc"
        if "zadłużeni" in n or "udziału kapitału" in n or "pokrycia zobow" in n:
            return "zadluzenie"
        if "cykl" in n or "obrot" in n or "obrót" in n:
            return "aktywnosc"
        return "strukturalne"

    def _create_raw_sheet(self, ws):
        """Arkusz danych surowych - wszystkie pozycje z kodami, kolumny = lata."""
        getters = [
            ("Bilans-Aktywa", lambda s: s.bilans_aktywa),
            ("Bilans-Pasywa", lambda s: s.bilans_pasywa),
            ("RZiS", lambda s: s.rzis),
            ("Nota", lambda s: s.nota_podatkowa),
            ("ZmianyKapitalu", lambda s: s.zestawienie_zmian_kapital),
            ("Przeplywy", lambda s: s.rachunek_przeplywow),
        ]
        wszystkie = []  # list[tuple[label, wiersz]]
        for label, getter in getters:
            segmenty = self._segmenty(rzis=(label == "RZiS"))
            for _naglowek, reps in segmenty:
                etykieta = label
                if len(segmenty) > 1:
                    m = reps[0].metadane
                    etykieta = f"{label} [{m.typ_jednostki}" + (
                        f"/{m.wariant_rzis}]" if label == "RZiS" else "]")
                _lata, wiersze = self._merge_section(getter, reps)
                for w in wiersze:
                    wszystkie.append((etykieta, w))

        lata = sorted({ok for _, w in wszystkie for ok in w['values']}, key=okresy.klucz_sortowania)
        naglowki = ["sekcja", "kod", "opis"] + [_etykieta(ok) for ok in lata]
        for col, h in enumerate(naglowki, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL

        row = 2
        for label, w in wszystkie:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=w['kod'])
            ws.cell(row=row, column=3, value=w['opis'])
            for i, rok in enumerate(lata):
                wartosc = w['values'].get(rok)
                if wartosc is not None:
                    c = ws.cell(row=row, column=4 + i, value=float(wartosc))
                    c.number_format = self.MONEY_FORMAT
            row += 1

        ws.column_dimensions['A'].width = 16
        ws.column_dimensions['B'].width = 28
        ws.column_dimensions['C'].width = 60
        for i in range(len(lata)):
            ws.column_dimensions[get_column_letter(4 + i)].width = 16
        if row > 2:
            ws.auto_filter.ref = f"A1:{get_column_letter(3 + len(lata))}{row - 1}"
        ws.freeze_panes = "D2"

    def _create_analytical_sheet(self, ws):
        """Arkusz danych analitycznych - format długi, wszystkie lata."""
        naglowki = ["firma", "nip", "krs", "typ_jednostki", "wersja",
                    "rok", "typ_okresu", "sekcja", "kod", "kod_pelny", "opis", "kwota", "okres"]
        for col, h in enumerate(naglowki, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = self.HEADER_FONT
            c.fill = self.HEADER_FILL

        row = 2
        for spr in self.reports:
            meta = spr.metadane
            firma = spr.dane_firmy
            okres_b = _okres(spr)
            okres_p = self._okres_porownawczy(spr)
            for poz in spr.wszystkie_pozycje():
                kod_pelny = poz.kod_pelny(meta.typ_jednostki, meta.wersja_schematu)
                wpisy = []
                if poz.kwota_biezaca is not None:
                    wpisy.append((okres_b, "biezacy", poz.kwota_biezaca))
                if poz.kwota_poprzednia is not None:
                    wpisy.append((okres_p, "poprzedni", poz.kwota_poprzednia))
                if poz.kwota_przeksztalcona is not None:
                    wpisy.append((okres_p, "przeksztalcony", poz.kwota_przeksztalcona))
                for okres_w, typ_okresu, kwota in wpisy:
                    rok_w = okres_w[1].year
                    ws.cell(row=row, column=1, value=firma.nazwa)
                    ws.cell(row=row, column=2, value=firma.nip)
                    ws.cell(row=row, column=3, value=firma.krs or "")
                    ws.cell(row=row, column=4, value=meta.typ_jednostki)
                    ws.cell(row=row, column=5, value=meta.wersja_schematu)
                    ws.cell(row=row, column=6, value=rok_w)
                    ws.cell(row=row, column=7, value=typ_okresu)
                    ws.cell(row=row, column=8, value=poz.sekcja)
                    ws.cell(row=row, column=9, value=poz.kod)
                    ws.cell(row=row, column=10, value=kod_pelny)
                    ws.cell(row=row, column=11, value=poz.opis)
                    c = ws.cell(row=row, column=12, value=float(kwota))
                    c.number_format = self.MONEY_FORMAT
                    ws.cell(row=row, column=13, value=_etykieta(okres_w))
                    row += 1

        szerokosci = [40, 12, 12, 12, 8, 8, 14, 12, 25, 35, 50, 15, 22]
        for i, w in enumerate(szerokosci, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        if row > 2:
            ws.auto_filter.ref = f"A1:M{row - 1}"
        ws.freeze_panes = "A2"

    # ----------------------------------------------------------- załączniki

    def _save_attachments(self, output_dir: Path) -> list:
        """Zapisuje załączniki binarne ze wszystkich sprawozdań.

        Każdy rok trafia do osobnego podkatalogu, aby uniknąć kolizji nazw.
        """
        saved = []
        if not any(s.zalaczniki for s in self.reports):
            return saved

        nazwa_clean = _oczysc_nazwe(self.reports[-1].dane_firmy.nazwa, limit=50)
        base_dir = Path(output_dir) / f"zalaczniki_{nazwa_clean}"

        for spr in self.reports:
            if not spr.zalaczniki:
                continue
            rok_dir = base_dir / _etykieta(_okres(spr))
            rok_dir.mkdir(parents=True, exist_ok=True)
            for i, zal in enumerate(spr.zalaczniki, 1):
                nazwa_pliku = zal.nazwa_pliku or f"zalacznik_{i}"
                output_path = rok_dir / nazwa_pliku
                if output_path.exists():
                    if "." in nazwa_pliku:
                        baza, ext = nazwa_pliku.rsplit(".", 1)
                        output_path = rok_dir / f"{baza}_{i}.{ext}"
                    else:
                        output_path = rok_dir / f"{nazwa_pliku}_{i}"
                try:
                    with open(output_path, "wb") as f:
                        f.write(zal.zawartosc)
                    saved.append(output_path)
                except IOError as e:
                    print(f"Błąd zapisu załącznika {nazwa_pliku}: {e}")
        return saved
