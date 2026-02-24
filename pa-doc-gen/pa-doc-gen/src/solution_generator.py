"""
solution_generator.py – Markdown-Dokumentation fuer Power Platform Solutions.

Generiert eine vollstaendige Dokumentation aller Entitaeten einer Solution:
  - Solution-Uebersicht
  - Komponentenverzeichnis
  - Flow-Dokumentation (mit Flussdiagramm) je Flow
  - Canvas Apps
  - Custom Connectors
  - Connection References
  - Environment Variables
  - Dataverse Tables
  - Security Roles
  - Web Resources
  - Plugins
  - Sonstige Komponenten
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from solution_parser import SolutionInfo, SolutionEntity, SolutionComponentType, get_solution_stats
from diagram import generate_mermaid_markdown, generate_mermaid_diagram
from generator import (
    generate_docs, _gen_trigger, _gen_actions, _gen_variables,
    _gen_connectors, _gen_dependencies, _gen_error_handling,
    _actions_tree_md, _actions_detail_md, _screenshot_link,
)
from models import PAProject


def _gen_solution_index(sol: SolutionInfo) -> str:
    """Erzeugt die Index-Seite fuer die Solution-Dokumentation."""
    stats = get_solution_stats(sol)

    components_list = []
    if stats["flows"]:
        components_list.append(f"- **Cloud Flows**: {stats['flows']}")
    if stats["canvas_apps"]:
        components_list.append(f"- **Canvas Apps**: {stats['canvas_apps']}")
    if stats["model_apps"]:
        components_list.append(f"- **Model-Driven Apps**: {stats['model_apps']}")
    if stats["custom_connectors"]:
        components_list.append(f"- **Custom Connectors**: {stats['custom_connectors']}")
    if stats["connection_references"]:
        components_list.append(f"- **Connection References**: {stats['connection_references']}")
    if stats["env_variables"]:
        components_list.append(f"- **Environment Variables**: {stats['env_variables']}")
    if stats["tables"]:
        components_list.append(f"- **Dataverse Tables**: {stats['tables']}")
    if stats["security_roles"]:
        components_list.append(f"- **Security Roles**: {stats['security_roles']}")
    if stats["web_resources"]:
        components_list.append(f"- **Web Resources**: {stats['web_resources']}")
    if stats["plugins"]:
        components_list.append(f"- **Plugins / Assemblies**: {stats['plugins']}")
    if stats["processes"]:
        components_list.append(f"- **Workflows / Prozesse**: {stats['processes']}")
    if stats["other"]:
        components_list.append(f"- **Sonstige**: {stats['other']}")

    components = "\n".join(components_list) if components_list else "Keine Komponenten gefunden."

    toc_entries = ["1. [Solution-Uebersicht](00_solution/overview.md)",
                   "2. [Komponentenverzeichnis](00_solution/components.md)"]

    idx = 3
    if sol.flows:
        for i, flow in enumerate(sol.flows, 1):
            safe_name = _safe_dirname(flow.name)
            toc_entries.append(f"{idx}. [Flow: {flow.name}](flows/{safe_name}/index.md)")
            idx += 1

    if sol.canvas_apps:
        toc_entries.append(f"{idx}. [Canvas Apps](00_solution/canvas_apps.md)")
        idx += 1

    if sol.custom_connectors:
        toc_entries.append(f"{idx}. [Custom Connectors](00_solution/custom_connectors.md)")
        idx += 1

    if sol.connection_references:
        toc_entries.append(f"{idx}. [Connection References](00_solution/connection_references.md)")
        idx += 1

    if sol.env_variables:
        toc_entries.append(f"{idx}. [Environment Variables](00_solution/env_variables.md)")
        idx += 1

    if sol.tables:
        toc_entries.append(f"{idx}. [Dataverse Tables](00_solution/tables.md)")
        idx += 1

    if sol.security_roles:
        toc_entries.append(f"{idx}. [Security Roles](00_solution/security_roles.md)")
        idx += 1

    if sol.web_resources:
        toc_entries.append(f"{idx}. [Web Resources](00_solution/web_resources.md)")
        idx += 1

    if sol.plugins:
        toc_entries.append(f"{idx}. [Plugins / Assemblies](00_solution/plugins.md)")
        idx += 1

    toc = "\n".join(toc_entries)

    return f"""# {sol.display_name or sol.unique_name or 'Power Platform Solution'} – Dokumentation

> Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M')}

## Inhaltsverzeichnis

{toc}

## Komponenten-Uebersicht

{components}

**Gesamt: {stats['total_components']} Komponenten**
"""


def _gen_solution_overview(sol: SolutionInfo) -> str:
    """Erzeugt die Solution-Uebersichtsseite."""
    managed = "Ja" if sol.managed else "Nein"
    return f"""# Solution-Uebersicht

## {sol.display_name or sol.unique_name}

| Eigenschaft | Wert |
|---|---|
| Unique Name | {sol.unique_name} |
| Anzeigename | {sol.display_name} |
| Version | {sol.version} |
| Publisher | {sol.publisher_name} |
| Publisher-Praefix | {sol.publisher_prefix} |
| Managed | {managed} |

