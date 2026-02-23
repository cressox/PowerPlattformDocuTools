# Datenmodell

## Tabellen

| Tabelle | Typ | Schlüssel | Beschreibung |
|---|---|---|---|
| FactZeitkonto | Fakt | PK: PersonalNr + Buchungsdatum | Zeitkontobuchungen pro Mitarbeiter und Tag |
| DimDatum | Dimension | PK: YearWeekKey | Kalender-Dimension mit ISO-Wochen |
| DimMitarbeiter | Dimension | PK: PersonalNr | Mitarbeiter-Stammdaten aus SAP HR |
| DimAbteilung | Dimension | PK: AbteilungID | Organisationseinheiten / Abteilungen |

## Beziehungen

| Von (Tabelle.Spalte) | Nach (Tabelle.Spalte) | Kardinalität | Filterrichtung |
|---|---|---|---|
| FactZeitkonto.YearWeekKey | DimDatum.YearWeekKey | N:1 | Single |
| FactZeitkonto.PersonalNr | DimMitarbeiter.PersonalNr | N:1 | Single |
| DimMitarbeiter.AbteilungID | DimAbteilung.AbteilungID | N:1 | Single |

## Datumslogik

ISO-Wochennummern nach DIN/ISO 8601. Woche beginnt am Montag. YearWeekKey = Jahr * 100 + ISOWoche (z.B. 202523 = Woche 23, 2025). Achtung: Kalenderwochen am Jahreswechsel (KW 52/53 → KW 1) müssen mit ISO-Jahr abgeglichen werden.

## Screenshots

![Datenmodell](images/data_model_screenshot.png)

## Anmerkungen

Star-Schema mit FactZeitkonto als zentraler Fakttabelle.
