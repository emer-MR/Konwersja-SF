"""
Testy regresyjne konwertera e-sprawozdań finansowych.

Dwie grupy testów:
1. Syntetyczne (zawsze uruchamiane) - minimalne XML budowane w teście, bez
   danych rzeczywistych: mapowanie RZiS, kontrola spójności, modele
   dyskryminacyjne na znanych liczbach, okresy, parser (format 2025
   `Dokument`, JednostkaOp, WTysiacach, KRS w schemacie 1-0), konsolidacja
   wieloletnia (duplikat okresu, okresy niepełne, przeliczenie tysięcy),
   grupowanie podmiotów, walidator webowy.
2. Na próbkach rzeczywistych (pomijane, gdy katalogu próbek brak - próbki są
   poza repozytorium). Katalog: zmienna środowiskowa KONWERSJA_SF_PROBKI albo
   domyślnie `..\\[Legacy] Konwersja SF\\Analiza SF - struktura i konwersja`.

Uruchomienie: `python -m pytest tests -q` (z katalogu repozytorium).
"""

import importlib.util
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from parser import SFParser  # noqa: E402
from indicators import (  # noqa: E402
    RZIS_MAP, DaneFinansowe, KalkulatorWskaznikow, extract_financial_data_from_sprawozdanie,
)
from multi_converter import MultiYearConverter  # noqa: E402
import okresy  # noqa: E402
import batch  # noqa: E402

D = Decimal


# =============================================================================
# Generator syntetycznych XML
# =============================================================================

def _k(a, b=None):
    s = f"<KwotaA>{a}</KwotaA>"
    if b is not None:
        s += f"<KwotaB>{b}</KwotaB>"
    return s


def mikro_xml(od="2025-01-01", do="2025-12-31", data="2026-03-31", nazwa="TESTOWA SP. Z O.O.",
              nip="1234563218", krs="0000123456", kod="SprFinJednostkaMikroWZlotych",
              wersja="1-0E", dokument=False, aktywa=("481255.33", "449900.48"),
              at=("0", "0"), ao=("481255.33", "449900.48"), zap=("0", "0"), nal=("0", "0"),
              kw=("439666.70", "408311.85"), zob=("41588.63", "41588.63"), rez=("0", "0"),
              rzis=None):
    """Minimalne sprawozdanie jednostki mikro (struktura jak w XSD)."""
    rzis = rzis or dict(A=("0", "40000"), B=("0", "5544.15"), B_I=("0", "0"), C=("0", "0"),
                        D=("0", "0"), E=("0", "3101"), F=("0", "31354.85"))
    r = "".join(f"<{kod_}>{_k(*v)}" + ("<B_I>" + _k(*rzis['B_I']) + "</B_I>" if kod_ == "B" else "")
                + f"</{kod_}>" for kod_, v in rzis.items() if kod_ != "B_I")
    sf = f"""<JednostkaMikro>
  <Naglowek><OkresOd>{od}</OkresOd><OkresDo>{do}</OkresDo><DataSporzadzenia>{data}</DataSporzadzenia>
    <KodSprawozdania kodSystemowy="SFJMIZ (2)" wersjaSchemy="{wersja}">{kod}</KodSprawozdania>
    <WariantSprawozdania>1</WariantSprawozdania></Naglowek>
  <InformacjeOgolneJednostkaMikro><P_1><P_1A><NazwaFirmy>{nazwa}</NazwaFirmy></P_1A>
    <P_1C>{nip}</P_1C><P_1D>{krs}</P_1D></P_1></InformacjeOgolneJednostkaMikro>
  <BilansJednostkaMikro>
    <Aktywa>{_k(*aktywa)}<Aktywa_A>{_k(*at)}</Aktywa_A>
      <Aktywa_B>{_k(*ao)}<Aktywa_B_1>{_k(*zap)}</Aktywa_B_1><Aktywa_B_2>{_k(*nal)}</Aktywa_B_2></Aktywa_B>
      <Aktywa_C>{_k("0", "0")}</Aktywa_C><Aktywa_D>{_k("0", "0")}</Aktywa_D></Aktywa>
    <Pasywa>{_k(*aktywa)}<Pasywa_A>{_k(*kw)}<Pasywa_A_1>{_k("5000", "5000")}</Pasywa_A_1></Pasywa_A>
      <Pasywa_B>{_k(*zob)}<Pasywa_B_1>{_k(*rez)}</Pasywa_B_1></Pasywa_B></Pasywa>
  </BilansJednostkaMikro>
  <RZiSJednostkaMikro>{r}</RZiSJednostkaMikro>
</JednostkaMikro>"""
    if dokument:  # format 2025: korzeń Dokument, SF w TrescDokumentu
        return (f'<?xml version="1.0" encoding="UTF-8"?><Dokument xmlns="http://crd.gov.pl/wzor/2025/08/12/13821/">'
                f"<OpisDokumentu/><DaneDokumentu/><TrescDokumentu format=\"text/xml\">{sf}</TrescDokumentu>"
                "</Dokument>")
    return '<?xml version="1.0" encoding="UTF-8"?>' + sf


