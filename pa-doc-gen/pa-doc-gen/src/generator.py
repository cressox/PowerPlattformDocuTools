"""
generator.py – Markdown-Dokumentation aus einem PAProject generieren.
"""
from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from models import PAProject, FlowAction, Screenshot
from diagram import generate_mermaid_markdown, generate_mermaid_diagram


DOCS_DIR = Path("docs")


def _screenshot_link(screenshots: list[Screenshot], section: str) -> str:
    """Erzeugt Markdown-Links fuer Screenshots einer Sektion."""
    links = []
    for s in screenshots:
        if s.section == section and s.filename:
            links.append(f"\n![{s.description or s.filename}](../data/screenshots/{s.filename})\n")
    return "\n".join(links)


def _actions_tree_md(actions: list[FlowAction], indent: int = 0) -> str:
    """Erzeugt eine eingerueckte Markdown-Darstellung der Aktionshierarchie."""
    lines = []
    prefix = "  " * indent
    for a in actions:
        connector_tag = f" `[{a.connector}]`" if a.connector else ""
        type_tag = f" *({a.action_type})*" if a.action_type else ""
        lines.append(f"{prefix}- **{a.name}**{type_tag}{connector_tag}")
        if a.description:
            lines.append(f"{prefix}  - {a.description}")
        if a.expression:
            lines.append(f"{prefix}  - Expression: `{a.expression.split(chr(10))[0]}`")
        if a.run_after:
            lines.append(f"{prefix}  - Run After: {', '.join(a.run_after)}")
        if a.children:
            lines.append(_actions_tree_md(a.children, indent + 1))
    return "\n".join(lines)


def _actions_detail_md(actions: list[FlowAction], level: int = 3) -> str:
    """Erzeugt detaillierte Markdown-Abschnitte fuer jede Aktion."""
    parts = []
    hdr = "#" * min(level, 6)
    for a in actions:
        parts.append(f"\n{hdr} {a.name}\n")
        rows = []
        if a.action_type:
            rows.append(f"| Typ | `{a.action_type}` |")
        if a.connector:
            rows.append(f"| Connector | {a.connector} |")
        if a.description:
            rows.append(f"| Beschreibung | {a.description} |")
        if a.inputs_summary:
            rows.append(f"| Inputs | {a.inputs_summary} |")
        if a.outputs_summary:
            rows.append(f"| Outputs | {a.outputs_summary} |")
        if a.configuration:
            rows.append(f"| Konfiguration | {a.configuration} |")
        if a.run_after:
            rows.append(f"| Run After | {', '.join(a.run_after)} |")

        if rows:
            parts.append("| Eigenschaft | Wert |")
            parts.append("|---|---|")
            parts.extend(rows)

        if a.expression:
            parts.append(f"\n**Expression:**\n```\n{a.expression}\n```\n")

        if a.children:
            parts.append(_actions_detail_md(a.children, level + 1))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Einzelne Dokumente generieren
# ---------------------------------------------------------------------------

def _gen_index(p: PAProject) -> str:
    return f"""# {p.meta.flow_name or 'Power Automate Flow'} – Dokumentation

> Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M')}

## Inhaltsverzeichnis

1. [Uebersicht](01_overview/overview.md)
2. [Trigger](01_overview/trigger.md)
3. [Flussdiagramm](01_overview/flowchart.md)
4. [Flow-Struktur – Aktionen](02_flow_structure/actions.md)
5. [Variablen](02_flow_structure/variables.md)
6. [Datenmappings](02_flow_structure/data_mappings.md)
7. [Konnektoren & Verbindungen](03_connections/connectors.md)
8. [Abhaengigkeiten](03_connections/dependencies.md)
9. [Fehlerbehandlung](04_error_handling/error_handling.md)
10. [SLA & Performance](05_governance/sla_performance.md)
11. [Governance & Betrieb](05_governance/governance_operations.md)
12. [Aenderungsprotokoll](06_change_log/change_log.md)
"""


def _gen_flowchart(p: PAProject) -> str:
    """Erzeugt die Flussdiagramm-Seite mit Mermaid-Diagramm."""
    return generate_mermaid_markdown(p)


