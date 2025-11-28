"""
Konwerter sprawozdań finansowych do formatu XLSX.

Generuje 5-arkuszowy plik Excel:
1. Bilans - format czytelny
2. RZiS - format czytelny
3. Nota podatkowa - jeśli dostępna
4. Dane surowe - wszystkie pozycje z kodami
5. Dane analityczne - format długi do analizy
"""

from datetime import date
from pathlib import Path
from typing import Optional

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from models import Sprawozdanie, PozycjaFinansowa


class XLSXConverter:
    """Konwerter sprawozdania do formatu XLSX."""

    # Style
    HEADER_FONT = Font(bold=True)
    HEADER_FILL = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    TITLE_FONT = Font(bold=True, size=12)
    MONEY_FORMAT = '#,##0.00'
    DATE_FORMAT = 'YYYY-MM-DD'

    def __init__(self):
        self.wb = None
        self.spr = None

    def convert(self, sprawozdanie: Sprawozdanie, output_dir: Path) -> Path:
        """Konwertuje sprawozdanie do XLSX i zapisuje do pliku.

        Args:
            sprawozdanie: Sparsowane sprawozdanie finansowe
            output_dir: Katalog wyjściowy

        Returns:
            Ścieżka do utworzonego pliku XLSX
        """
        self.spr = sprawozdanie
        self.wb = Workbook()

        # Arkusz 1: Bilans
        ws_bilans = self.wb.active
        ws_bilans.title = "Bilans"
        self._create_bilans_sheet(ws_bilans)

        # Arkusz 2: RZiS
        wariant = "w.por." if sprawozdanie.metadane.wariant_rzis == "porownawczy" else "w.kalk."
        ws_rzis = self.wb.create_sheet(f"RZiS ({wariant})")
        self._create_rzis_sheet(ws_rzis)

        # Arkusz 3: Nota podatkowa (jeśli dostępna)
        if sprawozdanie.nota_podatkowa:
            ws_nota = self.wb.create_sheet("Nota podatkowa")
            self._create_nota_sheet(ws_nota)

        # Arkusz 4: Dane surowe
        ws_surowe = self.wb.create_sheet("Dane surowe")
        self._create_raw_data_sheet(ws_surowe)

        # Arkusz 5: Dane analityczne
        ws_analityczne = self.wb.create_sheet("Dane analityczne")
        self._create_analytical_sheet(ws_analityczne)

        # Generuj nazwę pliku i zapisz
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = sprawozdanie.nazwa_pliku()
        output_path = output_dir / filename

        self.wb.save(output_path)
        return output_path

    def _create_bilans_sheet(self, ws):
        """Tworzy arkusz Bilans w formacie czytelnym."""
        meta = self.spr.metadane
        firma = self.spr.dane_firmy
        weryfikacja = self.spr.weryfikacja

        # Nagłówek
        ws['A1'] = "BILANS"
        ws['A1'].font = self.TITLE_FONT

        # Dane firmy
        ws['A2'] = "Firma:"
        ws['B2'] = firma.nazwa

        ws['A3'] = "NIP:"
        ws['B3'] = firma.nip

        if firma.krs:
            ws['A4'] = "KRS:"
            ws['B4'] = firma.krs

        # Okresy
        row = 6
        ws[f'A{row}'] = "Okres sprawozdawczy:"
        ws[f'B{row}'] = f"{meta.okres_od} - {meta.okres_do}"

        row += 1
        ws[f'A{row}'] = "Typ jednostki:"
        ws[f'B{row}'] = meta.typ_jednostki

        row += 1
        ws[f'A{row}'] = "Wersja schematu:"
        ws[f'B{row}'] = meta.wersja_schematu

        # Weryfikacja sum
        row += 2
        ws[f'A{row}'] = "Weryfikacja sum:"
        if weryfikacja:
            ws[f'B{row}'] = "Aktywa = Pasywa" if weryfikacja.aktywa_rowne_pasywom_biezacy else "BŁĄD: Aktywa ≠ Pasywa"
            if not weryfikacja.aktywa_rowne_pasywom_biezacy:
                ws[f'B{row}'].font = Font(color="FF0000", bold=True)

        # Nagłówki kolumn
        row += 2
        ws[f'A{row}'] = "Pozycja"
        ws[f'B{row}'] = f"Rok {meta.okres_do.year}"
        ws[f'C{row}'] = f"Rok {meta.okres_do.year - 1}"

        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = self.HEADER_FONT
            ws[f'{col}{row}'].fill = self.HEADER_FILL

        # AKTYWA
        row += 2
        ws[f'A{row}'] = "AKTYWA"
        ws[f'A{row}'].font = self.TITLE_FONT
        row += 1

        for poz in self.spr.bilans_aktywa:
            row = self._write_position_row(ws, row, poz)

        # PASYWA
        row += 2
        ws[f'A{row}'] = "PASYWA"
        ws[f'A{row}'].font = self.TITLE_FONT
        row += 1

        for poz in self.spr.bilans_pasywa:
            row = self._write_position_row(ws, row, poz)

        # Formatowanie kolumn
        ws.column_dimensions['A'].width = 60
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18

    def _create_rzis_sheet(self, ws):
        """Tworzy arkusz RZiS w formacie czytelnym."""
        meta = self.spr.metadane
        firma = self.spr.dane_firmy

        # Nagłówek
        wariant_nazwa = "WARIANT PORÓWNAWCZY" if meta.wariant_rzis == "porownawczy" else "WARIANT KALKULACYJNY"
        ws['A1'] = f"RACHUNEK ZYSKÓW I STRAT ({wariant_nazwa})"
        ws['A1'].font = self.TITLE_FONT

        # Dane firmy
        ws['A2'] = "Firma:"
        ws['B2'] = firma.nazwa

        ws['A3'] = "Okres:"
        ws['B3'] = f"{meta.okres_od} - {meta.okres_do}"

        # Nagłówki kolumn
        row = 5
        ws[f'A{row}'] = "Pozycja"
        ws[f'B{row}'] = f"Rok {meta.okres_do.year}"
        ws[f'C{row}'] = f"Rok {meta.okres_do.year - 1}"

        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = self.HEADER_FONT
            ws[f'{col}{row}'].fill = self.HEADER_FILL

        # Pozycje RZiS
        row += 1
        for poz in self.spr.rzis:
            row = self._write_position_row(ws, row, poz)

        # Formatowanie kolumn
        ws.column_dimensions['A'].width = 70
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18

    def _create_nota_sheet(self, ws):
        """Tworzy arkusz Nota podatkowa."""
        meta = self.spr.metadane
        firma = self.spr.dane_firmy

        # Nagłówek
        ws['A1'] = "NOTA PODATKOWA"
        ws['A1'].font = self.TITLE_FONT

        ws['A2'] = "Firma:"
        ws['B2'] = firma.nazwa

        # Nagłówki kolumn
        row = 4
        ws[f'A{row}'] = "Pozycja"
        ws[f'B{row}'] = f"Rok {meta.okres_do.year}"
        ws[f'C{row}'] = f"Rok {meta.okres_do.year - 1}"

        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = self.HEADER_FONT
            ws[f'{col}{row}'].fill = self.HEADER_FILL

        # Pozycje
        row += 1
        for poz in self.spr.nota_podatkowa:
            row = self._write_position_row(ws, row, poz)

        # Formatowanie kolumn
        ws.column_dimensions['A'].width = 80
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18

    def _create_raw_data_sheet(self, ws):
        """Tworzy arkusz z danymi surowymi (wszystkie pozycje z kodami)."""
        # Nagłówki
        headers = ["sekcja", "kod", "opis", "rok_biezacy", "rok_poprzedni"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL

        # Dane
        row = 2
        wszystkie_pozycje = self.spr.wszystkie_pozycje()

        for poz in wszystkie_pozycje:
            ws.cell(row=row, column=1, value=poz.sekcja)
            ws.cell(row=row, column=2, value=poz.kod)
            ws.cell(row=row, column=3, value=poz.opis)

            if poz.kwota_biezaca is not None:
                cell = ws.cell(row=row, column=4, value=float(poz.kwota_biezaca))
                cell.number_format = self.MONEY_FORMAT

            if poz.kwota_poprzednia is not None:
                cell = ws.cell(row=row, column=5, value=float(poz.kwota_poprzednia))
                cell.number_format = self.MONEY_FORMAT

            row += 1

        # Formatowanie kolumn
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 60
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15

        # Włącz autofiltr
        ws.auto_filter.ref = f"A1:E{row-1}"

    def _create_analytical_sheet(self, ws):
        """Tworzy arkusz z danymi analitycznymi (format długi)."""
        meta = self.spr.metadane
        firma = self.spr.dane_firmy

        # Nagłówki
        headers = [
            "firma", "nip", "krs", "typ_jednostki", "wersja",
            "okres", "sekcja", "kod", "kod_pelny", "opis", "kwota"
        ]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL

        row = 2
        wszystkie_pozycje = self.spr.wszystkie_pozycje()

        for poz in wszystkie_pozycje:
            kod_pelny = poz.kod_pelny(meta.typ_jednostki, meta.wersja_schematu)

            # Rok bieżący
            if poz.kwota_biezaca is not None:
                ws.cell(row=row, column=1, value=firma.nazwa)
                ws.cell(row=row, column=2, value=firma.nip)
                ws.cell(row=row, column=3, value=firma.krs or "")
                ws.cell(row=row, column=4, value=meta.typ_jednostki)
                ws.cell(row=row, column=5, value=meta.wersja_schematu)
                ws.cell(row=row, column=6, value=meta.okres_do)
                ws.cell(row=row, column=7, value=poz.sekcja)
                ws.cell(row=row, column=8, value=poz.kod)
                ws.cell(row=row, column=9, value=kod_pelny)
                ws.cell(row=row, column=10, value=poz.opis)
                cell = ws.cell(row=row, column=11, value=float(poz.kwota_biezaca))
                cell.number_format = self.MONEY_FORMAT
                row += 1

            # Rok poprzedni
            if poz.kwota_poprzednia is not None:
                okres_poprz = date(meta.okres_do.year - 1, 12, 31)
                ws.cell(row=row, column=1, value=firma.nazwa)
                ws.cell(row=row, column=2, value=firma.nip)
                ws.cell(row=row, column=3, value=firma.krs or "")
                ws.cell(row=row, column=4, value=meta.typ_jednostki)
                ws.cell(row=row, column=5, value=meta.wersja_schematu)
                ws.cell(row=row, column=6, value=okres_poprz)
                ws.cell(row=row, column=7, value=poz.sekcja)
                ws.cell(row=row, column=8, value=poz.kod)
                ws.cell(row=row, column=9, value=kod_pelny)
                ws.cell(row=row, column=10, value=poz.opis)
                cell = ws.cell(row=row, column=11, value=float(poz.kwota_poprzednia))
                cell.number_format = self.MONEY_FORMAT
                row += 1

        # Formatowanie kolumn
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 8
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 10
        ws.column_dimensions['H'].width = 25
        ws.column_dimensions['I'].width = 35
        ws.column_dimensions['J'].width = 50
        ws.column_dimensions['K'].width = 15

        # Włącz autofiltr
        ws.auto_filter.ref = f"A1:K{row-1}"

    def _write_position_row(self, ws, row: int, poz: PozycjaFinansowa) -> int:
        """Zapisuje wiersz pozycji finansowej.

        Args:
            ws: Arkusz
            row: Numer wiersza
            poz: Pozycja finansowa

        Returns:
            Numer następnego wiersza
        """
        # Wcięcie na podstawie poziomu
        indent = "  " * poz.poziom
        ws[f'A{row}'] = f"{indent}{poz.opis}"

        # Pogrubienie dla pozycji głównych
        if poz.poziom == 0:
            ws[f'A{row}'].font = Font(bold=True)

        # Kwoty
        if poz.kwota_biezaca is not None:
            cell = ws[f'B{row}']
            cell.value = float(poz.kwota_biezaca)
            cell.number_format = self.MONEY_FORMAT
            cell.alignment = Alignment(horizontal='right')

        if poz.kwota_poprzednia is not None:
            cell = ws[f'C{row}']
            cell.value = float(poz.kwota_poprzednia)
            cell.number_format = self.MONEY_FORMAT
            cell.alignment = Alignment(horizontal='right')

        return row + 1


def convert_file(xml_path: str, output_dir: str) -> str:
    """Funkcja pomocnicza do konwersji pojedynczego pliku.

    Args:
        xml_path: Ścieżka do pliku XML
        output_dir: Katalog wyjściowy

    Returns:
        Ścieżka do utworzonego pliku XLSX
    """
    from parser import SFParser

    parser = SFParser()
    sprawozdanie = parser.parse(Path(xml_path))

    converter = XLSXConverter()
    output_path = converter.convert(sprawozdanie, Path(output_dir))

    return str(output_path)