def zapisz(tmp_path, nazwa, tresc) -> Path:
    p = tmp_path / nazwa
    p.write_text(tresc, encoding="utf-8")
    return p


def parsuj(tmp_path, tresc, nazwa="sf.xml"):
    return SFParser().parse(zapisz(tmp_path, nazwa, tresc))


# =============================================================================
# 1. Mapowanie RZiS i kontrola spójności
# =============================================================================

def test_rzis_map_zysk_netto_wg_xsd():
    assert RZIS_MAP[("Inna", "porownawczy")]["ZN"] == "L"      # K = obowiązkowe zmniejszenia
    assert RZIS_MAP[("Inna", "porownawczy")]["OZ"] == "K"
    assert RZIS_MAP[("Inna", "kalkulacyjny")]["ZN"] == "O"
    assert RZIS_MAP[("Inna", "kalkulacyjny")]["WDO"] == "I"
    assert RZIS_MAP[("Mala", "porownawczy")]["ZN"] == "J"
    assert RZIS_MAP[("Mala", "kalkulacyjny")]["WS"] == "E"
    assert RZIS_MAP[("Mala", "kalkulacyjny")]["KDO"] == ("B", "C", "D")
    assert RZIS_MAP[("Inna", "kalkulacyjny")]["KDO"] == ("B", "D", "E")


def test_mikro_wartosci_i_spojnosc(tmp_path):
    s = parsuj(tmp_path, mikro_xml(rzis=dict(A=("1000", "0"), B=("700", "0"), B_I=("50", "0"),
                                             C=("20", "0"), D=("10", "0"), E=("60", "0"),
                                             F=("250", "0"))))
    d = extract_financial_data_from_sprawozdanie(s)
    assert d.wynik_ze_sprzedazy == D("300")
    assert d.wynik_z_dzialalnosci_operacyjnej == D("310")
    assert d.zysk_strata_brutto == D("310")          # F + E
    assert not [u for u in d.uwagi if u.startswith("NIESPÓJNOŚĆ")]


def test_mikro_niespojnosc_rzis_generuje_uwage(tmp_path):
    s = parsuj(tmp_path, mikro_xml(rzis=dict(A=("1000", "0"), B=("700", "0"), B_I=("0", "0"),
                                             C=("0", "0"), D=("0", "0"), E=("0", "0"),
                                             F=("200", "0"))))  # powinno być 300
    d = extract_financial_data_from_sprawozdanie(s)
    assert any(u.startswith("NIESPÓJNOŚĆ RZiS") for u in d.uwagi)


def test_mikro_ujemne_koszty_i_amortyzacja(tmp_path):
    s = parsuj(tmp_path, mikro_xml(rzis=dict(A=("1000", "0"), B=("-700", "0"), B_I=("-50", "0"),
                                             C=("0", "0"), D=("0", "0"), E=("0", "0"),
                                             F=("300", "0"))))
    d = extract_financial_data_from_sprawozdanie(s)
    assert d.koszty_dzialalnosci_operacyjnej == D("700")
    assert d.amortyzacja == D("50")


# =============================================================================
# 2. Modele dyskryminacyjne na znanych liczbach
# =============================================================================