def _gen_overview(p: PAProject) -> str:
    scr = _screenshot_link(p.screenshots, "overview")
    envs = ""
    if p.meta.environments:
        envs = "\n### Umgebungen\n\n| Umgebung | URL |\n|---|---|\n"
        for e in p.meta.environments:
            envs += f"| {e.env_type} | {e.url} |\n"

    services = ""
    if p.meta.connected_services:
        services = "\n### Verbundene Dienste\n\n" + "\n".join(f"- {s}" for s in p.meta.connected_services)

    return f"""# Uebersicht

## {p.meta.flow_name}

| Eigenschaft | Wert |
|---|---|
| Typ | {p.meta.flow_type} |
| Status | {p.meta.status} |
| Eigentuemer | {p.meta.owner} |
| Autor | {p.meta.author} |
| Erstellt | {p.meta.created_date} |
| Letzte Aenderung | {p.meta.last_modified} |
| Solution | {p.meta.solution_name} |
| Lizenz | {p.meta.license_requirement} |

### Beschreibung

{p.meta.description}
{envs}
{services}
{scr}
"""


def _gen_trigger(p: PAProject) -> str:
    t = p.trigger
    scr = _screenshot_link(p.screenshots, "trigger")
    schema = ""
    if t.input_schema:
        schema = f"\n### Input-Schema\n\n```json\n{t.input_schema}\n```\n"
    filt = ""
    if t.filter_expression:
        filt = f"\n### Filter / Bedingungen\n\n```json\n{t.filter_expression}\n```\n"

    return f"""# Trigger

## {t.name}

| Eigenschaft | Wert |
|---|---|
| Typ | {t.trigger_type} |
| Connector | {t.connector} |
| Frequenz | {t.schedule_frequency} |
| Intervall | {t.schedule_interval} |
| Zeitzone | {t.schedule_timezone} |
| Authentifizierung | {t.authentication} |

### Beschreibung

{t.description}
{schema}
{filt}
{scr}
"""


def _gen_actions(p: PAProject) -> str:
    scr = _screenshot_link(p.screenshots, "actions")
    tree = _actions_tree_md(p.actions)
    detail = _actions_detail_md(p.actions)

    return f"""# Flow-Struktur – Aktionen

## Aktionshierarchie

{tree}

---

## Aktionen im Detail

{detail}
{scr}
"""


def _gen_variables(p: PAProject) -> str:
    if not p.variables:
        return "# Variablen\n\nKeine Variablen definiert.\n"

    rows = ""
    for v in p.variables:
        rows += f"| {v.name} | {v.var_type} | `{v.initial_value}` | {v.description} | {v.set_in} | {v.used_in} |\n"

    return f"""# Variablen

| Name | Typ | Initialwert | Beschreibung | Gesetzt in | Verwendet in |
|---|---|---|---|---|---|
{rows}
"""


def _gen_data_mappings(p: PAProject) -> str:
    if not p.data_mappings:
        return "# Datenmappings\n\nKeine Datenmappings definiert.\n"

    rows = ""
    for m in p.data_mappings:
        rows += f"| {m.source_action} | {m.target_action} | {m.field_mapping} | {m.transformation} | {m.description} |\n"

    return f"""# Datenmappings

| Quelle | Ziel | Feldmapping | Transformation | Beschreibung |
|---|---|---|---|---|
{rows}
"""


def _gen_connectors(p: PAProject) -> str:
    if not p.connections:
        return "# Konnektoren & Verbindungen\n\nKeine Konnektoren definiert.\n"

    rows = ""
    for c in p.connections:
        rows += f"| {c.connector_name} | {c.connector_type} | {c.connection_name} | {c.auth_type} | {c.service_account} | {c.required_permissions} |\n"

    return f"""# Konnektoren & Verbindungen

| Connector | Typ | Verbindung | Auth-Typ | Service-Account | Berechtigungen |
|---|---|---|---|---|---|
{rows}
"""


def _gen_dependencies(p: PAProject) -> str:
    if not p.dependencies:
        return "# Abhaengigkeiten\n\nKeine Abhaengigkeiten definiert.\n"

    rows = ""
    for d in p.dependencies:
        rows += f"| {d.dep_type} | {d.name} | {d.description} |\n"

    return f"""# Abhaengigkeiten

| Typ | Name | Beschreibung |
|---|---|---|
{rows}
"""


