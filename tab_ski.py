"""Tab Ski. Das Layout steckt nur in draw() - hier spaeter anpassen. Snowboard erbt es (tab_snowboard.py).

Layout (Hochformat, alles zentriert): Logo, Kategorie (unterstrichen), Modell, Zusatzzeilen,
dann bis zu zwei Preisvarianten mit Beschriftung. Der Statt-Preis wird ohne Strich gedruckt
(wird im Laden von Hand durchgestrichen)."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


def preis_text(text):
    """'899' -> '899,- €', '1100' -> '1.100,- €', '199,90' -> '199,90 €'. Nicht lesbar -> unveraendert."""
    roh = (text or "").replace("€", "").replace("EUR", "").replace(",-", "").strip()
    if "," in roh:
        roh = roh.replace(".", "").replace(",", ".")  # deutsche Schreibweise 1.099,50
    try:
        zahl = float(roh)
    except ValueError:
        return (text or "").strip()
    if zahl == int(zahl):
        return f"{int(zahl):,}".replace(",", ".") + ",- €"
    return f"{zahl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


class SkiTab(SchilderTab):
    TYP = "ski"
    FIELDS = [("marke", "Marke"), ("kategorie", "Kategorie (z. B. Allmountain)"), ("modell", "Modell"),
              ("zusatz1", "Zusatz 1 (z. B. incl. Bindung)"), ("zusatz2", "Zusatz 2 (z. B. incl. Montage)"),
              ("text1", "Preis 1: Text (z. B. Setpreis bei uns)"), ("statt1", "Preis 1: alter Preis (€)"),
              ("preis1", "Preis 1 (€)"),
              ("text2", "Preis 2: Text (optional)"), ("statt2", "Preis 2: alter Preis (€)"),
              ("preis2", "Preis 2 (€, optional)")]
    LISTE = ("marke", "modell", "preis1")

    @staticmethod
    def draw(c, w, h, it):
        pad = 4 * mm
        mitte = w / 2
        breite = w - 2 * pad
        BOLD, REG = "Helvetica-Bold", "Helvetica"

        def zentriert(text, font, groesse, y, unterstrichen=False):
            c.setFont(font, groesse)
            c.drawCentredString(mitte, y, text)
            if unterstrichen:
                b = c.stringWidth(text, font, groesse)
                c.setLineWidth(0.7)
                c.line(mitte - b / 2, y - 1.5, mitte + b / 2, y - 1.5)

        # Logo oben mittig, sonst Marke als Text
        logo_h = 0.17 * h
        if it.get("logo"):
            sheet.draw_logo(c, it["logo"], pad, h - pad - logo_h, breite, logo_h, anchor="n")
        elif it.get("marke"):
            s = sheet.fit_font_size(it["marke"], BOLD, 22, breite)
            zentriert(it["marke"], BOLD, s, h - pad - s)

        # Inhalt: (Hoehe, Zeichenfunktion); der Platz unter dem Logo wird gleichmaessig verteilt
        bloecke = []

        def text(wert, font, groesse, unterstrichen=False):
            wert = (wert or "").strip()
            if wert:
                g = sheet.fit_font_size(wert, font, groesse, breite)
                bloecke.append((g, lambda y, wert=wert, g=g: zentriert(wert, font, g, y, unterstrichen)))

        def preiszeile(statt, preis):
            preis, statt = preis_text(preis), preis_text(statt)
            if not preis:
                return
            g = sheet.fit_font_size(preis, BOLD, 18, 0.5 * breite if statt else breite)

            def zeichnen(y):
                if statt:
                    gs = sheet.fit_font_size(statt, REG, 15, 0.42 * breite)
                    c.setFont(REG, gs)
                    c.drawCentredString(pad + 0.25 * breite, y, statt)
                    c.setFont(BOLD, g)
                    c.drawCentredString(pad + 0.73 * breite, y, preis)
                else:
                    zentriert(preis, BOLD, g, y)
            bloecke.append((g, zeichnen))

        text(it.get("kategorie"), REG, 12, unterstrichen=True)
        text(it.get("modell"), BOLD, 16)
        text(it.get("zusatz1"), REG, 11)
        text(it.get("zusatz2"), REG, 11)
        text(it.get("text1"), REG, 11)
        preiszeile(it.get("statt1"), it.get("preis1"))
        text(it.get("text2"), REG, 11)
        preiszeile(it.get("statt2"), it.get("preis2"))

        oben = h - pad - logo_h
        unten = pad
        frei = oben - unten - sum(g for g, _ in bloecke)
        luecke = max(frei / (len(bloecke) + 1), 2)
        y = oben
        for g, zeichnen in bloecke:
            y -= luecke + g
            zeichnen(y + g * 0.2)