def _dane_wzorcowe():
    return DaneFinansowe(
        typ_jednostki="Inna", aktywa_ogolem=D("1000"), aktywa_ogolem_poprz=D("1000"),
        aktywa_obrotowe=D("600"), aktywa_trwale=D("400"), zapasy=D("100"),
        zobowiazania_krotkoterminowe=D("300"), zobowiazania_krotkoterminowe_poprz=D("300"),
        zobowiazania_dlugoterminowe=D("100"), zobowiazania_ogolem=D("400"),
        kapital_wlasny=D("600"), zysk_zatrzymany=D("200"),
        przychody_netto_ze_sprzedazy=D("2000"), koszty_dzialalnosci_operacyjnej=D("1900"),
        wynik_ze_sprzedazy=D("100"), wynik_z_dzialalnosci_operacyjnej=D("120"),
        zysk_strata_brutto=D("110"), zysk_strata_netto=D("90"), dni_okresu=365,
    )


def _wynik(dane, skrot):
    return {w.skrot: w for w in KalkulatorWskaznikow(dane).oblicz_wszystkie()}[skrot].wartosc


def test_model_poznanski():
    # X1 = 90/1000, X2 = (600-100)/300, X3 = (600+100)/1000, X4 = 100/2000
    oczek = (D("3.562") * D("0.09") + D("1.588") * (D("500") / D("300")) + D("4.288") * D("0.7")
             + D("6.719") * D("0.05") - D("2.368"))
    assert abs(_wynik(_dane_wzorcowe(), "FD_P") - oczek) < D("0.0001")
    assert abs(oczek - D("3.9368")) < D("0.001")


def test_model_gajdki_stosa():
    # X1 = 2000/1000, X2 = 300*365/1900, X3 = 90/1000, X4 = 110/2000, X5 = 400/1000
    oczek = (D("0.7732059") - D("0.0856425") * 2 + D("0.0007747") * (D("300") * 365 / D("1900"))
             + D("0.9220985") * D("0.09") + D("0.6535995") * D("0.055") - D("0.594687") * D("0.4"))
    assert abs(_wynik(_dane_wzorcowe(), "FD_GS") - oczek) < D("0.0001")


def test_model_altmana_z_prim():
    # X1 = (600-300)/1000, X2 = 200/1000, X3 = 120/1000, X4 = 600/400, X5 = 2000/1000
    oczek = (D("0.717") * D("0.3") + D("0.847") * D("0.2") + D("3.107") * D("0.12")
             + D("0.420") * D("1.5") + D("0.998") * 2)
    assert abs(_wynik(_dane_wzorcowe(), "FD_A") - oczek) < D("0.0001")
    assert abs(oczek - D("3.3833")) < D("0.001")


def test_cykle_skalowane_do_dlugosci_okresu():
    d = _dane_wzorcowe()
    pelny = _wynik(d, "CZ")                  # 100*365/2000 = 18,25
    d.dni_okresu = 183
    niepelny = _wynik(d, "CZ")               # 100*183/2000
    assert abs(pelny - D("18.25")) < D("0.0001")
    assert abs(niepelny - D("100") * 183 / D("2000")) < D("0.0001")


def test_jednostka_przy_kwotach_bezwzglednych():
    d = _dane_wzorcowe()
    assert _kp_str(d).endswith(" zł")
    d.jednostka_walutowa = "tys. PLN"
    assert _kp_str(d).endswith(" tys. zł")


def _kp_str(d):
    return {w.skrot: w for w in KalkulatorWskaznikow(d).oblicz_wszystkie()}["KP"].wartosc_str


# =============================================================================
# 3. Okresy
# =============================================================================

def test_okresy_etykiety_i_okres_poprzedni():
    assert okresy.etykieta_okresu(date(2022, 1, 1), date(2022, 12, 31)) == "2022"
    assert okresy.etykieta_okresu(date(2022, 1, 1), date(2022, 7, 17)) == "2022 (01.01-17.07)"
    assert okresy.etykieta_okresu(date(2022, 4, 1), date(2023, 3, 31)) == "01.04.2022-31.03.2023"
    assert okresy.okres_poprzedni(date(2022, 4, 1), date(2023, 3, 31)) == (date(2021, 4, 1), date(2022, 3, 31))
    assert okresy.okres_poprzedni(date(2022, 7, 18), date(2022, 12, 31)) == (None, date(2022, 7, 17))


# =============================================================================
# 4. Parser
# =============================================================================

