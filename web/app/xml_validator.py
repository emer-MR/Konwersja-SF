"""
Walidacja XML - bezpieczeństwo i struktura sprawozdań finansowych.
"""

import re
from typing import Tuple, Optional
from lxml import etree


class XMLValidationError(Exception):
    """Wyjątek dla błędów walidacji XML."""
    pass


def validate_xml_security(content: bytes) -> Tuple[bool, Optional[str]]:
    """
    Sprawdza bezpieczeństwo pliku XML.

    Wykrywa potencjalnie niebezpieczne elementy:
    - XXE (XML External Entity) attacks
    - Billion Laughs attack
    - External DTD references
    - Podejrzane encje
    - Skrypty i osadzone pliki wykonywalne

    Args:
        content: Zawartość pliku XML jako bytes

    Returns:
        Tuple (is_safe, error_message)
    """
    try:
        content_str = content.decode('utf-8', errors='replace')
    except Exception:
        content_str = content.decode('latin-1', errors='replace')

    # Sprawdź DOCTYPE z zewnętrznymi encjami (XXE)
    if re.search(r'<!DOCTYPE[^>]*\[', content_str, re.IGNORECASE):
        return False, "Plik zawiera DOCTYPE z definicją encji (potencjalne zagrożenie XXE)"

    # Sprawdź zewnętrzne encje
    if re.search(r'<!ENTITY\s+\S+\s+SYSTEM', content_str, re.IGNORECASE):
        return False, "Plik zawiera zewnętrzne encje SYSTEM"

    if re.search(r'<!ENTITY\s+\S+\s+PUBLIC', content_str, re.IGNORECASE):
        return False, "Plik zawiera zewnętrzne encje PUBLIC"

    # Sprawdź CDATA z potencjalnie niebezpieczną zawartością
    cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
    for match in re.finditer(cdata_pattern, content_str, re.DOTALL):
        cdata_content = match.group(1).lower()
        if '<script' in cdata_content or 'javascript:' in cdata_content:
            return False, "Plik zawiera potencjalnie niebezpieczną zawartość w sekcji CDATA"

    # Sprawdź parametry encji (Billion Laughs)
    entity_count = content_str.count('<!ENTITY')
    if entity_count > 10:
        return False, f"Plik zawiera zbyt wiele encji ({entity_count}) - potencjalny atak DoS"

    # Sprawdź czy nie ma osadzonego kodu
    dangerous_patterns = [
        (r'<script', "Plik zawiera element <script>"),
        (r'javascript:', "Plik zawiera odniesienie javascript:"),
        (r'vbscript:', "Plik zawiera odniesienie vbscript:"),
        (r'data:text/html', "Plik zawiera osadzony HTML (data:text/html)"),
        (r'file://', "Plik zawiera odniesienie file://"),
    ]

    for pattern, error_msg in dangerous_patterns:
        if re.search(pattern, content_str, re.IGNORECASE):
            return False, error_msg

    return True, None


def validate_xml_structure(content: bytes) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Sprawdza czy plik XML ma strukturę sprawozdania finansowego.

    Weryfikuje:
    - Poprawność składni XML
    - Obecność elementu głównego JednostkaMikro/JednostkaMala/JednostkaInna
    - Odpowiednie namespace'y MF

    Args:
        content: Zawartość pliku XML jako bytes

    Returns:
        Tuple (is_valid, error_message, entity_type)
    """
    # Parsuj XML z zabezpieczeniami
    parser = etree.XMLParser(
        resolve_entities=False,  # Wyłącz rozwijanie encji
        no_network=True,  # Wyłącz dostęp do sieci
        dtd_validation=False,  # Wyłącz walidację DTD
        load_dtd=False,  # Nie ładuj zewnętrznych DTD
    )

    try:
        root = etree.fromstring(content, parser=parser)
    except etree.XMLSyntaxError as e:
        return False, f"Błąd składni XML: {str(e)}", None

    # Pobierz nazwę elementu głównego
    try:
        localname = etree.QName(root).localname
    except (ValueError, TypeError):
        localname = root.tag

    # Sprawdź czy to sprawozdanie finansowe
    valid_root_names = [
        "JednostkaMikro",
        "JednostkaMala",
        "JednostkaInna",
        "JednostkaMikroWZlotych",
        "JednostkaMalaWZlotych",
        "JednostkaInnaWZlotych",
        "JednostkaMikroWTysiacach",
        "JednostkaMalaWTysiacach",
        "JednostkaInnaWTysiacach",
    ]

    entity_type = None
    is_valid_root = False

    for valid_name in valid_root_names:
        if valid_name in localname:
            is_valid_root = True
            # Określ typ jednostki
            if "Mikro" in valid_name:
                entity_type = "Mikro"
            elif "Mala" in valid_name:
                entity_type = "Mala"
            else:
                entity_type = "Inna"
            break

    if not is_valid_root:
        return False, f"Nieobsługiwany typ dokumentu: '{localname}'. Obsługiwane są tylko sprawozdania finansowe (JednostkaMikro, JednostkaMala, JednostkaInna).", None

    # Sprawdź namespace
    namespace = etree.QName(root).namespace or ""
    valid_ns_patterns = [
        "mf.gov.pl/schematy/SF",
        "sprawozdaniafinansowe",
    ]

    has_valid_ns = any(pattern.lower() in namespace.lower() for pattern in valid_ns_patterns)

    # Pozwól również bez namespace dla starszych plików
    if not has_valid_ns and namespace:
        return False, f"Nierozpoznany namespace dokumentu: '{namespace}'", None

    # Sprawdź czy są wymagane sekcje
    has_naglowek = False
    has_bilans = False

    for elem in root.iter():
        try:
            elem_localname = etree.QName(elem).localname
        except (ValueError, TypeError):
            continue

        if elem_localname == "Naglowek":
            has_naglowek = True
        elif "Bilans" in elem_localname:
            has_bilans = True

        if has_naglowek and has_bilans:
            break

    if not has_naglowek:
        return False, "Brak sekcji Naglowek - nieprawidłowa struktura sprawozdania", None

    if not has_bilans:
        return False, "Brak sekcji Bilans - nieprawidłowa struktura sprawozdania", None

    return True, None, entity_type


def validate_xml(content: bytes) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Pełna walidacja pliku XML - bezpieczeństwo i struktura.

    Args:
        content: Zawartość pliku XML jako bytes

    Returns:
        Tuple (is_valid, error_message, entity_type)
    """
    # Najpierw sprawdź bezpieczeństwo
    is_safe, security_error = validate_xml_security(content)
    if not is_safe:
        return False, security_error, None

    # Następnie sprawdź strukturę
    return validate_xml_structure(content)