### Beschreibung

{sol.description or '–'}
"""


def _gen_components_list(sol: SolutionInfo) -> str:
    """Erzeugt ein vollstaendiges Komponentenverzeichnis."""
    parts = ["# Komponentenverzeichnis\n"]

    # Nach Typ gruppieren
    type_groups: dict[str, list[SolutionEntity]] = {}
    for e in sol.entities:
        if e.entity_type not in type_groups:
            type_groups[e.entity_type] = []
        type_groups[e.entity_type].append(e)

    for etype, entities in sorted(type_groups.items()):
        parts.append(f"\n## {etype} ({len(entities)})\n")
        parts.append("| Name | Anzeigename | Beschreibung |")
        parts.append("|---|---|---|")
        for e in entities:
            parts.append(f"| {e.name} | {e.display_name or '–'} | {e.description or '–'} |")

    return "\n".join(parts)


def _gen_canvas_apps_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Canvas Apps."""
    if not sol.canvas_apps:
        return "# Canvas Apps\n\nKeine Canvas Apps in dieser Solution.\n"

    parts = ["# Canvas Apps\n"]
    for app in sol.canvas_apps:
        parts.append(f"\n## {app.display_name or app.name}\n")
        parts.append("| Eigenschaft | Wert |")
        parts.append("|---|---|")
        parts.append(f"| Name | {app.name} |")
        if app.details.get("author"):
            parts.append(f"| Autor | {app.details['author']} |")
        if app.details.get("app_version"):
            parts.append(f"| Version | {app.details['app_version']} |")
        if app.description:
            parts.append(f"\n{app.description}\n")

    return "\n".join(parts)


def _gen_custom_connectors_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Custom Connectors."""
    if not sol.custom_connectors:
        return "# Custom Connectors\n\nKeine Custom Connectors in dieser Solution.\n"

    parts = ["# Custom Connectors\n"]
    parts.append("| Name | Beschreibung | Host | Auth-Typ |")
    parts.append("|---|---|---|---|")
    for cc in sol.custom_connectors:
        host = cc.details.get("host", "–")
        auth = cc.details.get("auth_type", "–")
        parts.append(f"| {cc.display_name or cc.name} | {cc.description or '–'} | {host} | {auth} |")

    return "\n".join(parts)


def _gen_connection_refs_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Connection References."""
    if not sol.connection_references:
        return "# Connection References\n\nKeine Connection References in dieser Solution.\n"

    parts = ["# Connection References\n"]
    parts.append("| Name | Anzeigename | Connector-ID |")
    parts.append("|---|---|---|")
    for cr in sol.connection_references:
        conn_id = cr.details.get("connector_id", "–")
        parts.append(f"| {cr.name} | {cr.display_name or '–'} | {conn_id} |")

    return "\n".join(parts)


def _gen_env_variables_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Environment Variables."""
    if not sol.env_variables:
        return "# Environment Variables\n\nKeine Environment Variables in dieser Solution.\n"

    parts = ["# Environment Variables\n"]
    parts.append("| Name | Anzeigename | Typ | Standardwert | Erforderlich |")
    parts.append("|---|---|---|---|---|")
    for ev in sol.env_variables:
        ev_type = ev.details.get("type") or ev.details.get("value", "–")
        default = ev.details.get("default_value", "–")
        required = "Ja" if ev.details.get("is_required") else "Nein"
        parts.append(f"| {ev.name} | {ev.display_name or '–'} | {ev_type} | {default} | {required} |")

    return "\n".join(parts)


def _gen_tables_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Dataverse Tables."""
    if not sol.tables:
        return "# Dataverse Tables\n\nKeine Dataverse Tables in dieser Solution.\n"

    parts = ["# Dataverse Tables\n"]
    parts.append("| Schema-Name | Anzeigename | Attribute |")
    parts.append("|---|---|---|")
    for t in sol.tables:
        attr_count = t.details.get("attribute_count", "–")
        parts.append(f"| {t.name} | {t.display_name or '–'} | {attr_count} |")

    return "\n".join(parts)


def _gen_security_roles_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Security Roles."""
    if not sol.security_roles:
        return "# Security Roles\n\nKeine Security Roles in dieser Solution.\n"

    parts = ["# Security Roles\n"]
    parts.append("| Name | Beschreibung |")
    parts.append("|---|---|")
    for sr in sol.security_roles:
        parts.append(f"| {sr.name} | {sr.description or '–'} |")

    return "\n".join(parts)


def _gen_web_resources_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Web Resources."""
    if not sol.web_resources:
        return "# Web Resources\n\nKeine Web Resources in dieser Solution.\n"

    parts = ["# Web Resources\n"]
    parts.append("| Name | Typ |")
    parts.append("|---|---|")
    for wr in sol.web_resources:
        wr_type = wr.details.get("resource_type", "–")
        parts.append(f"| {wr.name} | {wr_type} |")

    return "\n".join(parts)


