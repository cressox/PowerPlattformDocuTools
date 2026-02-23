# Measures (DAX)

| # | Name | Ordner | Beschreibung |
|---|---|---|---|
| 1 | [Aufbau Stunden](#aufbau-stunden) | Zeitkonto | Summe der aufgebauten Überstunden |
| 2 | [Abbau Stunden](#abbau-stunden) | Zeitkonto | Summe der abgebauten Überstunden |
| 3 | [Saldo Stunden](#saldo-stunden) | Zeitkonto | Kumulierter Saldo (Aufbau – Abbau) bis zum ausgewählten Zeitpunkt |
| 4 | [Saldo Vorwoche](#saldo-vorwoche) | Zeitkonto | Saldo der Vorwoche für Vergleichszwecke |
| 5 | [t](#t) | t | t |

## Aufbau Stunden

**Ordner:** Zeitkonto

**Beschreibung:** Summe der aufgebauten Überstunden

**DAX-Code:**

```dax
Aufbau Stunden =
SUM( FactZeitkonto[AufbauStunden] )

```

**Abhängigkeiten:** FactZeitkonto[AufbauStunden]

**Filter-/Kontextverhalten:** Reagiert auf alle Slicer (Datum, Abteilung, Person).

**Validierung:** Vergleich mit SAP-Standardreport PT_BAL00.

---

## Abbau Stunden

**Ordner:** Zeitkonto

**Beschreibung:** Summe der abgebauten Überstunden

**DAX-Code:**

```dax
Abbau Stunden =
SUM( FactZeitkonto[AbbauStunden] )

```

**Abhängigkeiten:** FactZeitkonto[AbbauStunden]

---

## Saldo Stunden

**Ordner:** Zeitkonto

**Beschreibung:** Kumulierter Saldo (Aufbau – Abbau) bis zum ausgewählten Zeitpunkt

**DAX-Code:**

```dax
Saldo Stunden =
CALCULATE(
    [Aufbau Stunden] - [Abbau Stunden],
    FILTER(
        ALL( DimDatum ),
        DimDatum[YearWeekKey] <= MAX( DimDatum[YearWeekKey] )
    )
)

```

**Abhängigkeiten:** [Aufbau Stunden], [Abbau Stunden], DimDatum[YearWeekKey]

**Filter-/Kontextverhalten:** Verwendet ALL(DimDatum) für kumulative Berechnung. Abteilungs-/Personen-Filter bleiben aktiv.

**Validierung:** Stichprobenweise Prüfung gegen SAP-Saldoübersicht.

---

## Saldo Vorwoche

**Ordner:** Zeitkonto

**Beschreibung:** Saldo der Vorwoche für Vergleichszwecke

**DAX-Code:**

```dax
Saldo Vorwoche =
CALCULATE(
    [Saldo Stunden],
    FILTER(
        ALL( DimDatum ),
        DimDatum[YearWeekKey] =
            MAXX( FILTER( ALL( DimDatum ), DimDatum[YearWeekKey] < MAX( DimDatum[YearWeekKey] ) ),
                  DimDatum[YearWeekKey] )
    )
)

```

**Abhängigkeiten:** [Saldo Stunden], DimDatum[YearWeekKey]

**Filter-/Kontextverhalten:** Berechnet Saldo für die KW vor der aktuell ausgewählten KW.

---

## t

**Ordner:** t

**Beschreibung:** t

**DAX-Code:**

```dax
t
```

**Abhängigkeiten:** t

**Filter-/Kontextverhalten:** t

**Validierung:** t

---
