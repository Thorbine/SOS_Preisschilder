"""Programm-Update aus dem oeffentlichen GitHub-Repository (Mac und Windows).

Ablauf: neuesten Stand von "main" abfragen -> ZIP laden und pruefen -> nur
Programmdateien (*.py, requirements.txt, README.md, Startdateien) ueber den
Programmordner kopieren -> Programm neu starten. Der Ordner "daten"
(Einstellungen, Schilderlisten) wird nie angefasst."""
import io
import json
import os
import shutil
import sys
import urllib.request
import zipfile

from settings import APP_DIR

REPO = "Thorbine/SOS_Preisschilder"
API_COMMIT = f"https://api.github.com/repos/{REPO}/commits/main"
ZIP_URL = f"https://github.com/{REPO}/archive/refs/heads/main.zip"
VERSION_FILE = os.path.join(APP_DIR, "version.txt")
TIMEOUT = 20
UPDATE_DATEIEN = {"requirements.txt", "README.md", "start.command", "start.bat"}


class UpdateError(Exception):
    pass


def current_version():
    try:
        with open(VERSION_FILE, encoding="utf-8") as f:
            return f.read().strip() or "dev"
    except OSError:
        return "dev"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SOS-Preisschilder-Update"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def check_for_update():
    """-> {'sha', 'kurz', 'notiz', 'neuer'}"""
    try:
        data = json.loads(_get(API_COMMIT).decode("utf-8"))
        sha = data["sha"]
        notiz = data["commit"]["message"].splitlines()[0]
    except Exception as e:
        raise UpdateError(f"Keine Verbindung zu GitHub oder noch keine Version veröffentlicht ({e}).")
    return {"sha": sha, "kurz": sha[:7], "notiz": notiz, "neuer": sha[:7] != current_version()}


def _ist_programmdatei(name):
    return "/" not in name and (name.endswith(".py") or name in UPDATE_DATEIEN)


def install(info):
    """Laedt das ZIP und ersetzt die Programmdateien. Erst alles pruefen, dann kopieren."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(_get(ZIP_URL)))
    except Exception as e:
        raise UpdateError(f"Download fehlgeschlagen: {e}")
    wurzel = zf.namelist()[0].split("/")[0] + "/"
    dateien = {n[len(wurzel):]: n for n in zf.namelist() if _ist_programmdatei(n[len(wurzel):])}
    if "main.py" not in dateien or zf.testzip() is not None:
        raise UpdateError("Das heruntergeladene Update ist unvollständig.")
    inhalte = {name: zf.read(n) for name, n in dateien.items()}
    for name, inhalt in inhalte.items():
        ziel = os.path.join(APP_DIR, name)
        tmp = ziel + ".neu"
        with open(tmp, "wb") as f:
            f.write(inhalt)
        if os.path.exists(ziel):
            shutil.copymode(ziel, tmp)  # start.command bleibt ausführbar
        os.replace(tmp, ziel)
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(info["kurz"])


def restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)
