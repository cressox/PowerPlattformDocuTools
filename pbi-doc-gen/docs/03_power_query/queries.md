# Power Query (M) – Abfragen

## qry_FactZeitkonto

**Zweck:** Zeitkontodaten aus SAP HANA laden und bereinigen

**Eingaben:** SAP HANA View V_ZEITKONTEN

**Wichtige Transformationen:** Filterung auf aktive Mitarbeiter, Typumwandlung Datumsspalten, Berechnung der ISO-Woche über Date.WeekOfYear, Entfernung von Testdatensätzen.

**Ausgabetabelle:** `FactZeitkonto`

**M-Code:**

```powerquery
let
    Source = SapHana.Database("redacted-host:0000", [Implementation="2.0"]),
    Schema = Source{[Schema="HR_REPORTING"]}[Data],
    View = Schema{[Name="V_ZEITKONTEN"]}[Data],
    FilterActive = Table.SelectRows(View, each [Status] = "A"),
    AddISOWeek = Table.AddColumn(FilterActive, "ISOWoche",
        each Date.WeekOfYear([Buchungsdatum], Day.Monday), Int64.Type),
    AddYearWeekKey = Table.AddColumn(AddISOWeek, "YearWeekKey",
        each Date.Year([Buchungsdatum]) * 100 + [ISOWoche], Int64.Type)
in
    AddYearWeekKey

```

**Hinweise:** Join mit DimDatum über YearWeekKey; Join mit DimMitarbeiter über PersonalNr.

---

## qry_DimDatum

**Zweck:** Datumsdimensionstabelle mit ISO-Wochen generieren

**Eingaben:** Generiert (kein externer Input)

**Wichtige Transformationen:** Kalender von 2020-01-01 bis 2026-12-31, ISO-Wochennummer, ISO-Jahr, Quartal, Monatsname (deutsch).

**Ausgabetabelle:** `DimDatum`

**M-Code:**

```powerquery
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1,0,0,0)),
    ToTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Datum"}),
    TypeDate = Table.TransformColumnTypes(ToTable, {{"Datum", type date}}),
    AddISOWeek = Table.AddColumn(TypeDate, "ISOWoche",
        each Date.WeekOfYear([Datum], Day.Monday), Int64.Type),
    AddYear = Table.AddColumn(AddISOWeek, "Jahr",
        each Date.Year([Datum]), Int64.Type),
    AddYearWeekKey = Table.AddColumn(AddYear, "YearWeekKey",
        each [Jahr] * 100 + [ISOWoche], Int64.Type)
in
    AddYearWeekKey

```

---

## test

**Zweck:** test

**Eingaben:** test

**Wichtige Transformationen:** test
test
test

**Ausgabetabelle:** `test`

**M-Code:**

```powerquery
test
```

**Hinweise:** test

---