def test_format_2025_dokument(tmp_path):
    s = parsuj(tmp_path, mikro_xml(dokument=True))
    assert s.metadane.typ_jednostki == "Mikro"
    assert s.metadane.okres_do == date(2025, 12, 31)
    assert s.metadane.data_sporzadzenia == date(2026, 3, 31)
    assert s.metadane.jednostka_walutowa == "PLN"
    assert s.dane_firmy.nip == "1234563218" and s.dane_firmy.krs == "0000123456"
    d = extract_financial_data_from_sprawozdanie(s)
    assert d.aktywa_ogolem == D("481255.33")
    assert d.kapital_wlasny == D("439666.70")
    assert d.zobowiazania_ogolem == D("41588.63")
    assert d.przychody_netto_ze_sprzedazy == D("0")
    assert d.zysk_strata_netto == D("0")
    rz = {p.kod: p for p in s.rzis}
    assert d.aktywa_ogolem_poprz == D("449900.48")
    assert rz["A"].kwota_poprzednia == D("40000") and rz["F"].kwota_poprzednia == D("31354.85")


def test_jednostka_op_czytelny_blad(tmp_path):
    xml = ('<?xml version="1.0" encoding="UTF-8"?><JednostkaOp><Naglowek><OkresOd>2024-01-01</OkresOd>'
           '<OkresDo>2024-12-31</OkresDo></Naglowek></JednostkaOp>')
    with pytest.raises(ValueError, match="Nieobsługiwany typ sprawozdania"):
        parsuj(tmp_path, xml)


def test_wtysiacach_z_kodu_sprawozdania(tmp_path):
    s = parsuj(tmp_path, mikro_xml(dokument=True, kod="SprFinJednostkaMikroWTysiacach"))
    assert s.metadane.jednostka_walutowa == "tys. PLN"


def test_krs_w_elemencie_potomnym_schemat_1_0(tmp_path):
    xml = mikro_xml(nip="", krs="").replace("<P_1C></P_1C><P_1D></P_1D>",
                                            "<P_1C><KRS>0000544708</KRS></P_1C>")
    s = parsuj(tmp_path, xml)
    assert s.dane_firmy.krs == "0000544708"


# =============================================================================
# 5. Konsolidacja wieloletnia i grupowanie
# =============================================================================

def _multi(tmp_path, pliki):
    pary = [(p, SFParser().parse(p)) for p in pliki]
    conv = MultiYearConverter()
    out, _ = conv.convert(pary, tmp_path / "out")
    return conv, out


def test_duplikat_okresu_wygrywa_pozniejsza_data(tmp_path):
    p1 = zapisz(tmp_path, "a.xml", mikro_xml(data="2026-03-31"))
    p2 = zapisz(tmp_path, "b_korekta.xml", mikro_xml(data="2026-06-30", aktywa=("481255.33", "449900.48")))
    conv, _ = _multi(tmp_path, [p1, p2])
    assert len(conv.reports) == 1
    assert conv.reports[0].metadane.data_sporzadzenia == date(2026, 6, 30)
    assert any("ten sam okres" in o for o in conv.ostrzezenia)


def test_okresy_niepelne_osobne_kolumny_i_rozbieznosci(tmp_path):
    a = zapisz(tmp_path, "a.xml", mikro_xml(od="2022-01-01", do="2022-07-17", aktywa=("100", "90")))
    b = zapisz(tmp_path, "b.xml", mikro_xml(od="2022-07-18", do="2022-12-31", aktywa=("120", "101")))
    conv, _ = _multi(tmp_path, [a, b])
    lata, wiersze = conv._merge_section(lambda s: s.bilans_aktywa)
    assert [okresy.etykieta_okresu(*k) for k in lata[-2:]] == ["2022 (01.01-17.07)", "2022 (18.07-31.12)"]
    aktywa = next(w for w in wiersze if w["kod"] == "Aktywa")
    assert aktywa["values"][(date(2022, 1, 1), date(2022, 7, 17))] == D("100")   # z SF za okres
    roz = [r for r in conv.rozbieznosci if r["kod"] == "Aktywa"]
    assert roz and roz[0]["kwota_porown"] == D("101") and roz[0]["kwota_sf"] == D("100")


