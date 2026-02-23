# ⚡ Power Apps Doc Builder

**Generate high-quality, standardized documentation for Power Apps Canvas Apps from exported YAML.**

Produces Markdown, HTML, JSON, and LaTeX documentation suitable for handover, governance, and audits. Usable by non-developers.

---

## Features

- **YAML Parsing**: Paste or upload Power Apps Canvas App YAML exports
- **Comprehensive Documentation**: 14 sections covering app overview, architecture, screens, controls, connectors, variables, components, forms, security, error handling, ALM, and best-practice checks
- **Multi-Format Output**: Markdown (.md), HTML (.html), JSON (.json), LaTeX (.tex)
- **Screenshot Support**: Upload images, map to screens, embed in docs
- **Incremental Updates**: Re-import YAML to see diffs (added/removed screens, formula changes)
- **Best-Practice Checks**: Heuristic lint for delegation risks, naming conventions, hard-coded URLs, DLP-relevant connectors
- **Privacy**: IDs redacted by default, no cloud dependencies, fully offline
- **German Labels**: Documentation headings in German (code comments in English)

---

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Backend** | Python 3.11+ / stdlib `http.server` + PyYAML | Best YAML parsing (PyYAML pre-installed), zero pip installs needed, works offline |
| **Frontend** | Vanilla HTML/CSS/JS (single file) | No build step, no npm, instant startup, works in any browser |
| **Storage** | Local JSON files | `project.json` + `app_model.json` in `/data`, no database needed |

---

## Folder Structure

```
/powerapps-doc-builder
  /backend
    main.py              # HTTP server (all endpoints, stdlib only)
    parser.py            # Power Apps YAML parser
    doc_generator.py     # MD/HTML/JSON/LaTeX generator
    diff_engine.py       # Diff computation between model versions
  /frontend
    index.html           # Complete single-file frontend (HTML/CSS/JS)
  /data
    project.json         # Project state (auto-created)
    app_model.json       # Canonical model (auto-created)
    sample.yaml          # Sample Power Apps YAML for testing
    /output              # Generated docs
    /images              # Uploaded screenshots
  README.md
```

---

## Setup & Run

### Prerequisites

