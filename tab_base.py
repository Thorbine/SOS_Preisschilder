"""Gemeinsame Basis der Schilder-Tabs (Helme, Baelle, ...).

Ein Unterklasse legt nur TYP (Schluessel in settings.TYPEN), FIELDS und draw() fest."""
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

import settings
import sheet


def pdf_oeffnen(pfad):
    if sys.platform == "darwin":
        subprocess.Popen(["open", pfad])
    elif sys.platform.startswith("win"):
        os.startfile(pfad)
    else:
        subprocess.Popen(["xdg-open", pfad])


class SchilderTab(ttk.Frame):
    TYP = ""
    FIELDS = []  # (key, Beschriftung)

    def __init__(self, master):
        super().__init__(master, padding=12)
        self.items = settings.load_list(self.TYP)
        self.vars = {k: tk.StringVar() for k, _ in self.FIELDS}
        self.anzahl = tk.IntVar(value=1)
        self.info = tk.StringVar()

        form = ttk.LabelFrame(self, text="Schild", padding=10)
        form.pack(fill="x")
        for i, (k, label) in enumerate(self.FIELDS):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=2, padx=(0, 8))
            ttk.Entry(form, textvariable=self.vars[k], width=36).grid(row=i, column=1, sticky="w", pady=2)
        n = len(self.FIELDS)
        ttk.Label(form, text="Anzahl").grid(row=n, column=0, sticky="w", pady=2)
        ttk.Spinbox(form, from_=1, to=500, textvariable=self.anzahl, width=6).grid(row=n, column=1, sticky="w", pady=2)

        knoepfe = ttk.Frame(self)
        knoepfe.pack(fill="x", pady=8)
        ttk.Button(knoepfe, text="Hinzufügen", command=self.hinzufuegen).pack(side="left")
        ttk.Button(knoepfe, text="Auswahl ändern", command=self.aendern).pack(side="left", padx=6)
        ttk.Button(knoepfe, text="Auswahl löschen", command=self.loeschen).pack(side="left")
        ttk.Button(knoepfe, text="Liste leeren", command=self.leeren).pack(side="left", padx=6)

        cols = [k for k, _ in self.FIELDS] + ["anzahl"]
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10, selectmode="browse")
        for k, label in self.FIELDS:
            self.tree.heading(k, text=label)
            self.tree.column(k, width=140, anchor="w")
        self.tree.heading("anzahl", text="Anzahl")
        self.tree.column("anzahl", width=60, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.auswahl_laden)

        unten = ttk.Frame(self)
        unten.pack(fill="x", pady=(8, 0))
        ttk.Label(unten, textvariable=self.info).pack(side="left")
        ttk.Button(unten, text="Drucken (PDF)", command=self.drucken).pack(side="right")

        self.bind("<Map>", lambda e: self.aktualisieren())  # Masse koennen im Einstellungs-Tab geaendert worden sein
        self.aktualisieren()

    def masse(self):
        s = settings.load()
        return s[self.TYP]["breite"], s[self.TYP]["hoehe"], s["rand"], s["abstand"]

    def aktualisieren(self):
        self.tree.delete(*self.tree.get_children())
        for i, it in enumerate(self.items):
            self.tree.insert("", "end", iid=str(i), values=[it.get(k, "") for k, _ in self.FIELDS] + [it["anzahl"]])
        gesamt = sum(it["anzahl"] for it in self.items)
        w, h, rand, abstand = self.masse()
        try:
            pb = sheet.pro_blatt(w, h, rand, abstand)
            blaetter = -(-gesamt // pb)
            self.info.set(f"{w:g} × {h:g} mm · {pb} Schilder pro Blatt · {gesamt} Schilder = {blaetter} Blatt")
        except ValueError as e:
            self.info.set(str(e))

    def _eingabe(self):
        try:
            anzahl = int(self.anzahl.get())
        except (tk.TclError, ValueError):
            anzahl = 0
        if anzahl < 1:
            messagebox.showwarning("Anzahl", "Die Anzahl muss mindestens 1 sein.")
            return None
        item = {k: self.vars[k].get().strip() for k, _ in self.FIELDS}
        if not any(item.values()):
            messagebox.showwarning("Schild", "Bitte mindestens ein Feld ausfüllen.")
            return None
        item["anzahl"] = anzahl
        return item

    def _speichern(self):
        settings.save_list(self.TYP, self.items)
        self.aktualisieren()

    def _auswahl(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def hinzufuegen(self):
        item = self._eingabe()
        if item:
            self.items.append(item)
            self._speichern()

    def aendern(self):
        i = self._auswahl()
        if i is None:
            messagebox.showinfo("Ändern", "Bitte erst ein Schild in der Liste auswählen.")
            return
        item = self._eingabe()
        if item:
            self.items[i] = item
            self._speichern()
            self.tree.selection_set(str(i))

    def loeschen(self):
        i = self._auswahl()
        if i is not None:
            del self.items[i]
            self._speichern()

    def leeren(self):
        if self.items and messagebox.askyesno("Liste leeren", "Alle Schilder dieser Liste löschen?"):
            self.items = []
            self._speichern()

    def auswahl_laden(self, _=None):
        i = self._auswahl()
        if i is None or i >= len(self.items):
            return
        for k, _label in self.FIELDS:
            self.vars[k].set(self.items[i].get(k, ""))
        self.anzahl.set(self.items[i]["anzahl"])

    def drucken(self):
        if not self.items:
            messagebox.showinfo("Drucken", "Die Liste ist leer.")
            return
        w, h, rand, abstand = self.masse()
        alle = [it for it in self.items for _ in range(it["anzahl"])]
        pfad = os.path.join(tempfile.gettempdir(), f"preisschilder_{self.TYP}.pdf")
        try:
            sheet.render_pdf(pfad, w, h, alle, self.draw, rand, abstand)
            pdf_oeffnen(pfad)
        except (ValueError, OSError) as e:
            messagebox.showerror("Drucken", str(e))

    @staticmethod
    def draw(c, w, h, item):
        raise NotImplementedError
