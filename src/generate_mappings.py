#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generator mapowań pozycji finansowych na podstawie plików XSD.

Parsuje schematy XSD Ministerstwa Finansów i generuje kompletny plik mappings.py
z opisami wszystkich pozycji Bilansu, RZiS, Zestawienia zmian w kapitale
i Rachunku przepływów pieniężnych dla jednostek Mikro, Mała, Inna.
"""

from lxml import etree
from pathlib import Path
from collections import defaultdict


def parse_xsd_properly(xsd_path):
    """Parsuje XSD używając lxml i wyciąga wszystkie pozycje z dokumentacją."""
    tree = etree.parse(str(xsd_path))
    root = tree.getroot()

    ns = {'xsd': 'http://www.w3.org/2001/XMLSchema'}

    result = {
        'Bilans_Aktywa': {},
        'Bilans_Pasywa': {},
        'RZiS_Por': {},
        'RZiS_Kalk': {},
        'RZiS_Mikro': {},  # Specjalny RZiS dla jednostek Mikro
        'ZestZmianWKapitale': {},  # Zestawienie zmian w kapitale własnym
        'RachPrzeplywow_Bezp': {},  # Rachunek przepływów - metoda bezpośrednia
        'RachPrzeplywow_Posr': {},  # Rachunek przepływów - metoda pośrednia
    }

    def get_doc(elem):
        """Pobiera dokumentację elementu"""
        doc = elem.find('.//xsd:documentation', ns)
        if doc is not None and doc.text:
            return doc.text.strip()
        return None

    # Iteruj przez wszystkie complexType
    for ct in root.findall('.//xsd:complexType', ns):
        ct_name = ct.get('name') or ''

        # Dla jednostki Mikro - specjalny typ RZiSJednostkaMikro
        if ct_name == 'RZiSJednostkaMikro' or ct_name == 'RZiSJednostkaMikroWTys':
            for elem in ct.iter('{http://www.w3.org/2001/XMLSchema}element'):
                elem_name = elem.get('name')
                if elem_name and not elem_name.startswith('PozycjaUszczegolawiajaca'):
                    doc = get_doc(elem)
                    if doc:
                        result['RZiS_Mikro'][elem_name] = doc

        # Zestawienie zmian w kapitale własnym
        if 'ZestZmianWKapitale' in ct_name:
            for elem in ct.iter('{http://www.w3.org/2001/XMLSchema}element'):
                elem_name = elem.get('name')
                if elem_name and not elem_name.startswith('PozycjaUszczegolawiajaca'):
                    doc = get_doc(elem)
                    if doc:
                        result['ZestZmianWKapitale'][elem_name] = doc

        # Rachunek przepływów pieniężnych
        if 'RachPrzeplywow' in ct_name:
            for elem in ct.iter('{http://www.w3.org/2001/XMLSchema}element'):
                elem_name = elem.get('name')
                if elem_name and not elem_name.startswith('PozycjaUszczegolawiajaca'):
                    doc = get_doc(elem)
                    if doc:
                        # Sprawdź czy to metoda bezpośrednia czy pośrednia
                        parent_elem = elem.getparent()
                        is_bezp = False
                        is_posr = False
                        while parent_elem is not None:
                            parent_name = parent_elem.get('name') or ''
                            if parent_name == 'PrzeplywyBezp':
                                is_bezp = True
                                break
                            elif parent_name == 'PrzeplywyPosr':
                                is_posr = True
                                break
                            parent_elem = parent_elem.getparent()

                        if is_bezp:
                            result['RachPrzeplywow_Bezp'][elem_name] = doc
                        elif is_posr:
                            result['RachPrzeplywow_Posr'][elem_name] = doc
                        else:
                            # Dla elementów na poziomie głównym (bez rozróżnienia metody)
                            # dodaj do obu słowników
                            result['RachPrzeplywow_Bezp'][elem_name] = doc
                            result['RachPrzeplywow_Posr'][elem_name] = doc

        # Znajdź elementy RZiSPor i RZiSKalk (są to choice)
        for elem in ct.findall('.//xsd:element', ns):
            elem_name = elem.get('name')

            if elem_name == 'RZiSPor':
                # Wszystkie dzieci to pozycje RZiS porównawczego
                for child in elem.iter('{http://www.w3.org/2001/XMLSchema}element'):
                    child_name = child.get('name')
                    if child_name and not child_name.startswith('PozycjaUszczegolawiajaca'):
                        doc = get_doc(child)
                        if doc:
                            result['RZiS_Por'][child_name] = doc

            elif elem_name == 'RZiSKalk':
                for child in elem.iter('{http://www.w3.org/2001/XMLSchema}element'):
                    child_name = child.get('name')
                    if child_name and not child_name.startswith('PozycjaUszczegolawiajaca'):
                        doc = get_doc(child)
                        if doc:
                            result['RZiS_Kalk'][child_name] = doc

            elif elem_name == 'Aktywa':
                for child in elem.iter('{http://www.w3.org/2001/XMLSchema}element'):
                    child_name = child.get('name')
                    if child_name and not child_name.startswith('PozycjaUszczegolawiajaca'):
                        doc = get_doc(child)
                        if doc:
                            # Dodaj prefix Aktywa_ jeśli brak
                            if not child_name.startswith('Aktywa'):
                                child_name = 'Aktywa_' + child_name
                            result['Bilans_Aktywa'][child_name] = doc

            elif elem_name == 'Pasywa':
                for child in elem.iter('{http://www.w3.org/2001/XMLSchema}element'):
                    child_name = child.get('name')
                    if child_name and not child_name.startswith('PozycjaUszczegolawiajaca'):
                        doc = get_doc(child)
                        if doc:
                            # Dodaj prefix Pasywa_ jeśli brak
                            if not child_name.startswith('Pasywa'):
                                child_name = 'Pasywa_' + child_name
                            result['Bilans_Pasywa'][child_name] = doc

            # Bezpośrednie pozycje Aktywa/Pasywa
            elif elem_name and elem_name.startswith('Aktywa'):
                doc = get_doc(elem)
                if doc:
                    result['Bilans_Aktywa'][elem_name] = doc
            elif elem_name and elem_name.startswith('Pasywa'):
                doc = get_doc(elem)
                if doc:
                    result['Bilans_Pasywa'][elem_name] = doc

    return result


def format_opis_bilans(kod: str, opis: str) -> str:
    """
    Formatuje opis pozycji bilansu.

    Przykłady:
        Aktywa -> "Aktywa razem"
        Aktywa_A -> "A. Aktywa trwałe"
        Aktywa_A_I_1 -> "A.I.1. ..."
        Pasywa_B_IV_2_1 -> "B.IV.2.1. – długoterminowe"
    """
    parts = kod.split('_')

    # Jeśli to główna suma (Aktywa, Pasywa)
    if len(parts) == 1:
        return opis

    # Usuń prefix Aktywa/Pasywa
    hier_parts = parts[1:]

    # Buduj oznaczenie
    oznaczenie = '.'.join(hier_parts)

    # Jeśli opis zaczyna się od "–", zachowaj
    if opis.startswith('–') or opis.startswith('−') or opis.startswith('-'):
        return f"{oznaczenie}. {opis}"
    else:
        return f"{oznaczenie}. {opis}"


def format_opis_rzis(kod: str, opis: str) -> str:
    """
    Formatuje opis pozycji RZiS.

    Przykłady:
        A -> "A. Przychody..."
        A_I -> "A.I. ..."
        B_VI_1 -> "B.VI.1. emerytalne"
    """
    parts = kod.split('_')
    oznaczenie = '.'.join(parts)

    if opis.startswith('–') or opis.startswith('−') or opis.startswith('-'):
        return f"{oznaczenie}. {opis}"
    else:
        return f"{oznaczenie}. {opis}"


def sort_key(kod: str) -> tuple:
    """Klucz sortowania dla kodów pozycji."""
    parts = kod.replace('Aktywa_', '').replace('Pasywa_', '').split('_')
    result = []
    for p in parts:
        # Litery sortuj alfabetycznie, liczby numerycznie
        if p.isdigit():
            result.append((1, int(p), p))
        else:
            result.append((0, 0, p))
    return tuple(result)


def generate_mappings_py(positions_by_unit: dict) -> str:
    """Generuje kod Python dla mappings.py"""

    lines = []
    lines.append('"""')
    lines.append('Mapowania pozycji finansowych - wygenerowane z plików XSD.')
    lines.append('')
    lines.append('Ten plik zawiera słowniki mapujące kody pozycji XML na opisy czytelne dla człowieka.')
    lines.append('Wygenerowano automatycznie na podstawie schematów XSD Ministerstwa Finansów.')
    lines.append('"""')
    lines.append('')
    lines.append('from typing import Optional')
    lines.append('')

    # Dla każdego typu jednostki
    for unit_type in ['Inna', 'Mala', 'Mikro']:
        positions = positions_by_unit.get(unit_type, {})

        lines.append(f'# {"="*77}')
        lines.append(f'# JEDNOSTKA {unit_type.upper()}')
        lines.append(f'# {"="*77}')
        lines.append('')

        # Bilans
        bilans_aktywa = positions.get('Bilans_Aktywa', {})
        bilans_pasywa = positions.get('Bilans_Pasywa', {})

        if bilans_aktywa or bilans_pasywa:
            var_name = f'BILANS_{unit_type.upper()}'
            lines.append(f'{var_name} = {{')

            # Aktywa
            if bilans_aktywa:
                lines.append('    # AKTYWA')
                for kod in sorted(bilans_aktywa.keys(), key=sort_key):
                    opis = bilans_aktywa[kod]
                    formatted = format_opis_bilans(kod, opis)
                    formatted = formatted.replace('"', '\\"')
                    lines.append(f'    "{kod}": "{formatted}",')

            # Pasywa
            if bilans_pasywa:
                lines.append('')
                lines.append('    # PASYWA')
                for kod in sorted(bilans_pasywa.keys(), key=sort_key):
                    opis = bilans_pasywa[kod]
                    formatted = format_opis_bilans(kod, opis)
                    formatted = formatted.replace('"', '\\"')
                    lines.append(f'    "{kod}": "{formatted}",')

            lines.append('}')
            lines.append('')

        # RZiS Porównawczy
        rzis_por = positions.get('RZiS_Por', {})
        if rzis_por:
            var_name = f'RZIS_{unit_type.upper()}_POROWNAWCZY'
            lines.append(f'{var_name} = {{')
            for kod in sorted(rzis_por.keys(), key=sort_key):
                opis = rzis_por[kod]
                formatted = format_opis_rzis(kod, opis)
                formatted = formatted.replace('"', '\\"')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

        # RZiS Kalkulacyjny
        rzis_kalk = positions.get('RZiS_Kalk', {})
        if rzis_kalk:
            var_name = f'RZIS_{unit_type.upper()}_KALKULACYJNY'
            lines.append(f'{var_name} = {{')
            for kod in sorted(rzis_kalk.keys(), key=sort_key):
                opis = rzis_kalk[kod]
                formatted = format_opis_rzis(kod, opis)
                formatted = formatted.replace('"', '\\"')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

        # RZiS Mikro (uproszczony, tylko dla jednostek Mikro)
        rzis_mikro = positions.get('RZiS_Mikro', {})
        if rzis_mikro and unit_type == 'Mikro':
            var_name = 'RZIS_MIKRO'
            lines.append(f'{var_name} = {{')
            for kod in sorted(rzis_mikro.keys(), key=sort_key):
                opis = rzis_mikro[kod]
                formatted = format_opis_rzis(kod, opis)
                # Escape cudzysłowów i newlines
                formatted = formatted.replace('"', '\\"')
                formatted = formatted.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

        # Zestawienie zmian w kapitale własnym (tylko dla Inna - najbardziej kompletne)
        zest_zmian = positions.get('ZestZmianWKapitale', {})
        if zest_zmian and unit_type == 'Inna':
            var_name = 'ZESTAWIENIE_ZMIAN_W_KAPITALE'
            lines.append(f'{var_name} = {{')
            for kod in sorted(zest_zmian.keys(), key=sort_key):
                opis = zest_zmian[kod]
                formatted = format_opis_rzis(kod, opis)  # Używamy tego samego formatowania
                formatted = formatted.replace('"', '\\"')
                formatted = formatted.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

        # Rachunek przepływów pieniężnych - metoda bezpośrednia (tylko dla Inna)
        rach_bezp = positions.get('RachPrzeplywow_Bezp', {})
        if rach_bezp and unit_type == 'Inna':
            var_name = 'RACHUNEK_PRZEPLYWOW_BEZPOSREDNI'
            lines.append(f'{var_name} = {{')
            for kod in sorted(rach_bezp.keys(), key=sort_key):
                opis = rach_bezp[kod]
                formatted = format_opis_rzis(kod, opis)
                formatted = formatted.replace('"', '\\"')
                formatted = formatted.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

        # Rachunek przepływów pieniężnych - metoda pośrednia (tylko dla Inna)
        rach_posr = positions.get('RachPrzeplywow_Posr', {})
        if rach_posr and unit_type == 'Inna':
            var_name = 'RACHUNEK_PRZEPLYWOW_POSREDNI'
            lines.append(f'{var_name} = {{')
            for kod in sorted(rach_posr.keys(), key=sort_key):
                opis = rach_posr[kod]
                formatted = format_opis_rzis(kod, opis)
                formatted = formatted.replace('"', '\\"')
                formatted = formatted.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                lines.append(f'    "{kod}": "{formatted}",')
            lines.append('}')
            lines.append('')

    # Nota podatkowa
    lines.append('# ' + '='*77)
    lines.append('# NOTA PODATKOWA')
    lines.append('# ' + '='*77)
    lines.append('')
    lines.append('NOTA_PODATKOWA = {')
    lines.append('    "P_ID_1": "Różnica między podstawą opodatkowania podatkiem dochodowym a wynikiem finansowym (zyskiem, stratą) brutto",')
    lines.append('    "P_ID_2": "Inne zmiany podstawy opodatkowania",')
    lines.append('    "P_ID_3": "Podstawa opodatkowania podatkiem dochodowym",')
    lines.append('    "P_ID_4": "Podatek dochodowy",')
    lines.append('}')
    lines.append('')

    # Funkcje pomocnicze
    lines.append('# ' + '='*77)
    lines.append('# FUNKCJE POMOCNICZE')
    lines.append('# ' + '='*77)
    lines.append('')
    lines.append('''
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
''')

    return '\n'.join(lines)


