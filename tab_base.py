"""Gemeinsame Basis der Schilder-Tabs (Helme, Baelle, ...).

Eine Unterklasse legt nur TYP (Schluessel in settings.TYPEN), FIELDS, LISTE und draw() fest.
Links Eingabe + Liste, rechts die Vorschau des aktuellen Druckbogens."""
import base64
import io
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from PIL import Image, ImageTk

import settings
import sheet

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None


def pdf_oeffnen(pfad):
    if sys.platform == "darwin":
        subprocess.Popen(["open", pfad])
    elif sys.platform.startswith("win"):
        os.startfile(pfad)
    else:
        subprocess.Popen(["xdg-open", pfad])


class SchilderTab(ttk.Frame):
    TYP = ""
    FIELDS = []  # (key, Beschriftung) oder (key, Beschriftung, [Vorschlaege]) -> frei editierbare Auswahl
    LISTE = ()   # Felder, die in der Liste stehen (leer = alle)

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.items = settings.load_list(self.TYP)
        self.keys = [f[0] for f in self.FIELDS] + ["logo"]
        self.vars = {k: tk.StringVar() for k in self.keys}
        self.anzahl = tk.IntVar(value=1)
        self.info = tk.StringVar()
        self.seite = 0
        self._job = None
        self._bild = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        links = ttk.Frame(self)
        links.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self._links(links)
        rechts = ttk.LabelFrame(self, text="Vorschau Druckbogen", padding=6)
        rechts.grid(row=0, column=1, sticky="nsew")
        self._rechts(rechts)

        for v in self.vars.values():
            v.trace_add("write", lambda *_: self._vorschau_planen())
        self.bind("<Map>", lambda e: self.aktualisieren())  # Masse koennen im Einstellungs-Tab geaendert worden sein
        self.aktualisieren()

    # --- Aufbau ---
    def _links(self, p):
        form = ttk.LabelFrame(p, text="Schild", padding=8)
        form.pack(fill="x")
        for i, f in enumerate(self.FIELDS):
            ttk.Label(form, text=f[1]).grid(row=i, column=0, sticky="w", pady=2, padx=(0, 8))
            if len(f) > 2:
                w = ttk.Combobox(form, textvariable=self.vars[f[0]], values=f[2], width=22)
            else:
                w = ttk.Entry(form, textvariable=self.vars[f[0]], width=24)
            w.grid(row=i, column=1, sticky="w", pady=2)
        n = len(self.FIELDS)
        ttk.Label(form, text="Anzahl").grid(row=n, column=0, sticky="w", pady=2)
        ttk.Spinbox(form, from_=1, to=500, textvariable=self.anzahl, width=6).grid(row=n, column=1, sticky="w", pady=2)
        self._logo_auswahl(p)

        kn = ttk.Frame(p)
        kn.pack(fill="x", pady=8)
        ttk.Button(kn, text="Hinzufügen", command=self.hinzufuegen).pack(side="left")
        ttk.Button(kn, text="Ändern", command=self.aendern).pack(side="left", padx=4)
        ttk.Button(kn, text="Löschen", command=self.loeschen).pack(side="left")
        ttk.Button(kn, text="Liste leeren", command=self.leeren).pack(side="left", padx=4)

        spalten = list(self.LISTE or [f[0] for f in self.FIELDS]) + ["anzahl"]
        beschr = {f[0]: f[1] for f in self.FIELDS}
        self.tree = ttk.Treeview(p, columns=spalten, show="headings", height=4, selectmode="browse")
        for k in spalten[:-1]:
            self.tree.heading(k, text=beschr[k])
            self.tree.column(k, width=110, anchor="w")
        self.tree.heading("anzahl", text="Anzahl")
        self.tree.column("anzahl", width=55, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.auswahl_laden)
        self.spalten = spalten[:-1]

        unten = ttk.Frame(p)
        unten.pack(fill="x", pady=(8, 0))
        ttk.Label(unten, textvariable=self.info, wraplength=360, justify="left").pack(side="left")
        ttk.Button(unten, text="Drucken (PDF)", command=self.drucken).pack(side="right")

    # --- Logo-Auswahl: Kacheln statt Dateidialog ---
    def _logo_auswahl(self, p):
        box = ttk.LabelFrame(p, text=f"Logo  (Ordner: daten/logos/{settings.TYPEN[self.TYP][0]})", padding=6)
        box.pack(fill="x", pady=(8, 0))
        kopf = ttk.Frame(box)
        kopf.pack(fill="x", pady=(0, 4))
        ttk.Button(kopf, text="Ordner öffnen", command=self.logo_ordner_oeffnen).pack(side="left")
        ttk.Button(kopf, text="Logo hinzufügen…", command=self.logo_waehlen).pack(side="left", padx=4)
        ttk.Button(kopf, text="Neu laden", command=self.logos_laden).pack(side="left")
        self.logo_text = tk.StringVar()
        ttk.Label(kopf, textvariable=self.logo_text, foreground="gray").pack(side="right")
        raum = ttk.Frame(box)
        raum.pack(fill="x")
        self.logo_canvas = tk.Canvas(raum, height=104, highlightthickness=0, background="white")
        sb = ttk.Scrollbar(raum, orient="vertical", command=self.logo_canvas.yview)
        self.logo_canvas.configure(yscrollcommand=sb.set)
        self.logo_canvas.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")
        self.logo_innen = tk.Frame(self.logo_canvas, background="white")
        self.logo_canvas.create_window((0, 0), window=self.logo_innen, anchor="nw")
        self.logo_innen.bind("<Configure>", lambda e: self.logo_canvas.configure(scrollregion=self.logo_canvas.bbox("all")))
        self.logo_canvas.bind("<Enter>", lambda e: self.logo_canvas.bind_all("<MouseWheel>", self._logo_rad))
        self.logo_canvas.bind("<Leave>", lambda e: self.logo_canvas.unbind_all("<MouseWheel>"))
        self._kacheln = {}
        self._thumbs = {}  # (name, mtime) -> PhotoImage
        self._logo_stand = None
        self.vars["logo"].trace_add("write", lambda *_: self._logo_markieren())

    def _logo_rad(self, e):
        self.logo_canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def _thumb(self, name):
        pfad = os.path.join(settings.LOGO_DIR, name)
        key = (name, os.path.getmtime(pfad))
        if key not in self._thumbs:
            im = Image.open(pfad).convert("RGBA")
            im.thumbnail((92, 44))
            bg = Image.new("RGBA", im.size, "white")
            bg.alpha_composite(im)
            self._thumbs[key] = ImageTk.PhotoImage(bg.convert("RGB"))
        return self._thumbs[key]

    def logos_laden(self, _=None):
        """Kacheln neu aufbauen - nur wenn sich die Dateien geaendert haben."""
        namen = settings.logos(self.TYP)
        stand = []
        for n in namen:
            try:
                stand.append((n, os.path.getmtime(os.path.join(settings.LOGO_DIR, n))))
            except OSError:
                pass
        if stand == self._logo_stand:
            return
        self._logo_stand = stand
        for w in self.logo_innen.winfo_children():
            w.destroy()
        self._kacheln = {}
        spalten = 4
        for i, name in enumerate([""] + [n for n, _ in stand]):
            try:
                if name:
                    kachel = tk.Label(self.logo_innen, image=self._thumb(name), background="white", bd=2, relief="flat")
                else:
                    kachel = tk.Label(self.logo_innen, text="kein Logo", foreground="gray", background="white",
                                      width=11, height=3, bd=2, relief="flat")
            except Exception:
                continue  # defekte Bilddatei ueberspringen
            kachel.grid(row=i // spalten, column=i % spalten, padx=2, pady=2)
            kachel.bind("<Button-1>", lambda e, n=name: self.vars["logo"].set(n))
            self._kacheln[name] = kachel
        self._logo_markieren()

    def _logo_markieren(self):
        aktuell = self.vars["logo"].get()
        for name, k in self._kacheln.items():
            k.configure(relief="solid" if name == aktuell else "flat", background="#cfe3ff" if name == aktuell else "white")
        self.logo_text.set(aktuell or "kein Logo")

    def logo_ordner_oeffnen(self):
        settings.logo_ordner_anlegen()
        pdf_oeffnen(settings.logo_ordner(self.TYP))

    def _rechts(self, p):
        nav = ttk.Frame(p)
        nav.pack(side="bottom", fill="x", pady=(6, 0))
        ttk.Button(nav, text="◀", width=3, command=lambda: self.blaettern(-1)).pack(side="left")
        self.seiten_text = tk.StringVar()
        ttk.Label(nav, textvariable=self.seiten_text).pack(side="left", padx=8)
        ttk.Button(nav, text="▶", width=3, command=lambda: self.blaettern(1)).pack(side="left")
        self.canvas = tk.Canvas(p, background="#9a9a9a", highlightthickness=0, width=420, height=560)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._vorschau_planen())

    # --- Daten ---
    def masse(self):
        s = settings.load()
        return s[self.TYP]["breite"], s[self.TYP]["hoehe"], s["rand"], s["abstand"]

    def aktualisieren(self):
        self.logos_laden()
        self.tree.delete(*self.tree.get_children())
        for i, it in enumerate(self.items):
            self.tree.insert("", "end", iid=str(i), values=[it.get(k, "") for k in self.spalten] + [it["anzahl"]])
        gesamt = sum(it["anzahl"] for it in self.items)
        w, h, rand, abstand = self.masse()
        try:
            pb = sheet.pro_blatt(w, h, rand, abstand)
            self.info.set(f"{w:g} × {h:g} mm · {pb} pro Blatt\n{gesamt} Schilder = {-(-gesamt // pb)} Blatt")
        except ValueError as e:
            self.info.set(str(e))
        self._vorschau_planen()

    def _form_item(self, anzahl=1):
        item = {k: self.vars[k].get().strip() for k in self.keys}
        item["anzahl"] = anzahl
        return item

    def _eingabe(self):
        try:
            anzahl = int(self.anzahl.get())
        except (tk.TclError, ValueError):
            anzahl = 0
        if anzahl < 1:
            messagebox.showwarning("Anzahl", "Die Anzahl muss mindestens 1 sein.")
            return None
        item = self._form_item(anzahl)
        if not any(v for k, v in item.items() if k != "anzahl"):
            messagebox.showwarning("Schild", "Bitte mindestens ein Feld ausfüllen.")
            return None
        return item

    def _speichern(self):
        settings.save_list(self.TYP, self.items)
        self.aktualisieren()

    def _auswahl(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def logo_waehlen(self):
        pfad = filedialog.askopenfilename(title="Logo wählen", filetypes=[("Bilder", "*.png *.jpg *.jpeg")])
        if not pfad:
            return
        settings.logo_ordner_anlegen()
        ordner = settings.TYPEN[self.TYP][0]
        name = os.path.basename(pfad)
        try:
            shutil.copyfile(pfad, os.path.join(settings.logo_ordner(self.TYP), name))  # Kopie: Original darf verschoben werden
        except (OSError, shutil.SameFileError) as e:
            messagebox.showerror("Logo", f"Logo konnte nicht gespeichert werden:\n{e}")
            return
        self.logos_laden()
        self.vars["logo"].set(ordner + "/" + name)

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
        for k in self.keys:
            self.vars[k].set(self.items[i].get(k, ""))
        self.anzahl.set(self.items[i]["anzahl"])

    # --- Vorschau + Druck ---
    def _bogen(self):
        """Schilder fuer den Bogen: die Liste, oder (leere Liste) das gerade eingetippte Schild."""
        alle = [it for it in self.items for _ in range(it["anzahl"])]
        if not alle and any(self.vars[k].get().strip() for k in self.keys):
            alle = [self._form_item()]
        return alle

    def _vorschau_planen(self):
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(250, self.vorschau)

    def blaettern(self, d):
        self.seite += d
        self.vorschau()

    def _text(self, msg):
        self.canvas.delete("all")
        self.canvas.create_text(10, 10, anchor="nw", text=msg, width=max(self.canvas.winfo_width() - 20, 100))

    def vorschau(self):
        self._job = None
        if pymupdf is None:
            self._text("Für die Vorschau fehlt das Paket pymupdf.\nInstallieren: pip3 install pymupdf")
            return
        alle = self._bogen()
        self.seiten_text.set("")
        if not alle:
            self._text("Noch keine Schilder. Felder ausfüllen, dann erscheint hier die Vorschau.")
            return
        w, h, rand, abstand = self.masse()
        try:
            buf = io.BytesIO()
            sheet.render_pdf(buf, w, h, alle, self.draw, rand, abstand)
            doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
        except ValueError as e:
            self._text(str(e))
            return
        self.seite = max(0, min(self.seite, len(doc) - 1))
        z = min(max(self.canvas.winfo_width(), 100) / sheet.PAGE_W, max(self.canvas.winfo_height(), 100) / sheet.PAGE_H)
        png = doc[self.seite].get_pixmap(matrix=pymupdf.Matrix(z, z)).tobytes("png")
        self._bild = tk.PhotoImage(data=base64.b64encode(png))  # Referenz halten, sonst raeumt Tk das Bild weg
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, 0, image=self._bild, anchor="n")
        self.seiten_text.set(f"Blatt {self.seite + 1} von {len(doc)}")

    def drucken(self):
        alle = self._bogen()
        if not alle:
            messagebox.showinfo("Drucken", "Die Liste ist leer.")
            return
        w, h, rand, abstand = self.masse()
        pfad = os.path.join(tempfile.gettempdir(), f"preisschilder_{self.TYP}.pdf")
        try:
            sheet.render_pdf(pfad, w, h, alle, self.draw, rand, abstand)
            pdf_oeffnen(pfad)
        except (ValueError, OSError) as e:
            messagebox.showerror("Drucken", str(e))

    @staticmethod
    def draw(c, w, h, item):
        raise NotImplementedError
