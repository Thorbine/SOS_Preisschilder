"""Tab Helme. Das Layout steckt nur in draw() - hier spaeter anpassen."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab

GROESSEN = ["S-M", "M-L", "L-XL"]  # Vorschlaege, beliebiger Text bleibt moeglich


class HelmeTab(SchilderTab):
    TYP = "helme"
    FIELDS = [("marke", "Marke"), ("modell", "Modell"),
              ("groesse1", "Größe 1", GROESSEN), ("mass1", "Maße 1 (z. B. 51–55 cm)"),
              ("groesse2", "Größe 2", GROESSEN), ("mass2", "Maße 2 (z. B. 55–59 cm)"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]
    LISTE = ("marke", "modell", "preis")

    @staticmethod
    def draw(c, w, h, it):
        pad = 4 * mm
        breite = w - 2 * pad
        logo_w = 0.32 * w if it.get("logo") else 0
        sheet.draw_logo(c, it.get("logo"), w - pad - logo_w, h - pad - 0.3 * h, logo_w, 0.3 * h)
        text_b = breite - logo_w - (3 * mm if logo_w else 0)
        marke = it.get("marke", "")
        s = sheet.fit_font_size(marke, "Helvetica-Bold", 16, text_b)
        c.setFont("Helvetica-Bold", s)
        c.drawString(pad, h - pad - s * 0.8, marke)
        modell = it.get("modell", "")
        s2 = sheet.fit_font_size(modell, "Helvetica", 12, text_b)
        c.setFont("Helvetica", s2)
        c.drawString(pad, h - pad - s * 0.8 - s2 * 1.3, modell)

        # Zwei Groessenzeilen unten links, z. B. "S-M  51–55 cm"
        zeilen = [(it.get("groesse1", ""), it.get("mass1", "")), (it.get("groesse2", ""), it.get("mass2", ""))]
        spalte = max(c.stringWidth(g, "Helvetica-Bold", 11) for g, _ in zeilen) + 8  # Maße bündig untereinander
        y = pad
        for g, m in reversed(zeilen):
            if not (g or m):
                continue
            c.setFont("Helvetica-Bold", 11)
            c.drawString(pad, y, g)
            c.setFont("Helvetica", 10)
            c.drawString(pad + spalte, y, m)
            y += 15

        preis = sheet.euro(it.get("preis", ""))
        sp = sheet.fit_font_size(preis, "Helvetica-Bold", 30, 0.55 * breite)
        c.setFont("Helvetica-Bold", sp)
        c.drawRightString(w - pad, pad, preis)
        if it.get("statt"):
            statt = "statt " + sheet.euro(it["statt"])
            c.setFont("Helvetica", 10)
            c.drawRightString(w - pad, pad + sp + 2, statt)
            breite_statt = c.stringWidth(statt, "Helvetica", 10)
            c.setLineWidth(0.7)
            c.line(w - pad - breite_statt, pad + sp + 5, w - pad, pad + sp + 5)
