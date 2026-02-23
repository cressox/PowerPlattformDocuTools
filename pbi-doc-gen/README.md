# Power BI Documentation Generator

Interaktives CLI-Tool zur Erstellung standardisierter Markdown-Dokumentation für Power BI Reports.

## Features

- **Geführte Eingabe** – Schritt-für-Schritt-Abfrage aller Dokumentationsabschnitte
- **Mehrzeiliger Code-Input** – DAX und Power Query (M) einfach per Paste-Modus (`<<<` … `>>>`)
- **YAML-Datenspeicher** – Strukturierte Projektdatei (`data/project.yml`) mit Auto-Save
- **Inkrementelle Updates** – Abschnitte jederzeit ergänzen oder ändern, ohne Datenverlust
- **Markdown-Generierung** – Saubere, verlinkte Dokumentation mit Tabellen, Code-Fences und Ankern
- **Import/Export** – Measures und Queries aus einfachen Textdateien importieren
- **Deutsch** – Alle Überschriften und Labels in deutscher Sprache

## Voraussetzungen

- Python 3.11+ (funktioniert auch mit 3.9+)
- Optional: `pyyaml` (empfohlen) – ohne PyYAML wird JSON als Fallback verwendet

## Installation

```bash
# Repository klonen / Dateien kopieren
cd pbi-doc-gen

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Starten

**macOS / Linux:**
```bash
chmod +x run.sh
./run.sh
# oder direkt:
python3 -m src.main
```

**Windows (PowerShell):**
```powershell
.\run.ps1
# oder direkt:
python -m src.main
```

## Hauptmenü

```
┌──────────────────────────────────────────┐
│  Hauptmenü                               │
├──────────────────────────────────────────┤
│  1  Neues Projekt anlegen                │
│  2  Projekt-Metadaten bearbeiten         │
│  3  KPI hinzufügen                       │
│  4  Datenquelle hinzufügen               │
│  5  Power Query (M) dokumentieren        │
│  6  Datenmodell bearbeiten               │
│  7  Measure (DAX) hinzufügen             │
│  8  Berichtsseite / Visuals hinzufügen   │
│  9  Governance bearbeiten                │
│ 10  Änderungsprotokoll-Eintrag           │
│ 11  ▶ Dokumentation generieren           │
│ 12  Import / Export Helfer               │
│  0  Beenden                              │
└──────────────────────────────────────────┘
```

## Mehrzeiliger Input (DAX / Power Query)

Bei Code-Feldern `<<<` eingeben, um den Paste-Modus zu starten. Mehrzeiligen Code einfügen und mit `>>>` auf einer eigenen Zeile beenden:

```
  DAX-Code (Pflichtfeld, für Mehrzeiler <<<): <<<
  📋 Mehrzeiliger Modus – Einfügen und mit >>> auf eigener Zeile beenden:
  Total Sales =
  SUM( Sales[Amount] )
  >>>
```

## Generierte Dokumentation

Nach Auswahl von Menüpunkt **11** wird folgende Ordnerstruktur erstellt:

```
docs/
├── index.md                              ← Einstiegspunkt
├── 01_overview/
│   ├── overview.md
│   └── kpis.md
├── 02_data_sources/
│   └── data_sources.md
├── 03_power_query/
│   └── queries.md
├── 04_data_model/
│   └── data_model.md
├── 05_measures/
│   └── measures.md
├── 06_report_design/
│   └── pages_visuals.md
├── 07_governance/
│   ├── refresh_gateway_rls.md
│   └── assumptions_limitations.md
└── 08_change_log/
    └── change_log.md
```

## Import-Format für Measures

Textdatei mit folgendem Format:

```
MEASURE: Total Sales
FOLDER: Sales
DESCRIPTION: Sum of all sales
DAX:
Total Sales = SUM( Sales[Amount] )

MEASURE: Avg Sales
DAX:
Avg Sales = AVERAGE( Sales[Amount] )
```

## Import-Format für Queries

```
QUERY: qry_Sales
PURPOSE: Load sales data
OUTPUT: FactSales
M:
let
    Source = Sql.Database("server", "db"),
    Sales = Source{[Schema="dbo",Item="Sales"]}[Data]
in
    Sales
```

## Projektdatei

Alle Eingaben werden in `data/project.yml` gespeichert. Diese Datei kann auch manuell bearbeitet werden. Ein vorbefülltes Beispiel für einen HR-Zeitkontenbericht ist enthalten.

## Tests

```bash
python -m pytest tests/ -v
# oder:
python -m unittest tests/test_core.py -v
```

## Erweiterung

- Neue Abschnitte: Dataclass in `src/models.py` hinzufügen, Generator-Funktion in `src/generator.py` ergänzen, Prompt in `src/prompts.py` erstellen, Menüpunkt in `src/main.py` verdrahten.
- Templates: Die Generator-Funktionen können durch Jinja2-Templates ersetzt werden – die Strings in `generator.py` dienen als Ausgangspunkt.

## Lizenz

MIT
