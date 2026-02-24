# Power Automate Documentation Generator (PA Doc Gen)

Ein professionelles Desktop-Tool zur Dokumentation von Microsoft Power Automate Flows. Erstellt strukturierte Markdown-Dokumentation und PDF-Exporte mit CI-Branding.

## Features

- **Flow-JSON-Import**: Automatisches Parsen von Power Automate Flow-Exporten (Portal, Solution, ARM Template, Clipboard)
- **Hierarchische Aktionsansicht**: Baumdarstellung aller Aktionen mit Verschachtelung (Scope, Condition, Loops)
- **14 Dokumentationsseiten**: Dashboard, Metadaten, Trigger, Aktionen, Konnektoren, Variablen, Fehlerbehandlung, Datenmappings, SLA, Governance, Abhängigkeiten, Änderungsprotokoll, Vorschau
- **Markdown-Generierung**: Vollständige Dokumentation in strukturierten Ordnern
- **PDF-Export**: Professionelle PDF-Dokumente mit CI-Branding, Titelseite, Inhaltsverzeichnis
- **Dark Mode**: Durchgängiges dunkles Farbschema
- **Screenshot-Support**: Strg+V, Drag & Drop, Dateibrowser
- **Code-Editor**: Syntax-Highlighting für JSON und PA-Expressions
- **YAML-Speicherung**: Projektdaten in YAML (Fallback: JSON)

## Voraussetzungen

- Python 3.11+
- PySide6 (Qt6)
- ReportLab, PyYAML, Markdown, Pygments

## Installation

```bash
# Repository klonen
git clone <repository-url>
cd pa-doc-gen

# Abhängigkeiten installieren
pip install -r requirements.txt

# Starten
python src/gui.py
```

## Projektstruktur

```
pa-doc-gen/
├── src/
│   ├── models.py              # Datenmodell (Dataclasses)
│   ├── storage.py             # YAML/JSON Persistenz
│   ├── generator.py           # Markdown-Generierung
│   ├── pdf_export.py          # ReportLab PDF-Export
│   ├── flow_parser.py         # Flow-JSON-Parser
│   ├── gui.py                 # GUI Entry Point
│   └── ui/
│       ├── theme.py           # Dark-Mode Farbpalette + QSS
│       ├── widgets.py         # Custom Widgets
│       ├── preview.py         # Live Markdown-Vorschau
│       └── mainwindow.py      # Hauptfenster mit allen Seiten
├── data/
│   ├── project.yml            # Projektdaten
│   ├── screenshots/           # Screenshots
│   └── imports/               # Flow-JSON-Importe
├── docs/                      # Generierte Dokumentation
├── tests/
│   └── test_all.py            # 25 Unit-Tests
├── requirements.txt
└── README.md
```

## Datenmodell

Das Tool bildet folgende Entitäten ab:

| Entität | Beschreibung |
|---|---|
| **ProjectMeta** | Flow-Name, Typ, Status, Umgebungen, Lizenz |
| **FlowTrigger** | Trigger-Typ, Connector, Zeitplan, Schema |
| **FlowAction** | Hierarchische Aktionen mit Verschachtelung |
| **FlowConnection** | Konnektoren und Service-Accounts |
| **FlowVariable** | Variablen mit Typ und Initialwert |
| **ErrorHandling** | Try/Catch, Retry-Logik, Timeouts |
| **DataMapping** | Quell-/Ziel-Zuordnungen, Transformationen |
| **FlowSLA** | Laufzeiten, Kritikalität, Eskalation |
| **Governance** | DLP, Monitoring, Backup, Tests |
| **FlowDependency** | Abhängigkeiten zu Flows, Apps, APIs |
| **ChangeLogEntry** | Versionshistorie |
| **CIBranding** | Firmenfarben, Logo, Footer |

## Flow-JSON-Import

Der Parser unterstützt folgende Formate:

1. **Portal-Export** (`.zip` mit `definition.json`)
2. **Solution-Export** (`.zip` mit `Workflows/*.json`)
3. **Clipboard-JSON** (aus "Peek Code" kopiert, per Strg+V einfügbar)
4. **Logic App ARM Template**

Erkannte Aktionstypen:
- OpenApiConnection (SharePoint, Outlook, Teams, Dataverse, etc.)
- Compose, SetVariable, InitializeVariable
- Condition (If), Switch, Foreach, Until, Scope
- Http, HttpWebhook, Response, Terminate, Wait, Delay

### Import-Workflow

1. Klick auf "Flow-JSON importieren" oder Strg+I
2. JSON-Datei wählen oder JSON aus Zwischenablage einfügen
3. Vorschau: Erkannte Trigger, Aktionen, Konnektoren
4. Option: Bestehende Daten überschreiben oder zusammenführen

## Generierte Dokumentation

### Markdown-Ordnerstruktur

```
docs/
├── index.md
├── 01_overview/
│   ├── overview.md
│   └── trigger.md
├── 02_flow_structure/
│   ├── actions.md
│   ├── variables.md
│   └── data_mappings.md
├── 03_connections/
│   ├── connectors.md
│   └── dependencies.md
├── 04_error_handling/
│   └── error_handling.md
├── 05_governance/
│   ├── sla_performance.md
│   └── governance_operations.md
└── 06_change_log/
    └── change_log.md
```

### PDF-Export

- Titelseite mit Logo und CI-Farben
- Inhaltsverzeichnis
- Alle Sektionen mit professionellen Tabellen
- Aktionshierarchie als eingerückte Tabelle
- Code-Blöcke für Expressions und JSON-Schemas
- Seitenzahlen und CI-Header/Footer

## Tastenkürzel

| Kürzel | Funktion |
|---|---|
| Strg+S | Projekt speichern |
| Strg+I | Flow-JSON importieren |
| Strg+V | Screenshot/JSON einfügen |

## Tests

```bash
cd pa-doc-gen
python -m pytest tests/ -v
```

25 Unit-Tests decken ab:
- Datenmodell (Erstellung, Enums, Hierarchie, IDs)
- Speicherung (YAML Save/Load, Roundtrip)
- Parser (Formaterkennung, Trigger, Aktionen, Variablen, Konnektoren, Expressions)
- Generierung (Markdown-Output, Aktionsbaum, Index-Links)
- PDF-Export (Grundfunktionalität)

## Konfiguration

### Dark Mode

Die Farbpalette ist in `src/ui/theme.py` definiert:

- `BG_BASE`: #0F1117
- `ACCENT`: #5B8DEF
- `SUCCESS`: #4CAF50
- `WARNING`: #E0A526
- `ERROR`: #EF5B5B

### CI-Branding

Über die "CI / Branding"-Seite konfigurierbar:
- Firmenname und Logo
- Primär-, Akzent- und Sekundärfarbe
- Header- und Footer-Text
- Vertraulichkeitsvermerk

## Cross-Platform

Getestet auf:
- Windows 10/11
- macOS 12+
- Ubuntu 22.04+

## Lizenz

Intern – Alle Rechte vorbehalten.
