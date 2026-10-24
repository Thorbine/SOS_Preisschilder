"""Start: python test_sheet.py"""
import os
import re
import tempfile

import sheet


def test_grid():
    # A4 210x297, Rand 10 -> nutzbar 190x277
    assert sheet.grid(95, 60, 10, 0) == (2, 4, False)  # 8 Stueck, gedreht nur 6
    assert sheet.grid(100, 60, 10, 0) == (3, 2, True)  # gedreht 6 statt 1*4
    assert sheet.pro_blatt(70, 40, 10, 0) == 12
    # Abstand zaehlt nur zwischen den Schildern: 3*60 + 2*5 = 190 passt genau
    assert sheet.grid(60, 50, 10, 5) == (3, 5, False)
    try:
        sheet.grid(250, 250, 10, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("zu grosses Schild muss abgelehnt werden")


def test_logos():
    import settings
    with tempfile.TemporaryDirectory() as d:
        alt = settings.LOGO_DIR
        settings.LOGO_DIR = d
        try:
            os.makedirs(os.path.join(d, "Helme"))
            for pfad in ("Helme/a.png", "Helme/b.txt", "gemeinsam.jpg"):
                open(os.path.join(d, pfad), "wb").close()
            assert settings.logos("helme") == ["Helme/a.png", "gemeinsam.jpg"]
            assert settings.logos("ski") == ["gemeinsam.jpg"]
        finally:
            settings.LOGO_DIR = alt


def test_csv_import():
    import csv_import
    kopf = "Art.-Nr.;Herst.kurz;Bez.;H.-Art.-Nr.;Orig. Farbe;Saison;SVK-P;RVK-P"
    zeilen = ["1;SALOMO;L1;DRIVER PRIME;black;H/W 2025;360,00;", "2;SALOMO;L1;Driver Prime;white;H/W 2026;380,00;",
              "3;POC;P1;Obex MIPS;black;H/W 2026;210,00;149,00", "4;POC;P1;Obex MIPS;grey;H/W 2026;210,00;149,00", "5;SOSSPO;;RTL Helm;;;20,00;"]
    with tempfile.TemporaryDirectory() as d:
        pfad = os.path.join(d, "h.csv")
        with open(pfad, "w", encoding="cp1252") as f:
            f.write("\n".join([kopf] + zeilen))
        items = csv_import.lese_helme(pfad, ["Helme/Salomon Schriftzug.png", "Helme/Salomon.png", "Helme/POC.png"])
    assert [(i["logo"], i["modell"], i["preis"], i["statt"]) for i in items] == [
        ("Helme/Salomon.png", "Driver Prime", "380", ""), ("Helme/POC.png", "Obex MIPS", "149", "210")]
    assert csv_import.zusammenfuehren(items, [dict(items[0])]) == 0


def test_groessen_anlegen():
    from tab_helme import anlegen_groessen
    g = ["XS-S", "S-M", "M-L"]
    items = [dict(logo="a", modell="Gems", preis="1"), dict(logo="a", modell="Alto", groesse1="M-L", mass1="55"),
             dict(logo="b", modell="Gems", preis="3")]
    assert anlegen_groessen(items, g) == 6
    assert [(i["logo"], i["modell"], i["groesse1"]) for i in items] == [
        ("a", "Gems", "XS-S"), ("a", "Gems", "S-M"), ("a", "Gems", "M-L"),
        ("a", "Alto", "XS-S"), ("a", "Alto", "S-M"), ("a", "Alto", "M-L"),
        ("b", "Gems", "XS-S"), ("b", "Gems", "S-M"), ("b", "Gems", "M-L")]
    assert [i for i in items if i["modell"] == "Alto" and i["groesse1"] == "M-L"][0]["mass1"] == "55"
    assert anlegen_groessen(items, g) == 0


def test_euro():
    assert sheet.euro("199,9") == "199,90 €"
    assert sheet.euro("5") == "5,00 €"
    assert sheet.euro("abc") == "abc"


def test_pdf():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.pdf")
        n = sheet.pro_blatt(100, 60, 10, 0)
        sheet.render_pdf(p, 100, 60, list(range(n + 1)), lambda c, w, h, it: None)
        seiten = len(re.findall(rb"/Type /Page(?!s)", open(p, "rb").read()))
        assert seiten == 2, f"n+1 Schilder -> 2 Seiten, war {seiten}"


if __name__ == "__main__":
    test_grid()
    test_euro()
    test_logos()
    test_csv_import()
    test_groessen_anlegen()
    test_pdf()
    print("OK")
