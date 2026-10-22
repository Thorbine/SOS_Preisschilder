"""Tab Tennisbaelle. Das Layout steckt nur in draw() - hier spaeter anpassen."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


class BaelleTab(SchilderTab):
    TYP = "baelle"
    FIELDS = [("name", "Marke / Ball"), ("inhalt", "Inhalt (z. B. 4er Dose)"),
              ("preis", "Preis (€)"), ("einzel", "Preis pro Ball (€, optional)")]

    @staticmethod
    def draw(c, w, h, it):
        pad = 3 * mm
        breite = w - 2 * pad
        name = it.get("name", "")
        s = sheet.fit_font_size(name, "Helvetica-Bold", 14, breite)
        c.setFont("Helvetica-Bold", s)
        c.drawString(pad, h - pad - s * 0.8, name)
        c.setFont("Helvetica", 9)
        c.drawString(pad, h - pad - s * 0.8 - 12, it.get("inhalt", ""))
        preis = sheet.euro(it.get("preis", ""))
        sp = sheet.fit_font_size(preis, "Helvetica-Bold", 24, breite)
        c.setFont("Helvetica-Bold", sp)
        c.drawRightString(w - pad, pad + 3 * mm, preis)
        if it.get("einzel"):
            c.setFont("Helvetica", 7)
            c.drawString(pad, pad + 1, sheet.euro(it["einzel"]) + " pro Ball")
