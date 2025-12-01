#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Konwerter Sprawozdań Finansowych XML → XLSX

Uruchomienie:
    python run.py          - uruchamia interfejs graficzny
    python run.py --help   - wyświetla pomoc
    python run.py plik.xml - konwertuje pojedynczy plik
    python run.py folder/  - konwertuje wszystkie pliki w folderze
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Konwerter Sprawozdań Finansowych XML → XLSX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python run.py                           # Uruchom GUI
  python run.py sprawozdanie.xml          # Konwertuj pojedynczy plik
  python run.py folder/ -o output/        # Konwertuj folder do output/
  python run.py folder/ -r                # Rekurencyjnie przeszukuj podfoldery
        """
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Plik XML lub folder z plikami do konwersji"
    )

    parser.add_argument(
        "-o", "--output",
        help="Folder wyjściowy (domyślnie: ten sam co wejściowy)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Przeszukuj podfoldery rekurencyjnie"
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Uruchom interfejs graficzny"
    )

    args = parser.parse_args()

    # Jeśli brak argumentów lub --gui, uruchom GUI
    if args.input is None or args.gui:
        run_gui()
        return

    # Tryb wiersza poleceń
    run_cli(args)


def run_gui():
    """Uruchamia interfejs graficzny."""
    from gui import SFConverterGUI
    app = SFConverterGUI()
    app.run()


def run_cli(args):
    """Uruchamia konwersję z wiersza poleceń."""
    from parser import SFParser
    from converter import XLSXConverter

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Błąd: Ścieżka nie istnieje: {input_path}")
        sys.exit(1)

    # Zbierz pliki do przetworzenia
    files = []

    if input_path.is_file():
        files.append(input_path)
    elif input_path.is_dir():
        pattern = "**/*.xml" if args.recursive else "*.xml"
        files.extend(input_path.glob(pattern))

        pattern_xades = pattern.replace(".xml", ".xades")
        files.extend(input_path.glob(pattern_xades))

    if not files:
        print("Nie znaleziono plików XML do przetworzenia.")
        sys.exit(1)

    print(f"Znaleziono {len(files)} plików do przetworzenia.\n")

    # Konwersja
    sf_parser = SFParser()
    converter = XLSXConverter()

    success = 0
    errors = 0

    for file_path in files:
        # Określ folder wyjściowy
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = file_path.parent

        try:
            print(f"Przetwarzanie: {file_path.name}")

            sprawozdanie = sf_parser.parse(file_path)
            output_path, attachments = converter.convert(sprawozdanie, output_dir)

            print(f"  [OK] Zapisano: {output_path.name}")

            # Informacja o załącznikach
            if attachments:
                print(f"       Załączniki ({len(attachments)}):")
                for att_path in attachments:
                    print(f"       • {att_path.name}")

            success += 1

        except Exception as e:
            print(f"  [BLAD] {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Przetworzono: {success}/{len(files)} plików")
    if errors > 0:
        print(f"Błędy: {errors}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