def test_przeliczenie_tysiecy(tmp_path):
    zl = zapisz(tmp_path, "2024.xml", mikro_xml(od="2024-01-01", do="2024-12-31", data="2025-03-31",
                                               aktywa=("449900.48", "1000"), kw=("408311.85", "0"),
                                               zob=("41588.63", "1000"), ao=("449900.48", "1000")))
    tys = zapisz(tmp_path, "2025.xml", mikro_xml(kod="SprFinJednostkaMikroWTysiacach",
                                                aktywa=("481.26", "449.90"), kw=("439.67", "408.31"),
                                                zob=("41.59", "41.59"), ao=("481.26", "449.90")))
    conv, _ = _multi(tmp_path, [zl, tys])
    r25 = conv.reports[-1]
    assert r25.metadane.jednostka_walutowa == "PLN"
    assert next(p for p in r25.bilans_aktywa if p.kod == "Aktywa").kwota_biezaca == D("481260")
    assert any("tysiącach" in o for o in conv.ostrzezenia)
    # 449 900 (tys.) vs 449 900,48 - w tolerancji zaokrągleń (10 zł)
    assert not [r for r in conv.rozbieznosci if r["kod"] in ("Aktywa", "Pasywa_A", "Pasywa_B")]


def test_grupowanie_union_find(tmp_path):
    class F:
        def __init__(self, nazwa, nip="", krs=None):
            self.dane_firmy = type("DF", (), dict(nazwa=nazwa, nip=nip, krs=krs))()
    pary = [(Path("a.xml"), F("Strefa Sp.z o.o.", "", "0000544708")),
            (Path("b.xml"), F("Strefa sp. z o.o. w likwidacji", "7272794779", "0000544708")),
            (Path("c.xml"), F("Lavinia sp. z o.o.", "5252571325")),
            (Path("d.xml"), F("Lavinia sp. z o.o. SKA", "5252572543"))]
    grupy = list(batch._grupuj_podmioty(pary, log=lambda *a: None).values())
    assert len(grupy) == 3
    assert batch._normalizuj_nazwe("STREFA Sp.z o.o. w likwidacji") == batch._normalizuj_nazwe("Strefa")


# =============================================================================
# 6. Walidator aplikacji webowej (format 2025 i JednostkaOp)
# =============================================================================

def _web_validator():
    sciezka = REPO / "web" / "app" / "xml_validator.py"
    spec = importlib.util.spec_from_file_location("xml_validator_web", sciezka)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_web_walidator_dokument_2025_i_jednostka_op():
    v = _web_validator()
    ok, blad, typ = v.validate_xml(mikro_xml(dokument=True).encode("utf-8"))
    assert ok and typ == "Mikro", blad
    ok, blad, _ = v.validate_xml(b'<?xml version="1.0"?><JednostkaOp><Naglowek/><Bilans/></JednostkaOp>')
    assert not ok and "Nieobsługiwany" in blad


# =============================================================================
# 7. Próbki rzeczywiste (pomijane, gdy brak katalogu)
# =============================================================================

PROBKI = Path(os.environ.get(
    "KONWERSJA_SF_PROBKI",
    REPO.parent / "[Legacy] Konwersja SF" / "Analiza SF - struktura i konwersja"))
wymaga_probek = pytest.mark.skipif(not PROBKI.is_dir(), reason=f"brak katalogu próbek: {PROBKI}")


def _probka(*czesci):
    p = PROBKI.joinpath(*czesci)
    if not p.exists():
        pytest.skip(f"brak próbki {p}")
    return extract_financial_data_from_sprawozdanie(SFParser().parse(p))


@wymaga_probek
def test_probka_sun_stone_2022_zysk_netto_z_poz_L():
    d = _probka("Przykłady konwersji", "6", "SUN STONE INTERNATIONAL SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ.xml")
    assert d.zysk_strata_netto == D("-2293954.16")


@wymaga_probek
def test_probka_amontex_kalkulacyjny_inna():
    d = _probka("Test 2", "eSPR_report.xml")
    assert d.zysk_strata_netto == D("-313826.55")
    assert d.wynik_z_dzialalnosci_operacyjnej == D("-361383.33")


@wymaga_probek
def test_probka_miflex_kalkulacyjny_mala_okres_niepelny():
    d = _probka("Test 2", "ZAKŁADY PODZESPOŁÓW RADIOWYCH MIFLEX S.A..xml")
    assert d.wynik_ze_sprzedazy == D("-1882700.11")
    assert d.dni_okresu == 334


@wymaga_probek
def test_probka_pms_brak_zobowiazan_dlugoterminowych_to_zero():
    d = _probka("Przykłady konwersji", "4", "SPRAWOZDANIE_PMS_2022-2.xml")
    assert d.zobowiazania_dlugoterminowe == D("0")
    assert _wynik(d, "FD_P") is not None
