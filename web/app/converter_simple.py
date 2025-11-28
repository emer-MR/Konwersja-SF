"""
Uproszczony konwerter dla wersji webowej.
Generuje tylko 2 arkusze: Bilans i RZiS.
"""

import sys
from pathlib import Path
from datetime import date
from decimal import Decimal
from typing import Optional

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

# Dodaj ścieżkę do głównego modułu src
SRC_PATH = Path(__file__).parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from parser import SFParser
from models import Sprawozdanie, PozycjaFinansowa


class SimpleXLSXConverter:
    """Uproszczony konwerter - tylko Bilans i RZiS."""

    HEADER_FONT = Font(bold=True)
    HEADER_FILL = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    TITLE_FONT = Font(bold=True, size=12)
    MONEY_FORMAT = '#,##0.00'

    def convert(self, xml_path: Path, output_path: Path) -> dict:
        """
        Konwertuje plik XML do uproszczonego XLSX.

        Args:
            xml_path: Ścieżka do pliku XML
            output_path: Ścieżka do pliku wyjściowego XLSX

        Returns:
            dict z metadanymi sprawozdania
        """
        # Parsuj XML
        parser = SFParser()
        spr = parser.parse(xml_path)

        # Utwórz workbook
        wb = Workbook()

        # Arkusz 1: Bilans
        ws_bilans = wb.active
        ws_bilans.title = "Bilans"
        self._create_bilans_sheet(ws_bilans, spr)

        # Arkusz 2: RZiS
        wariant = "w.por." if spr.metadane.wariant_rzis == "porownawczy" else "w.kalk."
        ws_rzis = wb.create_sheet(f"RZiS ({wariant})")
        self._create_rzis_sheet(ws_rzis, spr)

        # Zapisz
        wb.save(output_path)

        # Zwróć metadane
        return {
            "company_name": spr.dane_firmy.nazwa,
            "company_nip": spr.dane_firmy.nip,
            "entity_type": spr.metadane.typ_jednostki,
            "period_from": spr.metadane.okres_od,
            "period_to": spr.metadane.okres_do,
            "output_filename": output_path.name,
        }

    def _create_bilans_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz Bilans."""
        meta = spr.metadane
        firma = spr.dane_firmy
        weryfikacja = spr.weryfikacja

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

        # Weryfikacja sum
        row += 2
        ws[f'A{row}'] = "Weryfikacja sum:"
        if weryfikacja:
            if weryfikacja.aktywa_rowne_pasywom_biezacy:
                ws[f'B{row}'] = "OK (Aktywa = Pasywa)"
            else:
                ws[f'B{row}'] = "BŁĄD: Aktywa ≠ Pasywa"
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

        for poz in spr.bilans_aktywa:
            row = self._write_position_row(ws, row, poz)

        # PASYWA
        row += 2
        ws[f'A{row}'] = "PASYWA"
        ws[f'A{row}'].font = self.TITLE_FONT
        row += 1

        for poz in spr.bilans_pasywa:
            row = self._write_position_row(ws, row, poz)

        # Szerokości kolumn
        ws.column_dimensions['A'].width = 60
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18

    def _create_rzis_sheet(self, ws, spr: Sprawozdanie):
        """Tworzy arkusz RZiS."""
        meta = spr.metadane
        firma = spr.dane_firmy

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
        for poz in spr.rzis:
            row = self._write_position_row(ws, row, poz)

        # Szerokości kolumn
        ws.column_dimensions['A'].width = 70
        ws.column_dimensions['B'].width = 18
        ws.column_dimensions['C'].width = 18

    def _write_position_row(self, ws, row: int, poz: PozycjaFinansowa) -> int:
        """Zapisuje wiersz pozycji finansowej."""
        # Wcięcie
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


def convert_file(xml_path: str, output_path: str) -> dict:
    """
    Funkcja pomocnicza do konwersji.

    Args:
        xml_path: Ścieżka do pliku XML
        output_path: Ścieżka do pliku XLSX

    Returns:
        dict z metadanymi sprawozdania
    """
    converter = SimpleXLSXConverter()
    return converter.convert(Path(xml_path), Path(output_path))
