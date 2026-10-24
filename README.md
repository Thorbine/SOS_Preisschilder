# SOS Sport – Preisschilder

Preisschilder für Helme und Tennisbälle erstellen und auf A4 drucken (so viele Schilder wie möglich pro Blatt, der Rahmen ist die Schnittlinie).

## Mac: einmalig einrichten
(Ohne Terminalfenster: Python installieren, dann `Preisschilder.app` im Programmordner doppelklicken, beim ersten Mal Rechtsklick → Öffnen und den Zugriff auf den Ordner erlauben. Die App lässt sich ins Dock ziehen.)
1. Python von https://www.python.org/downloads/ installieren (bringt Tkinter mit).
2. Auf GitHub **Code → Download ZIP**, entpacken.
3. Im Ordner `start.command` einmal im Terminal ausführbar machen: `chmod +x start.command`, danach Doppelklick (beim ersten Mal Rechtsklick → Öffnen).

## Windows
`start.bat` doppelklicken (Python muss installiert sein). Das Programm startet ohne Konsolenfenster.

## Logos
Logos (PNG/JPG) in den Ordner `daten/logos/<Produkt>` legen, z. B. `daten/logos/Helme`. Im Programm erscheinen sie als Kacheln zum Anklicken, „Ordner öffnen“ springt direkt dorthin. Logos direkt in `daten/logos` erscheinen bei allen Produkten.

## Schilder zusammenstellen
Alle Schilder bleiben pro Reiter gespeichert. In der Zeile eines Schilds legt „+“ ein Schild aufs Blatt, „−“ nimmt eines weg; die Spalte „Blatt“ zeigt die Stückzahl, die Zeile färbt sich grün. Die Blatt-Auswahl wird nicht gespeichert, beim Start ist das Blatt leer („Blatt leeren“ setzt alles auf null). Die Reihenfolge der Liste ist die Reihenfolge auf dem Blatt: mit ▲ ▼ verschieben oder über „Sortieren“ ordnen. Die Vorschau rechts zeigt sofort das Blatt.

## Helme aus der CSV importieren
Reiter Helme → „Helme aus CSV importieren…“ → `Helme.csv` wählen. Je Hersteller und Modell entsteht ein Schild (Farben fallen weg) mit Logo, Modell und Preis. Die neuen Schilder haben keine Größe und sind nicht auf dem Blatt. Größe und Maße ergänzen, für weitere Größen den Knopf „Kopieren“ nutzen. Ein erneuter Import legt nur neue Modelle an.

## Drucken
„Drucken (PDF)“ erzeugt ein A4-PDF und öffnet es. Dort drucken mit **100 % / „Tatsächliche Größe“** (nicht „An Seite anpassen“), sonst stimmen die Maße nicht.

## Update
Einstellungen → „Nach Update suchen“. Eigene Einstellungen und Listen (Ordner `daten`) bleiben erhalten.
