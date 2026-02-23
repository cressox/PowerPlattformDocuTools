# KPIs & Kennzahlen

| # | Name | Granularität | Beschreibung |
|---|---|---|---|
| 1 | Aufbau (Stunden) | ISO-Woche / Person | Gesamte aufgebaute Überstunden eines Mitarbeiters in der Betrachtungsperiode. |
| 2 | Abbau (Stunden) | ISO-Woche / Person | Gesamte abgebaute Überstunden (Gleitzeit, Freizeitausgleich) in der Periode. |
| 3 | Saldo (Stunden) | ISO-Woche / Person | Aktueller Überstundensaldo = kumulierter Aufbau minus kumulierter Abbau. |

## Aufbau (Stunden)

**Fachliche Beschreibung:** Gesamte aufgebaute Überstunden eines Mitarbeiters in der Betrachtungsperiode.

**Technische Definition:** SUM(FactZeitkonto[AufbauStunden]) – aggregiert pro Person und ISO-Woche.

**Granularität:** ISO-Woche / Person

**Filter / Kontext:** Kann nach Abteilung, Kostenstelle, Standort gefiltert werden.

**Einschränkungen / Hinweise:** Enthält keine Reisezeiten; Werte aus SAP HR können 1–2 Tage verzögert sein.

---

## Abbau (Stunden)

**Fachliche Beschreibung:** Gesamte abgebaute Überstunden (Gleitzeit, Freizeitausgleich) in der Periode.

**Technische Definition:** SUM(FactZeitkonto[AbbauStunden]) – aggregiert pro Person und ISO-Woche.

**Granularität:** ISO-Woche / Person

**Filter / Kontext:** Kann nach Abteilung, Kostenstelle, Standort gefiltert werden.



---

## Saldo (Stunden)

**Fachliche Beschreibung:** Aktueller Überstundensaldo = kumulierter Aufbau minus kumulierter Abbau.

**Technische Definition:** Laufende Summe: CALCULATE(SUM(FactZeitkonto[AufbauStunden]) - SUM(FactZeitkonto[AbbauStunden]), FILTER(ALL(DimDatum), DimDatum[ISOWoche] <= MAX(DimDatum[ISOWoche])))

**Granularität:** ISO-Woche / Person

**Filter / Kontext:** Stichtag-abhängig; bei Filterwechsel ändert sich der kumulative Saldo.

**Einschränkungen / Hinweise:** Korrekturbuchungen aus Vormonaten können den Saldo rückwirkend verändern.

---
