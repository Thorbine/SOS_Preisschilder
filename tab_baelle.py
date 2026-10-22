"""Tab Tennisbaelle. Das Layout steckt nur in draw() - hier spaeter anpassen.

Flacher Regalstreifen: links Logo, daneben Bezeichnung (klein) ueber dem Ballnamen,
in der Mitte der Inhalt (z. B. 4er Dose), rechts der Preis."""
from reportlab.lib.units import mm

import sheet
from tab_base import SchilderTab


class BaelleTab(SchilderTab):
    TYP = "baelle"
    FIELDS = [("typ", "Bezeichnung (z. B. DTB-Spielball)"), ("name", "Marke / Ball (z. B. Fort Tournament)"),
              ("inhalt", "Inhalt (z. B. 4er Dose)"),
              ("preis", "Preis (€)"), ("einzel", "Preis pro Ball (€, optional)")]
    LISTE = ("name", "inhalt", "preis")

    @staticmethod
    def draw(c, w, h, it):
        pad = 2.5 * mm
        BOLD, REG = "Helvetica-Bold", "Helvetica"
        logo_b = 0.2 * w if it.get("logo") else 0
        sheet.draw_logo(c, it.get("logo"), pad, pad, logo_b, h - 2 * pad, anchor="w")
        x0 = pad + logo_b + (4 * mm if logo_b else 0)
        spalte = 0.58 * w  # Inhalt beginnt hier
        text_b = spalte - x0 - 2 * mm

        typ, name = it.get("typ", ""), it.get("name", "")
        if typ and name:
            c.setFont(REG, sheet.fit_font_size(typ, REG, 9, text_b))
            c.drawString(x0, h * 0.58, typ)
            c.setFont(BOLD, sheet.fit_font_size(name, BOLD, 11, text_b))
            c.drawString(x0, h * 0.2, name)
        elif typ or name:
            t = typ or name
            c.setFont(BOLD, sheet.fit_font_size(t, BOLD, 12, text_b))
            c.drawString(x0, h * 0.38, t)

        inhalt = it.get("inhalt", "")
        if inhalt:
            c.setFont(REG, sheet.fit_font_size(inhalt, REG, 9, 0.2 * w))
            c.drawString(spalte, h * 0.2, inhalt)

        preis = sheet.euro(it.get("preis", ""))
        einzel = it.get("einzel")
        sp = sheet.fit_font_size(preis, BOLD, 13, 0.22 * w)
        c.setFont(BOLD, sp)
        c.drawRightString(w - pad, h * (0.5 if einzel else 0.36), preis)
        if einzel:
            c.setFont(REG, 6.5)
            c.drawRightString(w - pad, h * 0.18, sheet.euro(einzel) + " pro Ball")
