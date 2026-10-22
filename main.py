"""
SOS Sport - Preisschilder
Tkinter-Programm fuer Mac und Windows. Pro Schildtyp ein Tab, Druck als A4-PDF.

Start: python3 main.py   (Mac: start.command, Windows: start.bat)
"""
import os
import traceback
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import settings
from tab_helme import HelmeTab
from tab_baelle import BaelleTab
from tab_einstellungen import EinstellungenTab


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SOS Sport – Preisschilder")
        self.geometry(f"{min(1280, self.winfo_screenwidth() - 40)}x{min(820, self.winfo_screenheight() - 80)}")
        self.minsize(1000, 640)
        self.report_callback_exception = self._on_error
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        nb.add(HelmeTab(nb), text="Helme")
        nb.add(BaelleTab(nb), text="Tennisbälle")
        nb.add(EinstellungenTab(nb), text="Einstellungen")

    def _on_error(self, exc, val, tb):
        text = "".join(traceback.format_exception(exc, val, tb))
        try:
            os.makedirs(settings.DATEN_DIR, exist_ok=True)
            with open(os.path.join(settings.DATEN_DIR, "fehlerprotokoll.txt"), "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.now():%Y-%m-%d %H:%M:%S} ---\n{text}\n")
        except OSError:
            pass
        messagebox.showerror("Fehler", f"Unerwarteter Fehler:\n{val}\n\nDetails: daten/fehlerprotokoll.txt")


if __name__ == "__main__":
    App().mainloop()
