"""Tab Helme. Das Layout steckt nur in draw() - hier spaeter anpassen."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


class HelmeTab(SchilderTab):
    TYP = "helme"
    FIELDS = [("marke", "Marke"), ("modell", "Modell"), ("groessen", "Größen"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]

    @staticmethod
    def draw(c, w, h, it):
        pad = 4 * mm
        breite = w - 2 * pad
        marke = it.get("marke", "")
        s = sheet.fit_font_size(marke, "Helvetica-Bold", 16, breite)
        c.setFont("Helvetica-Bold", s)
        c.drawString(pad, h - pad - s * 0.8, marke)
        modell = it.get("modell", "")
        s2 = sheet.fit_font_size(modell, "Helvetica", 12, breite)
        c.setFont("Helvetica", s2)
        c.drawString(pad, h - pad - s * 0.8 - s2 * 1.3, modell)
        if it.get("groessen"):
            c.setFont("Helvetica", 8)
            c.drawString(pad, pad + 1, "Größen: " + it["groessen"])
        preis = sheet.euro(it.get("preis", ""))
        sp = sheet.fit_font_size(preis, "Helvetica-Bold", 30, breite)
        c.setFont("Helvetica-Bold", sp)
        c.drawRightString(w - pad, pad + 10 * mm, preis)
        if it.get("statt"):
            statt = "statt " + sheet.euro(it["statt"])
            c.setFont("Helvetica", 10)
            c.drawRightString(w - pad, pad + 10 * mm + sp + 2, statt)
            breite_statt = c.stringWidth(statt, "Helvetica", 10)
            y = pad + 10 * mm + sp + 5
            c.setLineWidth(0.7)
            c.line(w - pad - breite_statt, y, w - pad, y)
