"""Import der Helme aus der Warenwirtschafts-CSV (Semikolon, Windows-Kodierung). Keine Oberflaeche.

Pro Hersteller und Modell ein Schild (Farben und Artikelnummern fallen weg). Groesse und Masse stehen nicht
in der CSV und werden im Programm ergaenzt. Spalten: Herst.kurz = Hersteller, H.-Art.-Nr. = Modellname,
SVK-P = Preis, RVK-P = reduzierter Preis, Saison = z. B. "H/W 2026"."""
import csv
import os
import re

IGNORIERT = {"SOSSPO"}  # eigene Mietartikel (RTL Helm), brauchen kein Schild
GROSS_BLEIBT = {"MIPS", "QV", "LT", "GT", "HD", "RTL", "SL", "BC", "Q", "XL", "XS", "LED", "MOD"}


def schoener_name(name):
    """Nur komplett GROSSGESCHRIEBENE Namen werden zu "Alto Q-Lite"; Kuerzel wie MIPS bleiben gross."""
    name = " ".join(name.split())
    if not name.isupper():
        return name
    return re.sub(r"[A-Za-zÄÖÜ]+", lambda m: m.group(0) if m.group(0) in GROSS_BLEIBT else m.group(0).capitalize(), name)


def preis_text(text):
    """'180,00' -> '180', '149,50' -> '149,50'; leer -> ''."""
    t = (text or "").strip().replace(".", "")
    if not t:
        return ""
    try:
        zahl = float(t.replace(",", "."))
    except ValueError:
        return ""
    return str(int(zahl)) if zahl == int(zahl) else f"{zahl:.2f}".replace(".", ",")


def logo_fuer(hersteller, logos):
    """Logo, dessen Dateiname mit dem (evtl. abgeschnittenen) Herstellernamen beginnt, z. B. SALOMO -> Salomon.
    Bei mehreren gewinnt der kuerzeste Name ("Salomon" vor "Salomon Schriftzug")."""
    h = hersteller.strip().lower()
    treffer = [l for l in logos if h and os.path.splitext(os.path.basename(l))[0].lower().startswith(h)]
    return min(treffer, key=lambda l: len(os.path.basename(l)), default="")


def _lesen(pfad):
    for kodierung in ("utf-8-sig", "cp1252"):
        try:
            with open(pfad, encoding=kodierung, newline="") as f:
                return list(csv.reader(f, delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise ValueError("Die Datei konnte nicht gelesen werden (Kodierung).")


def _saison_jahr(text):
    m = re.search(r"\d{4}", text or "")
    return int(m.group()) if m else 0


def lese_helme(pfad, logos):
    """-> Liste von Schildern (dict wie im Reiter Helme), je Hersteller + Modell eines."""
    zeilen = _lesen(pfad)
    if not zeilen:
        return []
    kopf = {n.strip(): i for i, n in enumerate(zeilen[0])}
    fehlt = [n for n in ("Herst.kurz", "H.-Art.-Nr.", "SVK-P") if n not in kopf]
    if fehlt:
        raise ValueError("Das ist nicht die Helm-CSV, es fehlen die Spalten: " + ", ".join(fehlt))
    gruppen = {}
    for z in zeilen[1:]:
        if len(z) <= max(kopf["Herst.kurz"], kopf["H.-Art.-Nr."], kopf["SVK-P"]):
            continue
        hersteller, modell = z[kopf["Herst.kurz"]].strip(), z[kopf["H.-Art.-Nr."]].strip()
        if hersteller and modell and hersteller.upper() not in IGNORIERT:
            gruppen.setdefault((hersteller, re.sub(r"\s+", "", modell).lower()), []).append(z)
    items = []
    for (hersteller, _), zs in gruppen.items():
        neu = max(zs, key=lambda z: _saison_jahr(z[kopf["Saison"]]) if "Saison" in kopf else 0)  # neueste Saison
        preis, statt = preis_text(neu[kopf["SVK-P"]]), ""
        rvk = [preis_text(z[kopf["RVK-P"]]) for z in zs] if "RVK-P" in kopf else []
        if rvk and all(rvk):  # alle Farben reduziert -> Preis reduziert, alter Preis als Statt-Preis
            preis, statt = min(rvk, key=lambda p: float(p.replace(",", "."))), preis
        items.append({"logo": logo_fuer(hersteller, logos), "modell": schoener_name(neu[kopf["H.-Art.-Nr."]]),
                      "groesse1": "", "mass1": "", "preis": preis, "statt": statt, "anzahl": 1, "druck": False})
    return items


def zusammenfuehren(vorhanden, neu):
    """Haengt neue Schilder an, die es (gleiches Logo + gleicher Modellname) noch nicht gibt. -> Anzahl neu."""
    def schluessel(it):
        return it.get("logo", ""), re.sub(r"\s+", "", it.get("modell", "")).lower()
    bekannt = {schluessel(it) for it in vorhanden}
    dazu = []
    for it in neu:
        if schluessel(it) not in bekannt:
            bekannt.add(schluessel(it))
            dazu.append(it)
    vorhanden.extend(dazu)
    return len(dazu)