def _gen_error_handling(p: PAProject) -> str:
    if not p.error_handling:
        return "# Fehlerbehandlung\n\nKeine Fehlerbehandlung definiert.\n"

    parts = ["# Fehlerbehandlung\n"]
    for eh in p.error_handling:
        parts.append(f"## {eh.scope_name}\n")
        parts.append(f"| Eigenschaft | Wert |")
        parts.append(f"|---|---|")
        if eh.pattern:
            parts.append(f"| Pattern | {eh.pattern} |")
        if eh.retry_count:
            parts.append(f"| Retry-Anzahl | {eh.retry_count} |")
        if eh.retry_interval:
            parts.append(f"| Retry-Intervall | {eh.retry_interval} |")
        if eh.retry_type:
            parts.append(f"| Retry-Typ | {eh.retry_type} |")
        if eh.notification_method:
            parts.append(f"| Benachrichtigung | {eh.notification_method} → {eh.notification_target} |")
        if eh.timeout:
            parts.append(f"| Timeout | {eh.timeout} |")
        if eh.description:
            parts.append(f"\n{eh.description}\n")

    return "\n".join(parts)


def _gen_sla(p: PAProject) -> str:
    s = p.sla
    return f"""# SLA & Performance

| Eigenschaft | Wert |
|---|---|
| Erwartete Laufzeit | {s.expected_runtime} |
| Maximale Laufzeit | {s.max_runtime} |
| Durchschnittl. Ausfuehrungen | {s.avg_executions} |
| Kritikalitaet | {s.criticality} |
| Eskalationspfad | {s.escalation_path} |

{s.description}
"""


def _gen_governance(p: PAProject) -> str:
    g = p.governance
    return f"""# Governance & Betrieb

## DLP & Compliance

| Eigenschaft | Wert |
|---|---|
| DLP-Policy | {g.dlp_policy} |
| Genehmigungs-Workflow | {g.approval_workflow} |

## Monitoring & Backup

| Eigenschaft | Wert |
|---|---|
| Monitoring-Setup | {g.monitoring_setup} |
| Backup-Strategie | {g.backup_strategy} |
| Rollback-Verfahren | {g.rollback_procedure} |

## Tests

| Eigenschaft | Wert |
|---|---|
| Testverfahren | {g.test_procedure} |
| Testdaten | {g.test_data} |

## Annahmen & Einschraenkungen

**Annahmen:** {g.assumptions}

**Einschraenkungen:** {g.limitations}

{g.description}
"""


def _gen_changelog(p: PAProject) -> str:
    if not p.changelog:
        return "# Aenderungsprotokoll\n\nKeine Eintraege.\n"

    rows = ""
    for c in p.changelog:
        rows += f"| {c.version} | {c.date} | {c.author} | {c.description} | {c.impact} | {c.ticket} |\n"

    return f"""# Aenderungsprotokoll

| Version | Datum | Autor | Beschreibung | Auswirkung | Ticket |
|---|---|---|---|---|---|
{rows}
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_docs(project: PAProject, output_dir: Path | str | None = None) -> Path:
    """Generiert die komplette Markdown-Dokumentation."""
    out = Path(output_dir) if output_dir else DOCS_DIR
    # Unterordner anlegen
    for sub in ("01_overview", "02_flow_structure", "03_connections",
                "04_error_handling", "05_governance", "06_change_log"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    files = {
        "index.md": _gen_index(project),
        "01_overview/overview.md": _gen_overview(project),
        "01_overview/trigger.md": _gen_trigger(project),
        "01_overview/flowchart.md": _gen_flowchart(project),
        "02_flow_structure/actions.md": _gen_actions(project),
        "02_flow_structure/variables.md": _gen_variables(project),
        "02_flow_structure/data_mappings.md": _gen_data_mappings(project),
        "03_connections/connectors.md": _gen_connectors(project),
        "03_connections/dependencies.md": _gen_dependencies(project),
        "04_error_handling/error_handling.md": _gen_error_handling(project),
        "05_governance/sla_performance.md": _gen_sla(project),
        "05_governance/governance_operations.md": _gen_governance(project),
        "06_change_log/change_log.md": _gen_changelog(project),
    }

    for rel_path, content in files.items():
        fp = out / rel_path
        fp.write_text(content, encoding="utf-8")

    return out