- **Python 3.11+** with PyYAML ([python.org](https://www.python.org/downloads/))
  - PyYAML is typically pre-installed. If not: `pip install pyyaml`
- No Node.js, no npm, no build step required!

### Windows

```powershell
# 1. Clone or download this folder
cd powerapps-doc-builder

# 2. Start the server (that's it!)
python backend\main.py

# → Open http://127.0.0.1:8000 in your browser
```

### macOS / Linux

```bash
# 1. Clone or download this folder
cd powerapps-doc-builder

# 2. Start the server (that's it!)
python3 backend/main.py

# → Open http://127.0.0.1:8000 in your browser
```

### Quick Start

1. Open **http://127.0.0.1:8000** in your browser
2. **Step 1**: Paste the sample YAML from `data/sample.yaml` or upload it
3. **Step 2**: Review the parsed summary (screens, controls, connectors)
4. **Step 3**: (Optional) Upload screenshots and map them to screens
5. **Step 4**: Add manual notes (purpose, environment, roles)
6. **Step 5**: Click "Generate" and preview/download your docs

---

## Workflow

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Paste/Upload │────▶│  Parse YAML │────▶│   Summary    │
│     YAML      │     │   Engine    │     │  Dashboard   │
└──────────────┘     └─────────────┘     └──────┬───────┘
                                                │
                    ┌───────────────────────────┘
                    │
              ┌─────▼──────┐     ┌──────────────┐     ┌──────────────┐
              │ Screenshots │────▶│  Add Notes   │────▶│   Generate   │
              │   Mapping   │     │  & Settings  │     │  MD/HTML/... │
              └────────────┘     └──────────────┘     └──────┬───────┘
                                                             │
                                                  ┌──────────▼──────────┐
                                                  │  Preview & Download │
                                                  └─────────────────────┘
```

---

## Internal Data Model (`app_model.json`)

The canonical model is a single JSON document with this schema:

```json
{
  "generated_at": "ISO 8601 timestamp",
  "parser_version": "1.0.0",
  "app_name": "string",
  "app_properties": {
    "AppVersion": "string",
    "Author": "string",
    "OnStart": "formula string",
    "...": "..."
  },
  "screens": [
    {
      "name": "ScreenName",
      "index": 0,
      "purpose": "",
      "properties": { "OnVisible": "...", "Fill": "..." },
      "controls": [
        {
          "name": "ControlName",
          "type": "button|gallery|form|label|...",
          "parent": "ParentName",
          "screen": "ScreenName",
          "properties": { "Text": "...", "OnSelect": "..." },
          "formulas": [
            { "property": "OnSelect", "formula": "Navigate(...)", "control": "ControlName" }
          ]
        }
      ],
      "formulas": [ /* screen-level formulas */ ]
    }
  ],
  "controls_flat": [ /* all controls across all screens, flat list */ ],
  "connectors": [
    { "name": "Office365Users", "type": "Office365Users", "details": {} }
  ],
  "data_sources": [
    { "name": "Urlaubsantraege", "columns_referenced": ["Status", "VonDatum", "..."] }
  ],
  "variables": {
    "global_vars": [
      { "name": "varCurrentUser", "locations": ["..."], "initialized_in": ["App.OnStart"] }
    ],
    "context_vars": [ /* UpdateContext variables */ ],
    "collections": [
      { "name": "colMitarbeiter", "locations": ["..."], "initialized_in": ["..."], "shape_hint": "" }
    ]
  },
  "components": [ /* component definitions */ ],
  "forms": [
    {
      "name": "frmAntrag",
      "screen": "NeuerAntragScreen",
      "mode": "FormMode.New",
      "data_source": "'Urlaubsantraege'",
      "data_cards": [
        { "name": "dcVonDatum", "field": "VonDatum", "default": "Today()", "update": "..." }
      ]
    }
  ],
  "navigation_graph": [
    { "from_screen": "HomeScreen", "to_screen": "DetailScreen", "trigger_control": "btnDetails", "trigger_property": "OnSelect" }
  ],
  "formulas_all": [ /* every formula across the entire app */ ],
  "error_handling": [
    { "type": "Notify|IfError", "location": "Screen.Control.Property", "message_hint": "..." }
  ],
  "best_practice_findings": [
    { "type": "delegation_risk|performance|naming_convention|security|hardcoded_value|unused",
      "severity": "warning|info",
      "message_de": "German message",
      "message_en": "English message",
      "location": "..." }
  ],
  "stats": {
    "total_screens": 4,
    "total_controls": 20,
    "total_formulas": 35,
    "control_type_counts": { "button": 6, "gallery": 2, "..." : "..." }
  },
  "unparsed": [ /* sections that couldn't be parsed */ ]
}
```

---

## Documentation Sections Generated

| # | Section (German) | Content |
|---|-----------------|---------|
| 1 | App-Übersicht | Name, version, author, stats, purpose, users, environments |
| 2 | Architektur | Navigation graph, data access approach, integration points, delegation risks |
| 3 | Bildschirm-Dokumentation | Per-screen: screenshot, controls, data bindings, navigation, business logic |
| 4 | Kontroll-Inventar | Type counts, detailed major controls |
| 5 | Datenquellen & Konnektoren | Connectors, data sources, referenced columns |
| 6 | Variablen & Sammlungen | Global vars, context vars, collections with init locations |
| 7 | Komponenten | Component definitions, inputs/outputs, usage locations |
| 8 | Formulare & Datenkarten | Forms, modes, data cards, field mappings |
| 9 | Sicherheit & Governance | Roles, DLP flags, connector classification |
| 10 | Fehlerbehandlung | Notify, IfError patterns |
| 11 | ALM / Deployment | Export/import notes (user-editable) |
| 12 | Best-Practice-Prüfungen | Delegation, naming, hard-coded URLs, unused vars, DLP |
| 13 | Änderungsprotokoll | Diff history with timestamps |
| 14 | Nicht interpretierte Abschnitte | Unparsed YAML sections |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/project` | Get project state + model summary |
| POST | `/api/project/notes` | Update manual notes |
| POST | `/api/project/settings` | Update settings |
| POST | `/api/parse` | Parse YAML (form: `yaml_text` or `yaml_file`) |
| GET | `/api/screens` | List screen names |
| POST | `/api/screenshots/upload` | Upload images (multipart) |
| POST | `/api/screenshots/upload-zip` | Upload ZIP of images |
| POST | `/api/screenshots/map` | Save screenshot mapping |
| GET | `/api/screenshots/auto-match` | Auto-match by filename |
| GET | `/api/images` | List uploaded images |
| POST | `/api/generate` | Generate docs (body: format list) |
| GET | `/api/preview/{fmt}` | Get doc content for preview |
| GET | `/api/download/{fname}` | Download generated file |
| GET | `/api/model` | Get full app_model.json |
| POST | `/api/changelog/note` | Add note to changelog entry |
| POST | `/api/reset` | Reset all project data |

---

## License

MIT – Free for internal and commercial use.
