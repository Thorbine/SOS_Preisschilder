"""Tab Einstellungen: Schildmasse, Seitenrand/-abstand, Programm-Update."""
import tkinter as tk
from tkinter import ttk, messagebox

import settings
import updater


class EinstellungenTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        s = settings.load()
        self.vars = {}

        masse = ttk.LabelFrame(self, text="Schildmaße (mm)", padding=10)
        masse.pack(fill="x")
        for r, (typ, (name, _, _)) in enumerate(settings.TYPEN.items()):
            ttk.Label(masse, text=name, width=14).grid(row=r, column=0, sticky="w", pady=3)
            for c, (key, label) in enumerate((("breite", "Breite"), ("hoehe", "Höhe"))):
                ttk.Label(masse, text=label).grid(row=r, column=1 + 2 * c, padx=(10, 4))
                self._feld(masse, (typ, key), s[typ][key]).grid(row=r, column=2 + 2 * c)

        seite = ttk.LabelFrame(self, text="Druckbogen A4 (mm)", padding=10)
        seite.pack(fill="x", pady=10)
        ttk.Label(seite, text="Seitenrand").grid(row=0, column=0, sticky="w", pady=3)
        self._feld(seite, ("rand",), s["rand"]).grid(row=0, column=1, padx=8)
        ttk.Label(seite, text="Abstand zwischen Schildern").grid(row=1, column=0, sticky="w", pady=3)
        self._feld(seite, ("abstand",), s["abstand"]).grid(row=1, column=1, padx=8)
        ttk.Label(seite, text="Abstand 0 = Schilder grenzen aneinander, eine Schnittlinie trennt zwei Schilder.",
                  foreground="gray").grid(row=2, column=0, columnspan=2, sticky="w")

        ttk.Button(self, text="Speichern", command=self.speichern).pack(anchor="w")

        upd = ttk.LabelFrame(self, text="Programm-Update", padding=10)
        upd.pack(fill="x", pady=14)
        self.status = tk.StringVar(value=f"Installierte Version: {updater.current_version()}")
        ttk.Label(upd, textvariable=self.status, wraplength=700, justify="left").pack(anchor="w")
        ttk.Button(upd, text="Nach Update suchen", command=self.update_suchen).pack(anchor="w", pady=(8, 0))

    def _feld(self, parent, pfad, wert):
        v = tk.StringVar(value=f"{wert:g}")
        self.vars[pfad] = v
        return ttk.Entry(parent, textvariable=v, width=8)

    def speichern(self):
        s = settings.load()
        try:
            for pfad, v in self.vars.items():
                zahl = float(v.get().replace(",", "."))
                if zahl < 0 or (len(pfad) == 2 and zahl <= 0):
                    raise ValueError
                if len(pfad) == 2:
                    s[pfad[0]][pfad[1]] = zahl
                else:
                    s[pfad[0]] = zahl
        except ValueError:
            messagebox.showwarning("Einstellungen", "Bitte nur positive Zahlen eintragen (Maße > 0).")
            return
        settings.save(s)
        messagebox.showinfo("Einstellungen", "Gespeichert.")

    def update_suchen(self):
        try:
            info = updater.check_for_update()
            if not info["neuer"]:
                self.status.set(f"Das Programm ist aktuell (Version {updater.current_version()}).")
                return
            if not messagebox.askyesno("Update", f"Neue Version {info['kurz']} gefunden:\n{info['notiz']}\n\nJetzt installieren? Das Programm startet danach neu."):
                return
            updater.install(info)
        except updater.UpdateError as e:
            messagebox.showerror("Update", str(e))
            return
        updater.restart()
