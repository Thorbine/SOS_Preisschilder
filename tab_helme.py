"""Tab Helme. Das Layout steckt nur in draw() - hier spaeter anpassen.

Layout: links grosses Logo (die Marke steht im Logo), rechts untereinander
Modell, Groesse ("L / 59-62 cm") und Preis."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab

GROESSEN = ["S-M", "M-L", "L-XL"]  # Vorschlaege, beliebiger Text bleibt moeglich


class HelmeTab(SchilderTab):
    TYP = "helme"
    FIELDS = [("modell", "Modell"),
              ("groesse1", "Größe", GROESSEN), ("mass1", "Maße (z. B. 51–55 cm)"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]
    LISTE = ("logo", "modell", "groesse1", "preis")

    @staticmethod
    def draw(c, w, h, it):
        pad = 5 * mm
        links_b = 0.42 * w - pad
        x0 = 0.48 * w  # linke Kante der Textspalte
        text_b = w - pad - x0

        # Links: Logo mittig-links
        sheet.draw_logo(c, it.get("logo"), pad, 0.2 * h, links_b, 0.6 * h, anchor="w")

        # Rechts: Modell oben
        modell = it.get("modell", "")
        sm = sheet.fit_font_size(modell, "Helvetica-Bold", 15, text_b)
        c.setFont("Helvetica-Bold", sm)
        c.drawString(x0, h * 0.72, modell)

        # Groesse mittig, "L / 59-62 cm"
        zeile = " / ".join(x for x in (it.get("groesse1", ""), it.get("mass1", "")) if x)
        if zeile:
            c.setFont("Helvetica-Bold", sheet.fit_font_size(zeile, "Helvetica-Bold", 10, text_b))
            c.drawString(x0, h * 0.52, zeile)

        # Preis unten, Statt-Preis klein darueber durchgestrichen
        preis = sheet.euro(it.get("preis", ""))
        sp = sheet.fit_font_size(preis, "Helvetica-Bold", 20, text_b)
        c.setFont("Helvetica-Bold", sp)
        c.drawString(x0, h * 0.18, preis)
        if it.get("statt"):
            statt = "statt " + sheet.euro(it["statt"])
            c.setFont("Helvetica", 9)
            c.drawString(x0, h * 0.18 + sp + 3, statt)
            c.setLineWidth(0.6)
            yl = h * 0.18 + sp + 3 + 3
            c.line(x0, yl, x0 + c.stringWidth(statt, "Helvetica", 9), yl)