def _gen_plugins_doc(sol: SolutionInfo) -> str:
    """Dokumentation fuer Plugins."""
    if not sol.plugins:
        return "# Plugins / Assemblies\n\nKeine Plugins in dieser Solution.\n"

    parts = ["# Plugins / Assemblies\n"]
    parts.append("| Name | Beschreibung |")
    parts.append("|---|---|")
    for p in sol.plugins:
        parts.append(f"| {p.name} | {p.description or '–'} |")

    return "\n".join(parts)


def _gen_flow_doc(entity: SolutionEntity) -> dict[str, str]:
    """
    Erzeugt die Flow-Dokumentation fuer einen einzelnen Flow.
    Gibt ein Dict (relative_path -> content) zurueck.
    """
    project = entity.flow_project
    if not project:
        return {
            "index.md": f"# {entity.name}\n\nFlow konnte nicht geparst werden.\n"
        }

    from diagram import generate_mermaid_markdown

    files = {}

    # Index
    from flow_parser import get_flow_stats
    stats = get_flow_stats(project)

    files["index.md"] = f"""# {project.meta.flow_name or entity.name}

| Eigenschaft | Wert |
|---|---|
| Typ | {project.meta.flow_type} |
| Status | {project.meta.status} |
| Beschreibung | {project.meta.description or '–'} |
| Trigger | {stats['trigger_type'] or '–'} |
| Aktionen | {stats['total_actions']} |
| Konnektoren | {stats['connectors']} |
| Variablen | {stats['variables']} |

## Seiten

1. [Flussdiagramm](flowchart.md)
2. [Trigger](trigger.md)
3. [Aktionen](actions.md)
4. [Variablen](variables.md)
5. [Konnektoren](connectors.md)
"""

    # Flussdiagramm
    files["flowchart.md"] = generate_mermaid_markdown(project)

    # Trigger
    files["trigger.md"] = _gen_trigger(project)

    # Aktionen
    files["actions.md"] = _gen_actions(project)

    # Variablen
    files["variables.md"] = _gen_variables(project)

    # Konnektoren
    files["connectors.md"] = _gen_connectors(project)

    return files


def _safe_dirname(name: str) -> str:
    """Erzeugt einen sicheren Verzeichnisnamen."""
    import re
    clean = re.sub(r'[<>:"/\\|?*]', '_', name)
    clean = re.sub(r'\s+', '_', clean)
    return clean[:60] or "unnamed"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_solution_docs(solution: SolutionInfo, output_dir: Path | str | None = None) -> Path:
    """Generiert komplette Markdown-Dokumentation fuer eine Solution."""
    out = Path(output_dir) if output_dir else Path("docs/solution")
    out.mkdir(parents=True, exist_ok=True)

    # Solution-Ordner
    sol_dir = out / "00_solution"
    sol_dir.mkdir(parents=True, exist_ok=True)

    # Index
    (out / "index.md").write_text(_gen_solution_index(solution), encoding="utf-8")

    # Solution-Uebersicht
    (sol_dir / "overview.md").write_text(_gen_solution_overview(solution), encoding="utf-8")

    # Komponentenverzeichnis
    (sol_dir / "components.md").write_text(_gen_components_list(solution), encoding="utf-8")

    # Canvas Apps
    if solution.canvas_apps:
        (sol_dir / "canvas_apps.md").write_text(_gen_canvas_apps_doc(solution), encoding="utf-8")

    # Custom Connectors
    if solution.custom_connectors:
        (sol_dir / "custom_connectors.md").write_text(_gen_custom_connectors_doc(solution), encoding="utf-8")

    # Connection References
    if solution.connection_references:
        (sol_dir / "connection_references.md").write_text(_gen_connection_refs_doc(solution), encoding="utf-8")

    # Environment Variables
    if solution.env_variables:
        (sol_dir / "env_variables.md").write_text(_gen_env_variables_doc(solution), encoding="utf-8")

    # Tables
    if solution.tables:
        (sol_dir / "tables.md").write_text(_gen_tables_doc(solution), encoding="utf-8")

    # Security Roles
    if solution.security_roles:
        (sol_dir / "security_roles.md").write_text(_gen_security_roles_doc(solution), encoding="utf-8")

    # Web Resources
    if solution.web_resources:
        (sol_dir / "web_resources.md").write_text(_gen_web_resources_doc(solution), encoding="utf-8")

    # Plugins
    if solution.plugins:
        (sol_dir / "plugins.md").write_text(_gen_plugins_doc(solution), encoding="utf-8")

    # Flows (einzeln dokumentieren)
    if solution.flows:
        flows_dir = out / "flows"
        flows_dir.mkdir(parents=True, exist_ok=True)

        for flow_entity in solution.flows:
            flow_dir = flows_dir / _safe_dirname(flow_entity.name)
            flow_dir.mkdir(parents=True, exist_ok=True)

            flow_docs = _gen_flow_doc(flow_entity)
            for fname, content in flow_docs.items():
                (flow_dir / fname).write_text(content, encoding="utf-8")

    return out
