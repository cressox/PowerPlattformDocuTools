# Power BI Documentation Generator v3 – Dark Mode GUI

Professionelles Desktop-Tool zur Erstellung standardisierter Power BI Dokumentation.
Dark-Mode GUI mit Syntax-Highlighting, Screenshot-Support, Live-Vorschau und PDF-Export.

## Features

- **Dark Mode GUI** – PySide6, durchgehend dunkles Design
- **Syntax-Highlighted Code-Editor** – DAX/M/SQL Keywords, Strings, Kommentare farbig
- **Strg+V ueberall** – Code, Screenshots, Text direkt einfuegbar
- **Screenshot-Support** – Per Drag and Drop, Dateibrowser oder Zwischenablage (Strg+V); Thumbnails inline
- **Live-Vorschau** – Generierte Doku als HTML-Preview + Raw Markdown nebeneinander
- **CI/Branding** – Firmenname, Logo, Farben, Footer/Header, Vertraulichkeitsvermerk
- **PDF-Export** – Ein-Klick PDF mit Titelseite, Tabellen, Code-Bloecken, Seitenzahlen
- **Markdown-Generierung** – Verlinkte Ordnerstruktur unter /docs
- **CLI weiterhin verfuegbar** – python -m src.main

## Architektur

```
pbi-doc-gen/
  src/
    models.py              Dataclasses inkl. CIBranding + Screenshot
    storage.py             YAML/JSON Persistence
    generator.py           Markdown-Generierung
    pdf_export.py          ReportLab PDF-Export
    gui.py                 Entry-Point fuer GUI
    ui/
      __init__.py
      theme.py             Dark-Mode Farbpalette + globales QSS
      widgets.py           CodeEditor, ScreenshotPanel, Sidebar, FormPage, ListEditorPage
      preview.py           Live-Vorschau (Markdown zu HTML)
      mainwindow.py        MainWindow + alle Seiten-Klassen
    main.py                CLI Entry-Point
    prompts.py             CLI Interactive Prompts
    importers.py           Text-Import/Export
  data/
    project.yml            Projektdaten
    screenshots/           Gespeicherte Screenshots
  docs/                    Generierte Markdown-Ausgabe
  tests/
    test_core.py           Core-Tests (Models, Storage, Generator)
    test_pdf.py            PDF-Export-Tests
  requirements.txt
```

## Installation

```bash
cd pbi-doc-gen
pip install -r requirements.txt
```

Voraussetzungen: Python 3.11+, Windows/macOS/Linux

## GUI starten

```bash
python -m src.gui
```

## CLI starten

```bash
python -m src.main
```

## GUI-Navigation (12 Seiten)

| Seite | Beschreibung |
|---|---|
| Dashboard | Projektuebersicht, Statistik-Karten, Oeffnen/Neu |
| Metadaten | Berichtsname, Eigentuemer, Umgebungen, URLs |
| CI / Branding | Firmenname, Logo, Farben (Color Picker), Footer, Vertraulichkeit |
| KPIs | KPI-Definitionen mit fachlicher + technischer Beschreibung |
| Datenquellen | Verbindungen, Gateways, Aktualisierungszyklen |
| Power Query | M-Abfragen mit Syntax-Highlighted Code-Editor |
| Datenmodell | Tabellen, Beziehungen, Datumslogik + Screenshot-Panel |
| Measures | DAX-Measures mit Syntax-Highlighted Code-Editor |
| Berichtsseiten | Seiten, Visuals, Slicer + Screenshot-Panel |
| Governance | Refresh, RLS, Performance, Annahmen, Einschraenkungen |
| Aenderungen | Versionsverlauf mit Auswirkungsgrad |
| Vorschau | Live HTML-Rendering + Raw Markdown Side-by-Side |

## CI/Branding fuer Kunden

Die CI-Seite erlaubt kundenspezifische Anpassungen:

- **Firmenname** – Erscheint in PDF-Header und Footer
- **Logo** – Firmenlogo auf der PDF-Titelseite
- **3 Farben** – Primaer, Akzent, Sekundaer per Color-Picker
- **Footer/Header-Text** – Auf jeder PDF-Seite
- **Cover-Untertitel** – Statt "Dokumentation" z.B. "Technische Spezifikation"
- **Vertraulichkeitsvermerk** – z.B. "Nur fuer internen Gebrauch"
- **Schriftart** – Optional: Custom Font Name

Alle Einstellungen werden im YAML gespeichert und beim PDF-Export angewendet.

## Screenshot-Workflow

Screenshots koennen auf 3 Wegen hinzugefuegt werden:

1. **Strg+V** – Screenshot im Snipping Tool machen, dann Strg+V im Screenshot-Panel
2. **Drag and Drop** – Bilddateien auf das Panel ziehen
3. **Dateibrowser** – Button "Bild waehlen" klicken

Bilder werden automatisch nach data/screenshots/ kopiert und als Thumbnail angezeigt.
Verfuegbar auf: Datenmodell-Seite, Berichtsseiten-Seite.

## Vorschau-Modus

Die Vorschau-Seite zeigt:

- **Links**: Gerendertes HTML mit Dark-Mode Styling (Tabellen, Code-Bloecke, Headings)
- **Rechts**: Raw Markdown zum Kopieren
- **Abschnitt-Dropdown**: Einzelne Sektionen waehlen
- **Alle Abschnitte**: Komplette Doku auf einen Blick

## Code-Editor Features

- Syntax-Highlighting fuer DAX, M (Power Query) und SQL
- Keywords in Lila, Strings in Gruen, Zahlen in Orange, Kommentare in Grau
- Monospace-Font (Cascadia Code / Consolas)
- Tab wird zu 4 Leerzeichen
- Volle Strg+V Unterstuetzung fuer Paste
- Dunkler Hintergrund mit gruener Schrift (Terminal-Look)

## Tests

```bash
python -m unittest tests/test_core.py tests/test_pdf.py -v
```

16 Tests: Models, Storage, Generator, Importers, PDF-Export

## Erweiterung

- Neue Section: Dataclass in models.py, Generator in generator.py + pdf_export.py, Page in mainwindow.py
- Neuer CI-Parameter: Feld in CIBranding, UI in CIBrandingPage, Nutzung in pdf_export.py

## Lizenz

MIT
