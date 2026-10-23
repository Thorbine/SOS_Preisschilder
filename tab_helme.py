"""Tab Helme. Das Layout steckt nur in draw() - hier spaeter anpassen.

Layout: links grosses Logo (die Marke steht im Logo), rechts untereinander
Modell, Groesse ("L / 59-62 cm") und Preis."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from reportlab.lib.units import mm

import csv_import
import settings
import sheet
from tab_base import SchilderTab

GROESSEN = ["XS-S", "S-M", "M-L", "L-XL", "XL-XXL"]  # Vorschlaege, beliebiger Text bleibt moeglich


class HelmeTab(SchilderTab):
    TYP = "helme"
    FIELDS = [("modell", "Modell"),
              ("groesse1", "Größe", GROESSEN), ("mass1", "Maße (z. B. 51–55 cm)"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]
    LISTE = ("logo", "modell", "groesse1", "mass1", "preis")
    KOPIE_LEER = ("groesse1", "mass1")  # Kopie = gleicher Helm in anderer Groesse

    def _extra(self, p):
        ttk.Button(p, text="Helme aus CSV importieren…", command=self.csv_importieren).pack(anchor="w", pady=(0, 4))

    def csv_importieren(self):
        """Liest die Helm-CSV: je Hersteller und Modell ein Schild (ohne Haken), schon vorhandene bleiben unberuehrt."""
        pfad = filedialog.askopenfilename(title="Helm-CSV wählen", filetypes=[("CSV", "*.csv"), ("Alle Dateien", "*.*")])
        if not pfad:
            return
        try:
            neu = csv_import.lese_helme(pfad, settings.logos(self.TYP))
        except (OSError, ValueError) as e:
            messagebox.showerror("Import", f"Die Datei konnte nicht gelesen werden:\n{e}")
            return
        dazu = csv_import.zusammenfuehren(self.items, neu)
        for it in self.items:
            it.setdefault("_blatt", 0)
        self._speichern()
        ohne_logo = sorted({it["modell"] for it in neu if not it["logo"]})
        text = f"{dazu} neue Helme importiert, {len(neu) - dazu} waren schon in der Liste.\n\nDie neuen haben noch keine Größe und sind nicht auf dem Blatt."
        if ohne_logo:
            text += "\n\nOhne Logo (keine passende Datei im Ordner): " + ", ".join(ohne_logo)
        messagebox.showinfo("Import", text)

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
