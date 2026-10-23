"""Tab Schlaeger. Das Layout steckt nur in draw() - hier spaeter anpassen.

Logo oben, Modell, zwei Linien mit Kopf/Gewicht/Besaitung/Balance (Beschriftung klein, Wert fett),
unten "UNSER PREIS" links und die UVP (rot, durchgestrichen) rechts."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


class SchlaegerTab(SchilderTab):
    TYP = "schlaeger"
    FIELDS = [("modell", "Modell (z. B. VCore Alpha L)"),
              ("kopf", "Kopf (z. B. 100 in² / 645 cm²)"), ("gewicht", "Gewicht (z. B. 260 g)"),
              ("besaitung", "Besaitung (z. B. 16/18)"), ("balance", "Balance (z. B. 335 mm)"),
              ("preis", "Unser Preis (€)"), ("uvp", "UVP (€, optional)")]
    LISTE = ("logo", "modell", "preis")

    @staticmethod
    def draw(c, w, h, it):
        pad = 5 * mm
        breite = w - 2 * pad
        BOLD, REG = "Helvetica-Bold", "Helvetica"
        grau = (0.35, 0.35, 0.35)

        # Logo oben mittig (die Marke steht im Logo)
        logo_h = 0.18 * h
        sheet.draw_logo(c, it.get("logo"), pad, h - pad - logo_h, breite, logo_h, anchor="n")

        modell = it.get("modell", "")
        c.setFont(BOLD, sheet.fit_font_size(modell, BOLD, 15, breite))
        c.drawString(pad, h * 0.68, modell)
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.setLineWidth(0.5)
        c.line(pad, h * 0.645, w - pad, h * 0.645)

        # Datenraster 2 x 2: links Kopf/Besaitung, rechts Gewicht/Balance
        rechts = pad + 0.58 * breite
        raster = [(pad, h * 0.55, "Kopf", it.get("kopf", "")), (rechts, h * 0.55, "Gewicht", it.get("gewicht", "")),
                  (pad, h * 0.37, "Besaitung", it.get("besaitung", "")), (rechts, h * 0.37, "Balance", it.get("balance", ""))]
        for x, y, label, wert in raster:
            if not wert:
                continue
            c.setFillColorRGB(*grau)
            c.setFont(REG, 7.5)
            c.drawString(x, y + 12, label)
            c.setFillColorRGB(0, 0, 0)
            c.setFont(BOLD, sheet.fit_font_size(wert, BOLD, 11, 0.55 * breite))
            c.drawString(x, y, wert)

        c.line(pad, h * 0.31, w - pad, h * 0.31)

        # Preis unten
        c.setFillColorRGB(*grau)
        c.setFont(BOLD, 7.5)
        c.drawString(pad, h * 0.23, "UNSER PREIS")
        c.setFillColorRGB(0, 0, 0)
        preis = sheet.euro(it.get("preis", ""))
        c.setFont(BOLD, sheet.fit_font_size(preis, BOLD, 22, 0.55 * breite))
        c.drawString(pad, h * 0.1, preis)
        if it.get("uvp"):
            uvp = sheet.euro(it["uvp"])
            c.setFillColorRGB(*grau)
            c.setFont(REG, 7.5)
            c.drawRightString(w - pad, h * 0.17, "UVP")
            c.setFillColorRGB(0.8, 0, 0)
            c.setStrokeColorRGB(0.8, 0, 0)
            c.setFont(BOLD, 10)
            c.drawRightString(w - pad, h * 0.1, uvp)
            b = c.stringWidth(uvp, BOLD, 10)
            c.setLineWidth(0.8)
            c.line(w - pad - b, h * 0.1 + 3.5, w - pad, h * 0.1 + 3.5)
        c.setFillColorRGB(0, 0, 0)
        c.setStrokeColorRGB(0, 0, 0)
