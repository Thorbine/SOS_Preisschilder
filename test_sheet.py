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
    test_pdf()
    print("OK")
