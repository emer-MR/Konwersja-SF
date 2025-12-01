"""
Parser XML sprawozdań finansowych.

Obsługuje formaty: XML, XAdES (podpisane elektronicznie).
Wspiera jednostki: Mikro, Mała, Inna.
Wspiera wersje schematów: 1-0, 1-2, 1-3.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from lxml import etree

import base64
from models import (
    MetadaneSprawozdania,
    DaneFirmy,
    PozycjaFinansowa,
    WynikWeryfikacji,
    Sprawozdanie,
    Zalacznik,
)
from mappings import get_opis, calculate_poziom


class SFParser:
    """Parser sprawozdań finansowych XML."""

    # Namespace'y dla różnych wersji schematów
    NAMESPACES = {
        # Wspólne definicje typów
        "dtsf": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/DefinicjeTypySprawozdaniaFinansowe/",
        # Podpisy cyfrowe (do ignorowania)
        "ds": "http://www.w3.org/2000/09/xmldsig#",
        "xades": "http://uri.etsi.org/01903/v1.3.2#",
        # Jednostka Mikro - wersje
        "jmi_1_2": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaMikroStruktury",
        "jmi_1_3": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaMikroStruktury",
        # Jednostka Mała - wersje
        "jma_1_2": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaMalaStruktury",
        "jma_1_3": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaMalaStruktury",
        # Jednostka Inna - wersje
        "jin_1_2": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaStruktury",
        "jin_1_3": "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaStruktury",
    }

    def __init__(self):
        self.root = None
        self.nsmap = {}

    def parse(self, file_path: Path) -> Sprawozdanie:
        """Parsuje plik XML/XAdES sprawozdania finansowego.

        Args:
            file_path: Ścieżka do pliku XML

        Returns:
            Sprawozdanie: Sparsowane sprawozdanie finansowe

        Raises:
            ValueError: Jeśli plik nie jest prawidłowym sprawozdaniem finansowym
            FileNotFoundError: Jeśli plik nie istnieje
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

        # Parsuj XML
        tree = etree.parse(str(file_path))
        self.root = tree.getroot()

        # Buduj mapę namespace'ów z dokumentu
        self._build_nsmap()

        # Wykryj typ jednostki i wersję schematu
        typ_jednostki = self._detect_entity_type()
        wersja_schematu = self._detect_schema_version()

        # Parsuj metadane
        metadane = self._parse_header(typ_jednostki, wersja_schematu)

        # Parsuj dane firmy
        dane_firmy = self._parse_company_info(typ_jednostki)

        # Parsuj bilans
        bilans_aktywa, bilans_pasywa = self._parse_bilans(typ_jednostki, metadane.wariant_rzis)

        # Parsuj RZiS
        rzis = self._parse_rzis(typ_jednostki, metadane.wariant_rzis)

        # Parsuj notę podatkową (jeśli istnieje)
        nota_podatkowa = self._parse_nota_podatkowa(typ_jednostki)

        # Parsuj zestawienie zmian w kapitale własnym (jeśli istnieje)
        zestawienie_zmian_kapital = self._parse_zestawienie_zmian_kapital(typ_jednostki)

        # Parsuj rachunek przepływów pieniężnych (jeśli istnieje)
        rachunek_przeplywow, wariant_przeplywow = self._parse_rachunek_przeplywow(typ_jednostki)

        # Parsuj załączniki binarne (jeśli istnieją)
        zalaczniki = self._parse_zalaczniki()

        # Weryfikacja sum
        weryfikacja = self._verify_sums(bilans_aktywa, bilans_pasywa)

        return Sprawozdanie(
            metadane=metadane,
            dane_firmy=dane_firmy,
            bilans_aktywa=bilans_aktywa,
            bilans_pasywa=bilans_pasywa,
            rzis=rzis,
            nota_podatkowa=nota_podatkowa,
            zestawienie_zmian_kapital=zestawienie_zmian_kapital,
            rachunek_przeplywow=rachunek_przeplywow,
            wariant_przeplywow=wariant_przeplywow,
            zalaczniki=zalaczniki,
            weryfikacja=weryfikacja,
        )

    def _build_nsmap(self):
        """Buduje mapę namespace'ów z dokumentu."""
        self.nsmap = dict(self.root.nsmap)
        # Usuń domyślny namespace (None key) i dodaj jako 'default'
        if None in self.nsmap:
            self.nsmap["default"] = self.nsmap.pop(None)
        # Dodaj standardowe namespace'y
        self.nsmap.update(self.NAMESPACES)

    def _detect_entity_type(self) -> str:
        """Wykrywa typ jednostki z nazwy root elementu.

        Returns:
            "Mikro", "Mala" lub "Inna"
        """
        tag = etree.QName(self.root).localname
        if "Mikro" in tag:
            return "Mikro"
        elif "Mala" in tag:
            return "Mala"
        else:
            return "Inna"

    def _detect_schema_version(self) -> str:
        """Wykrywa wersję schematu z atrybutu wersjaSchemy lub namespace.

        Returns:
            Wersja schematu, np. "1-2" lub "1-3"
        """
        # Szukaj atrybutu wersjaSchemy w KodSprawozdania
        kod_elem = self._find_element(".//KodSprawozdania")
        if kod_elem is not None:
            wersja = kod_elem.get("wersjaSchemy")
            if wersja:
                return wersja

        # Fallback: sprawdź namespace
        ns = self.root.nsmap.get(None, "")
        if "2025/01/01" in ns:
            return "1-3"
        elif "2018/07/09" in ns:
            return "1-2"
        else:
            return "1-0"

    def _safe_localname(self, elem) -> Optional[str]:
        """Bezpiecznie pobiera localname elementu.

        Args:
            elem: Element XML

        Returns:
            localname lub None jeśli nie można pobrać
        """
        if not isinstance(elem.tag, str):
            return None
        try:
            return etree.QName(elem).localname
        except (ValueError, TypeError):
            return None

    def _find_element(self, xpath: str, parent=None):
        """Znajduje element używając xpath z obsługą namespace'ów.

        Args:
            xpath: Ścieżka XPath (bez prefiksów namespace)
            parent: Element rodzica (domyślnie root)

        Returns:
            Element lub None
        """
        if parent is None:
            parent = self.root

        # Próbuj z różnymi namespace'ami
        for ns_prefix in [None, "default", "ns1", "ns2", "dtsf"]:
            try:
                if ns_prefix and ns_prefix in self.nsmap:
                    ns_xpath = xpath.replace("//", f"//{ns_prefix}:").replace("/", f"/{ns_prefix}:")
                    ns_xpath = ns_xpath.replace(f"{ns_prefix}:/", "/")
                    result = parent.find(ns_xpath, self.nsmap)
                else:
                    result = parent.find(xpath)
                if result is not None:
                    return result
            except (etree.XPathEvalError, KeyError):
                continue

        # Fallback: szukaj po localname
        tag_name = xpath.split("/")[-1]
        for elem in parent.iter():
            localname = self._safe_localname(elem)
            if localname and localname == tag_name:
                return elem
        return None

    def _find_elements(self, xpath: str, parent=None) -> list:
        """Znajduje wszystkie elementy pasujące do xpath."""
        if parent is None:
            parent = self.root

        results = []
        tag_name = xpath.split("/")[-1].replace("*", "")

        for elem in parent.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue
            if tag_name == "" or localname == tag_name or localname.startswith(tag_name):
                results.append(elem)

        return results

    def _get_text(self, xpath: str, parent=None) -> Optional[str]:
        """Pobiera tekst z elementu."""
        elem = self._find_element(xpath, parent)
        if elem is not None and elem.text:
            return elem.text.strip()
        return None

    def _parse_date(self, text: str) -> Optional[date]:
        """Parsuje datę z formatu YYYY-MM-DD."""
        if not text:
            return None
        try:
            parts = text.split("-")
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return None

    def _parse_decimal(self, text: str) -> Optional[Decimal]:
        """Parsuje kwotę do Decimal."""
        if not text:
            return None
        try:
            # Zamień przecinek na kropkę
            text = text.replace(",", ".").strip()
            return Decimal(text)
        except InvalidOperation:
            return None

    def _parse_header(self, typ_jednostki: str, wersja_schematu: str) -> MetadaneSprawozdania:
        """Parsuje nagłówek sprawozdania."""
        # Znajdź sekcję Naglowek
        naglowek = self._find_element("Naglowek")

        okres_od = None
        okres_do = None
        data_sporzadzenia = None

        if naglowek is not None:
            for elem in naglowek.iter():
                localname = self._safe_localname(elem)
                if not localname:
                    continue
                if localname == "OkresOd":
                    okres_od = self._parse_date(elem.text)
                elif localname == "OkresDo":
                    okres_do = self._parse_date(elem.text)
                elif localname == "DataSporzadzenia":
                    data_sporzadzenia = self._parse_date(elem.text)

        # Wykryj wariant RZiS
        wariant_rzis = self._detect_rzis_variant()

        # Wykryj jednostkę walutową (PLN lub tys. PLN)
        jednostka_walutowa = self._detect_currency_unit()

        return MetadaneSprawozdania(
            typ_jednostki=typ_jednostki,
            wersja_schematu=wersja_schematu,
            okres_od=okres_od or date.today(),
            okres_do=okres_do or date.today(),
            data_sporzadzenia=data_sporzadzenia,
            wariant_rzis=wariant_rzis,
            jednostka_walutowa=jednostka_walutowa,
        )

    def _detect_rzis_variant(self) -> str:
        """Wykrywa wariant RZiS (porównawczy/kalkulacyjny)."""
        # Szukaj elementów RZiS
        for elem in self.root.iter():
            # Pomijaj elementy nie będące tagami (komentarze, PI, itp.)
            if not isinstance(elem.tag, str):
                continue
            try:
                localname = etree.QName(elem).localname
                if "RZiSKalk" in localname or "Kalkulacyjny" in localname:
                    return "kalkulacyjny"
                elif "RZiSPor" in localname or "Porownawczy" in localname:
                    return "porownawczy"
            except (ValueError, TypeError):
                continue

        # Domyślnie porównawczy
        return "porownawczy"

    def _detect_currency_unit(self) -> str:
        """Wykrywa jednostkę walutową (PLN lub tys. PLN).

        Sprawozdania w wariancie WTysiacach mają:
        - Element główny zawierający "WTys" w nazwie
        - Lub namespace zawierający "WTysiacach"

        Returns:
            "PLN" lub "tys. PLN"
        """
        # Sprawdź nazwę elementu głównego
        tag = etree.QName(self.root).localname
        if "WTys" in tag:
            return "tys. PLN"

        # Sprawdź namespace elementu głównego
        ns = etree.QName(self.root).namespace or ""
        if "WTysiacach" in ns or "WTys" in ns:
            return "tys. PLN"

        # Domyślnie PLN (wariant WZlotych)
        return "PLN"

    def _parse_company_info(self, typ_jednostki: str) -> DaneFirmy:
        """Parsuje dane firmy."""
        nazwa = ""
        nip = ""
        krs = None
        regon = None

        # Adresy
        wojewodztwo = None
        powiat = None
        gmina = None
        miejscowosc = None
        ulica = None
        nr_domu = None
        nr_lokalu = None
        kod_pocztowy = None
        poczta = None
        kraj = "PL"

        # Szukaj sekcji z danymi firmy
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue

            # Nazwa firmy
            if localname == "NazwaFirmy" and elem.text:
                nazwa = elem.text.strip()

            # NIP i KRS - mogą być w P_1C, P_1D lub P_1E w zależności od wersji
            elif localname in ("P_1C", "P_1D", "P_1E") and elem.text:
                text = elem.text.strip()
                if len(text) == 10 and text.isdigit():
                    # KRS zaczyna się od 000
                    if text.startswith("000"):
                        krs = text
                    # NIP - pozostałe 10-cyfrowe numery
                    elif not nip:  # ustaw tylko jeśli jeszcze nie mamy NIP
                        nip = text

            # REGON
            elif localname == "REGON" and elem.text:
                regon = elem.text.strip()

            # Adres
            elif localname == "Wojewodztwo" and elem.text:
                wojewodztwo = elem.text.strip()
            elif localname == "Powiat" and elem.text:
                powiat = elem.text.strip()
            elif localname == "Gmina" and elem.text:
                gmina = elem.text.strip()
            elif localname == "Miejscowosc" and elem.text:
                miejscowosc = elem.text.strip()
            elif localname == "Ulica" and elem.text:
                ulica = elem.text.strip()
            elif localname == "NrDomu" and elem.text:
                nr_domu = elem.text.strip()
            elif localname == "NrLokalu" and elem.text:
                nr_lokalu = elem.text.strip()
            elif localname == "KodPocztowy" and elem.text:
                kod_pocztowy = elem.text.strip()
            elif localname == "Poczta" and elem.text:
                poczta = elem.text.strip()
            elif localname == "KodKraju" and elem.text:
                kraj = elem.text.strip()

        return DaneFirmy(
            nazwa=nazwa,
            nip=nip,
            krs=krs,
            regon=regon,
            wojewodztwo=wojewodztwo,
            powiat=powiat,
            gmina=gmina,
            miejscowosc=miejscowosc,
            ulica=ulica,
            nr_domu=nr_domu,
            nr_lokalu=nr_lokalu,
            kod_pocztowy=kod_pocztowy,
            poczta=poczta,
            kraj=kraj,
        )

    def _parse_bilans(self, typ_jednostki: str, wariant_rzis: str) -> tuple:
        """Parsuje bilans - zwraca (aktywa, pasywa)."""
        aktywa = []
        pasywa = []

        # Znajdź sekcję Bilans
        bilans_elem = None
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if localname and "Bilans" in localname and "JednostkaOp" not in localname:
                bilans_elem = elem
                break

        if bilans_elem is None:
            return aktywa, pasywa

        # Parsuj Aktywa i Pasywa
        for child in bilans_elem:
            localname = self._safe_localname(child)
            if not localname:
                continue

            if localname == "Aktywa" or localname.startswith("Aktywa"):
                aktywa = self._extract_positions_recursive(
                    child, "Bilans", typ_jednostki, wariant_rzis, prefix="Aktywa"
                )
            elif localname == "Pasywa" or localname.startswith("Pasywa"):
                pasywa = self._extract_positions_recursive(
                    child, "Bilans", typ_jednostki, wariant_rzis, prefix="Pasywa"
                )

        return aktywa, pasywa

    def _parse_rzis(self, typ_jednostki: str, wariant_rzis: str) -> list:
        """Parsuje Rachunek Zysków i Strat."""
        pozycje = []

        # Znajdź sekcję RZiS - różne struktury dla różnych typów jednostek:
        # - JednostkaInna/Mala: <RZiS><RZiSPor>...</RZiSPor></RZiS> lub <RZiS><RZiSKalk>...</RZiSKalk></RZiS>
        # - JednostkaMikro: <RZiSJednostkaMikro><A>...</A><B>...</B>...</RZiSJednostkaMikro>
        rzis_elem = None
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue

            # Dla jednostki Mikro - specjalny element RZiSJednostkaMikro
            if localname == "RZiSJednostkaMikro":
                rzis_elem = elem
                break

            # Szukaj elementu RZiSPor lub RZiSKalk (w zależności od wariantu)
            if localname == "RZiSPor" or localname == "RZiSKalk":
                rzis_elem = elem
                break
            # Alternatywnie: szukaj głównego kontenera RZiS jeśli brak RZiSPor/RZiSKalk
            if localname == "RZiS" and rzis_elem is None:
                # Sprawdź czy ma dzieci z pozycjami (A, B, C, itd.)
                for child in elem:
                    child_name = self._safe_localname(child)
                    if child_name in ("RZiSPor", "RZiSKalk"):
                        rzis_elem = child
                        break
                    # Dla jednostek Mikro może być uproszczona struktura
                    if child_name and len(child_name) <= 2 and child_name.isalpha():
                        rzis_elem = elem
                        break

        if rzis_elem is None:
            return pozycje

        # Parsuj rekurencyjnie
        pozycje = self._extract_positions_recursive(
            rzis_elem, "RZiS", typ_jednostki, wariant_rzis
        )

        return pozycje

    def _parse_nota_podatkowa(self, typ_jednostki: str) -> Optional[list]:
        """Parsuje notę podatkową (Dodatkowe Informacje i Objaśnienia)."""
        pozycje = []

        # Szukaj sekcji z notą podatkową
        nota_elem = None
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if localname and ("DodatkoweInformacje" in localname or "InformacjeDodatkowe" in localname):
                nota_elem = elem
                break

        if nota_elem is None:
            return None

        # Szukaj pozycji P_ID_*
        for elem in nota_elem.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue
            if localname.startswith("P_ID_"):
                kwota_a = None
                kwota_b = None

                for child in elem.iter():
                    child_name = self._safe_localname(child)
                    if not child_name:
                        continue
                    if child_name == "KwotaA" and child.text:
                        kwota_a = self._parse_decimal(child.text)
                    elif child_name == "KwotaB" and child.text:
                        kwota_b = self._parse_decimal(child.text)

                if kwota_a is not None or kwota_b is not None:
                    opis = get_opis(localname, typ_jednostki, "Nota")
                    pozycje.append(PozycjaFinansowa(
                        sekcja="Nota",
                        kod=localname,
                        opis=opis,
                        kwota_biezaca=kwota_a,
                        kwota_poprzednia=kwota_b,
                        poziom=0,
                    ))

        return pozycje if pozycje else None

    def _parse_zestawienie_zmian_kapital(self, typ_jednostki: str) -> Optional[list]:
        """Parsuje Zestawienie zmian w kapitale własnym."""
        pozycje = []

        # Szukaj sekcji Zestawienie zmian w kapitale
        zest_elem = None
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue
            if "ZestZmianWKapitale" in localname:
                zest_elem = elem
                break

        if zest_elem is None:
            return None

        # Parsuj rekurencyjnie
        pozycje = self._extract_positions_recursive(
            zest_elem, "ZestZmianWKapitale", typ_jednostki, ""
        )

        return pozycje if pozycje else None

    def _parse_rachunek_przeplywow(self, typ_jednostki: str) -> tuple:
        """Parsuje Rachunek przepływów pieniężnych.

        Returns:
            Tuple (lista pozycji, wariant: "bezposredni" lub "posredni")
        """
        pozycje = []
        wariant = "posredni"

        # Szukaj sekcji Rachunek przepływów
        rach_elem = None
        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue

            # Sprawdź wariant
            if localname == "PrzeplywyBezp":
                rach_elem = elem
                wariant = "bezposredni"
                break
            elif localname == "PrzeplywyPosr":
                rach_elem = elem
                wariant = "posredni"
                break
            elif "RachPrzeplywow" in localname:
                # Główny kontener - szukaj w dzieciach
                for child in elem:
                    child_name = self._safe_localname(child)
                    if child_name == "PrzeplywyBezp":
                        rach_elem = child
                        wariant = "bezposredni"
                        break
                    elif child_name == "PrzeplywyPosr":
                        rach_elem = child
                        wariant = "posredni"
                        break
                if rach_elem is not None:
                    break

        if rach_elem is None:
            return None, wariant

        # Parsuj rekurencyjnie
        pozycje = self._extract_positions_recursive(
            rach_elem, "RachPrzeplywow", typ_jednostki, ""
        )

        return (pozycje if pozycje else None), wariant

    def _extract_positions_recursive(
        self,
        element,
        sekcja: str,
        typ_jednostki: str,
        wariant_rzis: str,
        prefix: str = "",
        level: int = 0
    ) -> list:
        """Rekurencyjnie wyciąga pozycje finansowe z hierarchii XML.

        Args:
            element: Element XML do przetworzenia
            sekcja: Nazwa sekcji (Bilans, RZiS, Nota)
            typ_jednostki: Typ jednostki
            wariant_rzis: Wariant RZiS
            prefix: Prefix kodu (np. "Aktywa")
            level: Poziom zagnieżdżenia

        Returns:
            Lista pozycji finansowych
        """
        pozycje = []
        localname = self._safe_localname(element)

        # Pomijaj elementy bez localname
        if not localname:
            return pozycje

        # Pomijaj podpisy i załączniki
        if localname in ("Signature", "ds:Signature", "Zalacznik", "TrescZalacznika"):
            return pozycje
        if "Signature" in localname or "Zalacznik" in localname:
            return pozycje
        if "PozycjaUszczegolawiajaca" in localname:
            return pozycje

        # Wyciągnij kwoty z bieżącego elementu
        kwota_a = None
        kwota_b = None

        for child in element:
            child_name = self._safe_localname(child)
            if not child_name:
                continue
            if child_name == "KwotaA" and child.text:
                kwota_a = self._parse_decimal(child.text)
            elif child_name == "KwotaB" and child.text:
                kwota_b = self._parse_decimal(child.text)

        # Określ kod pozycji
        if prefix and not localname.startswith(prefix):
            kod = localname
        else:
            kod = localname

        # Dodaj pozycję jeśli ma kwoty
        if kwota_a is not None or kwota_b is not None:
            opis = get_opis(kod, typ_jednostki, sekcja, wariant_rzis)
            poziom = calculate_poziom(kod)

            pozycje.append(PozycjaFinansowa(
                sekcja=sekcja,
                kod=kod,
                opis=opis,
                kwota_biezaca=kwota_a,
                kwota_poprzednia=kwota_b,
                poziom=poziom,
            ))

        # Rekurencyjnie przetwarzaj dzieci
        for child in element:
            child_name = self._safe_localname(child)

            # Pomijaj elementy bez nazwy
            if not child_name:
                continue

            # Pomijaj elementy kwot i metadane
            if child_name in ("KwotaA", "KwotaB", "KodSprawozdania", "WariantSprawozdania"):
                continue

            # Pomijaj podpisy i załączniki
            if "Signature" in child_name or "Zalacznik" in child_name:
                continue
            if "PozycjaUszczegolawiajaca" in child_name:
                continue

            # Rekurencja
            child_positions = self._extract_positions_recursive(
                child, sekcja, typ_jednostki, wariant_rzis, prefix, level + 1
            )
            pozycje.extend(child_positions)

        return pozycje

    def _parse_zalaczniki(self) -> list:
        """Parsuje załączniki binarne z dokumentu XML.

        Struktura załącznika w XML (zgodna ze schematem XSD):
        <DodatkoweInformacjeIObjasnienia>
            <Opis>Opis załącznika</Opis>
            <Plik>
                <Nazwa>nazwa_pliku.pdf</Nazwa>
                <Zawartosc>base64-encoded-content</Zawartosc>
            </Plik>
        </DodatkoweInformacjeIObjasnienia>

        Returns:
            Lista załączników (Zalacznik objects)
        """
        zalaczniki = []

        # Szukaj elementów zawierających załączniki
        # Możliwe miejsca: DodatkoweInformacjeIObjasnienia, InformacjeUzupelniajaceDoBilansu
        sekcje_z_zalacznikami = [
            "DodatkoweInformacjeIObjasnienia",
            "InformacjeUzupelniajaceDoBilansu",
            "InformacjaDodatkowa",
        ]

        for elem in self.root.iter():
            localname = self._safe_localname(elem)
            if not localname:
                continue

            # Sprawdź czy to sekcja z potencjalnymi załącznikami
            is_attachment_section = any(
                sekcja in localname for sekcja in sekcje_z_zalacznikami
            )

            if not is_attachment_section:
                continue

            # Szukaj elementu Plik wewnątrz sekcji
            opis = ""
            sekcja_nazwa = localname

            for child in elem:
                child_name = self._safe_localname(child)
                if not child_name:
                    continue

                # Pobierz opis
                if child_name == "Opis" and child.text:
                    opis = child.text.strip()

                # Znajdź element Plik
                if child_name == "Plik":
                    nazwa_pliku = None
                    zawartosc_base64 = None

                    for plik_child in child:
                        plik_child_name = self._safe_localname(plik_child)
                        if not plik_child_name:
                            continue
                        if plik_child_name == "Nazwa" and plik_child.text:
                            nazwa_pliku = plik_child.text.strip()
                        elif plik_child_name == "Zawartosc" and plik_child.text:
                            zawartosc_base64 = plik_child.text.strip()

                    # Jeśli mamy nazwę i zawartość, dekoduj i dodaj załącznik
                    if nazwa_pliku and zawartosc_base64:
                        try:
                            zawartosc = base64.b64decode(zawartosc_base64)
                            zalaczniki.append(Zalacznik(
                                nazwa_pliku=nazwa_pliku,
                                zawartosc=zawartosc,
                                sekcja=sekcja_nazwa,
                                opis=opis,
                            ))
                        except (ValueError, base64.binascii.Error) as e:
                            # Błąd dekodowania base64 - pomijamy załącznik
                            print(f"Ostrzeżenie: Nie można zdekodować załącznika {nazwa_pliku}: {e}")

        return zalaczniki

    def _verify_sums(self, aktywa: list, pasywa: list) -> WynikWeryfikacji:
        """Weryfikuje czy Aktywa = Pasywa."""
        aktywa_razem_biezacy = None
        aktywa_razem_poprzedni = None
        pasywa_razem_biezacy = None
        pasywa_razem_poprzedni = None

        # Pierwsza pozycja aktywów to suma
        if aktywa and aktywa[0].kod == "Aktywa":
            aktywa_razem_biezacy = aktywa[0].kwota_biezaca
            aktywa_razem_poprzedni = aktywa[0].kwota_poprzednia

        # Pierwsza pozycja pasywów to suma
        if pasywa and pasywa[0].kod == "Pasywa":
            pasywa_razem_biezacy = pasywa[0].kwota_biezaca
            pasywa_razem_poprzedni = pasywa[0].kwota_poprzednia

        return WynikWeryfikacji(
            aktywa_razem_biezacy=aktywa_razem_biezacy,
            pasywa_razem_biezacy=pasywa_razem_biezacy,
            aktywa_razem_poprzedni=aktywa_razem_poprzedni,
            pasywa_razem_poprzedni=pasywa_razem_poprzedni,
        )


def parse_file(file_path: str) -> Sprawozdanie:
    """Funkcja pomocnicza do parsowania pliku.

    Args:
        file_path: Ścieżka do pliku XML

    Returns:
        Sprawozdanie finansowe
    """
    parser = SFParser()
    return parser.parse(Path(file_path))