def merge_positions(base: dict, new: dict) -> dict:
    """
    Łączy dwa słowniki pozycji, zachowując unikalne pozycje z obu.
    Nowe wartości nadpisują istniejące (nowsza wersja schematu ma priorytet).
    """
    result = dict(base)
    for key, value in new.items():
        if key not in result or result[key] == key:
            result[key] = value
    return result


def main():
    """Główna funkcja generująca mappings.py"""
    base_dir = Path(__file__).parent.parent

    # Wszystkie wersje schematów do przetworzenia (od najstarszej do najnowszej)
    versions = [
        ('1.0', 'Wersja 1.0', 'v1-0'),
        ('1.2', 'Wersja 1.2', 'v1-2'),
        ('1.3', 'Wersja 1.3', 'v1-3'),
    ]

    # Typy jednostek
    unit_types = [
        ('Inna', 'JednostkaInnaStrukturyDanychSprFin'),
        ('Mala', 'JednostkaMalaStrukturyDanychSprFin'),
        ('Mikro', 'JednostkaMikroStrukturyDanychSprFin'),
    ]

    positions_by_unit = {}

    print("="*60)
    print("Generowanie mapowań z wszystkich wersji schematów XSD")
    print("="*60)

    # Dla każdego typu jednostki
    for unit_type, filename_base in unit_types:
        print(f'\n--- Jednostka {unit_type} ---')

        # Inicjalizuj puste słowniki
        merged = {
            'Bilans_Aktywa': {},
            'Bilans_Pasywa': {},
            'RZiS_Por': {},
            'RZiS_Kalk': {},
            'RZiS_Mikro': {},
            'ZestZmianWKapitale': {},
            'RachPrzeplywow_Bezp': {},
            'RachPrzeplywow_Posr': {},
        }

        # Parsuj każdą wersję schematu
        for version_name, version_dir, version_suffix in versions:
            xsd_dir = base_dir / 'Struktury SF do obróbki' / version_dir
            filename = f'{filename_base}_{version_suffix}.xsd'
            xsd_path = xsd_dir / filename

            if xsd_path.exists():
                print(f'  Parsowanie wersji {version_name}: {filename}')
                positions = parse_xsd_properly(xsd_path)

                # Łącz z poprzednimi wersjami
                for section in ['Bilans_Aktywa', 'Bilans_Pasywa', 'RZiS_Por', 'RZiS_Kalk', 'RZiS_Mikro',
                                'ZestZmianWKapitale', 'RachPrzeplywow_Bezp', 'RachPrzeplywow_Posr']:
                    old_count = len(merged[section])
                    merged[section] = merge_positions(merged[section], positions.get(section, {}))
                    new_count = len(merged[section])
                    if new_count > old_count:
                        print(f'    {section}: +{new_count - old_count} nowych pozycji')
            else:
                print(f'  UWAGA: Brak pliku wersji {version_name}: {xsd_path}')

        # Podsumowanie dla typu jednostki
        print(f'  Suma pozycji po scaleniu:')
        print(f'    Bilans Aktywa: {len(merged["Bilans_Aktywa"])} pozycji')
        print(f'    Bilans Pasywa: {len(merged["Bilans_Pasywa"])} pozycji')
        print(f'    RZiS Por: {len(merged["RZiS_Por"])} pozycji')
        print(f'    RZiS Kalk: {len(merged["RZiS_Kalk"])} pozycji')
        if merged["RZiS_Mikro"]:
            print(f'    RZiS Mikro: {len(merged["RZiS_Mikro"])} pozycji')
        if merged["ZestZmianWKapitale"]:
            print(f'    Zest. zmian w kapitale: {len(merged["ZestZmianWKapitale"])} pozycji')
        if merged["RachPrzeplywow_Bezp"]:
            print(f'    Rach. przepływów (bezp.): {len(merged["RachPrzeplywow_Bezp"])} pozycji')
        if merged["RachPrzeplywow_Posr"]:
            print(f'    Rach. przepływów (pośr.): {len(merged["RachPrzeplywow_Posr"])} pozycji')

        positions_by_unit[unit_type] = merged

    # Generuj mappings.py
    print("\n" + "="*60)
    print("Generowanie pliku mappings.py...")
    mappings_content = generate_mappings_py(positions_by_unit)

    output_path = base_dir / 'src' / 'mappings.py'
    output_path.write_text(mappings_content, encoding='utf-8')
    print(f'Zapisano: {output_path}')
    print("="*60)


if __name__ == '__main__':
    main()
