"""Tab Ski. Das Layout steckt nur in draw() - hier spaeter anpassen. Snowboard erbt es (tab_snowboard.py)."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


class SkiTab(SchilderTab):
    TYP = "ski"
    FIELDS = [("marke", "Marke"), ("modell", "Modell"),
              ("laengen", "Längen (z. B. 160–180 cm)"), ("detail", "Zusatz (z. B. inkl. Bindung)"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]
    LISTE = ("marke", "modell", "laengen", "preis")

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

        # Unten links: Laengen und Zusatz
        y = pad
        if it.get("detail"):
            d = it["detail"]
            c.setFont("Helvetica", sheet.fit_font_size(d, "Helvetica", 10, 0.5 * breite))
            c.drawString(pad, y, d)
            y += 15
        laengen = it.get("laengen", "")
        if laengen:
            c.setFont("Helvetica-Bold", sheet.fit_font_size(laengen, "Helvetica-Bold", 11, 0.5 * breite))
            c.drawString(pad, y, laengen)

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
