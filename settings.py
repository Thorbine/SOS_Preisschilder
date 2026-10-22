"""Einstellungen und gespeicherte Schilderlisten (JSON im Ordner "daten").

"daten" gehoert dem Benutzer: das Programm-Update fasst den Ordner nie an."""
import json
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATEN_DIR = os.path.join(APP_DIR, "daten")

# Typ -> (Anzeigename, Breite mm, Hoehe mm). Neuer Schildtyp = neuer Eintrag + Tab.
TYPEN = {
    "helme": ("Helme", 100, 60),
    "baelle": ("Tennisbälle", 70, 40),
}
DEFAULTS = {"rand": 10, "abstand": 0, **{k: {"breite": b, "hoehe": h} for k, (_, b, h) in TYPEN.items()}}


LOGO_DIR = os.path.join(DATEN_DIR, "logos")


def logos():
    """Dateinamen der gespeicherten Logos (sortiert)."""
    try:
        return sorted(f for f in os.listdir(LOGO_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    except OSError:
        return []


def _pfad(name):
    return os.path.join(DATEN_DIR, name + ".json")


def _lesen(name, default):
    try:
        with open(_pfad(name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _schreiben(name, daten):
    os.makedirs(DATEN_DIR, exist_ok=True)
    tmp = _pfad(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _pfad(name))  # nie eine halb geschriebene Datei zurücklassen


def load():
    """Gespeicherte Einstellungen ueber den Defaults (fehlende Werte werden ergaenzt)."""
    s = _lesen("einstellungen", {})
    out = {"rand": s.get("rand", DEFAULTS["rand"]), "abstand": s.get("abstand", DEFAULTS["abstand"])}
    for k in TYPEN:
        out[k] = {**DEFAULTS[k], **(s.get(k) or {})}
    return out


def save(s):
    _schreiben("einstellungen", s)


def load_list(typ):
    return _lesen("liste_" + typ, [])


def save_list(typ, items):
    _schreiben("liste_" + typ, items)
