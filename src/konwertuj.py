#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punkt wejścia dla konwersji wsadowej metodą "przeciągnij i upuść".

Wywoływany przez plik "Konwertuj SF.bat" - przeciągnięte na .bat pliki XML/XAdES
trafiają tu jako argumenty wiersza poleceń.

Działanie: patrz batch.py.
  - 1 sprawozdanie podmiotu  -> pełny XLSX (8 arkuszy)
  - 2+ sprawozdania podmiotu -> 1 XLSX z kolumnami lat
"""

import sys
from pathlib import Path

# Umożliwia uruchomienie skryptu z dowolnego katalogu roboczego
# (przeciągnięcie plików na .bat nie ustawia cwd na katalog skryptu).
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Wymuszenie UTF-8 na wyjściu konsoli (polskie znaki).
for strumien in (sys.stdout, sys.stderr):
    try:
        strumien.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from batch import run_batch  # noqa: E402  (import po modyfikacji sys.path)


def main():
    sciezki = sys.argv[1:]

    print("=" * 60)
    print("  KONWERTER SPRAWOZDAŃ FINANSOWYCH - tryb wsadowy")
    print("=" * 60)
    print()

    if not sciezki:
        print("Nie przekazano żadnych plików.")
        print()
        print("Jak używać:")
        print("  Przeciągnij pliki XML / XAdES sprawozdań finansowych")
        print("  na ikonę pliku 'Konwertuj SF.bat'.")
        print()
        print("  Sprawozdania tego samego podmiotu (ten sam NIP/KRS) zostaną")
        print("  połączone w jeden plik Excel z kolumnami kolejnych lat.")
        return

    run_batch(sciezki)

    print()
    print("=" * 60)
    print("  Zakończono.")
    print("=" * 60)


if __name__ == "__main__":
    main()
