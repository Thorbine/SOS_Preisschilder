"""A4-Bogen mit moeglichst vielen Schildern (reportlab). Keine Oberflaeche.

Jedes Schild bekommt einen Rahmen - der gilt beim Ausschneiden als Schnittlinie.
Das Layout eines Schildes steckt allein in der Funktion draw(c, w, h, item),
die der jeweilige Tab liefert (Koordinaten in Punkt, Ursprung links unten)."""
import os

import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = A4  # Punkt


def _anzahl(platz, groesse, abstand):
    # n Schilder brauchen n*groesse + (n-1)*abstand
    return max(0, int((platz + abstand + 1e-6) // (groesse + abstand)))


def grid(w_mm, h_mm, rand_mm, abstand_mm):
    """-> (Spalten, Zeilen, gedreht). Probiert das Schild auch um 90 Grad gedreht
    und nimmt die Variante mit mehr Schildern pro Blatt."""
    nutz_w = PAGE_W / mm - 2 * rand_mm
    nutz_h = PAGE_H / mm - 2 * rand_mm
    normal = (_anzahl(nutz_w, w_mm, abstand_mm), _anzahl(nutz_h, h_mm, abstand_mm), False)
    gedreht = (_anzahl(nutz_w, h_mm, abstand_mm), _anzahl(nutz_h, w_mm, abstand_mm), True)
    best = max(normal, gedreht, key=lambda g: g[0] * g[1])
    if best[0] * best[1] == 0:
        raise ValueError(f"Ein Schild von {w_mm:g} × {h_mm:g} mm passt nicht auf A4 (Rand {rand_mm:g} mm).")
    return best


def pro_blatt(w_mm, h_mm, rand_mm, abstand_mm):
    sp, ze, _ = grid(w_mm, h_mm, rand_mm, abstand_mm)
    return sp * ze


def render_pdf(pfad, w_mm, h_mm, items, draw, rand_mm=10, abstand_mm=0):
    """Schreibt alle items (ein Eintrag = ein Schild) auf A4-Seiten."""
    if not items:
        raise ValueError("Keine Schilder zum Drucken.")
    sp, ze, gedreht = grid(w_mm, h_mm, rand_mm, abstand_mm)
    zw, zh = (h_mm, w_mm) if gedreht else (w_mm, h_mm)  # Zelle auf dem Papier
    # Raster zentrieren, damit der Drucker-Randbereich links/rechts gleich ist
    x0 = (PAGE_W - (sp * zw + (sp - 1) * abstand_mm) * mm) / 2
    y_oben = PAGE_H - (PAGE_H - (ze * zh + (ze - 1) * abstand_mm) * mm) / 2
    c = canvas.Canvas(pfad, pagesize=A4)
    c.setTitle("Preisschilder")
    for i, item in enumerate(items):
        pos = i % (sp * ze)
        if i and pos == 0:
            c.showPage()
        x = x0 + (pos % sp) * (zw + abstand_mm) * mm
        y = y_oben - ((pos // sp) + 1) * zh * mm - (pos // sp) * abstand_mm * mm
        c.saveState()
        if gedreht:
            c.translate(x + zw * mm, y)
            c.rotate(90)
        else:
            c.translate(x, y)
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(0, 0, w_mm * mm, h_mm * mm)
        draw(c, w_mm * mm, h_mm * mm, item)
        c.restoreState()
    c.save()


def fit_font_size(text, font, max_size, max_breite, min_size=5):
    """Groesste Schriftgroesse <= max_size, bei der text in max_breite passt."""
    size = max_size
    while size > min_size and stringWidth(text, font, size) > max_breite:
        size -= 0.5
    return size


def draw_logo(c, name, x, y, w, h):
    """Logo (Datei aus daten/logos) proportional in die Box x,y,w,h, rechtsbuendig/oben.
    Fehlende oder defekte Datei: Schild wird ohne Logo gedruckt."""
    if not name:
        return
    try:
        c.drawImage(os.path.join(settings.LOGO_DIR, name), x, y, w, h,
                    preserveAspectRatio=True, mask="auto", anchor="ne")
    except Exception:
        pass


def euro(text):
    """'199,9' / '199.90' / '199,95 €' -> '199,90 €'. Nicht lesbar -> Text unveraendert."""
    roh = (text or "").replace("€", "").replace("EUR", "").strip().replace(",", ".")
    try:
        return f"{float(roh):.2f}".replace(".", ",") + " €"
    except ValueError:
        return (text or "").strip()
