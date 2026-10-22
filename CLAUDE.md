# Preisschilder-Programm (SOS Sport Braunschweig)

Python 3 + Tkinter + reportlab, Mac und Windows. Ein Tab pro Schildtyp, Druck als A4-PDF (Rahmen = Schnittlinie).

## Aufbau
- Neuer Schildtyp: Eintrag in `settings.TYPEN`, Tab-Klasse nach Vorbild `tab_helme.py` (nur `FIELDS` + `draw()`), in `main.py` einhängen.
- `sheet.py` ist UI-frei und hat Tests: `python test_sheet.py`.
- Update: `updater.py` lädt das ZIP von `main` und ersetzt nur Programmdateien. Ordner `daten/` (Einstellungen, Listen) nie überschreiben.

## Arbeitsablauf
- Claude ändert, testet, pusht. Thorben startet das Update über Einstellungen > "Nach Update suchen".
- Das Update zieht den Stand von `main`. Änderungen erst nach `main`, wenn sie fertig sind.
- Keine `*_previous.py`/`*_v1.py` Kopien, der Git-Verlauf ist das Backup.
