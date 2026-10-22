"""Tab Snowboard: gleiches Layout wie Ski, eigene Liste und eigene Schildmasse."""
from tab_ski import SkiTab


class SnowboardTab(SkiTab):
    TYP = "snowboard"
    FIELDS = [("marke", "Marke"), ("modell", "Modell"),
              ("laengen", "Längen (z. B. 150–158 cm)"), ("detail", "Zusatz (z. B. Rocker, Allmountain)"),
              ("preis", "Preis (€)"), ("statt", "Statt-Preis (€, optional)")]
