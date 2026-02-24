"""
Markdown document generator.

Generates the /docs folder structure from a Project instance.
All user-facing text is in German; code identifiers stay English.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from .models import (
    Project, KPI, DataSource, PowerQuery, Measure,
    ReportPage, ChangeLogEntry, ModelTable, ModelRelationship,
)

DOCS_ROOT = Path("docs")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _esc(text: str) -> str:
    """Escape pipe chars for Markdown tables."""
    return text.replace("|", "\\|").replace("\n", " ")


# ===================================================================
# Individual generators
# ===================================================================

def gen_index(p: Project) -> str:
    m = p.meta
    lines = [
        f"# {m.report_name or 'Power BI Report'} – Dokumentation",
        "",
        f"> {m.short_description}" if m.short_description else "",
        "",
        "| Feld | Wert |",
        "|---|---|",
        f"| **Eigentümer** | {m.owner} |",
        f"| **Autor** | {m.author} |",
        f"| **Version** | {m.version} |",
        f"| **Datum** | {m.date} |",
        f"| **Zielgruppe** | {m.audience} |",
        "",
        "## Inhaltsverzeichnis",
        "",
        "1. [Übersicht](01_overview/overview.md)",
        "2. [KPIs & Kennzahlen](01_overview/kpis.md)",
        "3. [Datenquellen](02_data_sources/data_sources.md)",
        "4. [Power Query (M)](03_power_query/queries.md)",
        "5. [Datenmodell](04_data_model/data_model.md)",
        "6. [Measures (DAX)](05_measures/measures.md)",
        "7. [Berichtsseiten & Visuals](06_report_design/pages_visuals.md)",
        "8. [Governance – Aktualisierung, Gateway, RLS](07_governance/refresh_gateway_rls.md)",
        "9. [Annahmen & Einschränkungen](07_governance/assumptions_limitations.md)",
        "10. [Änderungsprotokoll](08_change_log/change_log.md)",
        "11. [Berechtigungen](09_permissions/permissions.md)",
        "12. [Ablagestruktur](10_storage/storage.md)",
        "13. [Namenskonzept](11_naming/naming_conventions.md)",
        "14. [Änderungshinweise & Best Practices](12_change_guidance/change_guidance.md)",
        "",
        "---",
        f"*Generiert mit Power BI Documentation Generator*",
    ]
    return "\n".join(lines) + "\n"


def gen_overview(p: Project) -> str:
    m = p.meta
    envs_table = ""
    if m.environments:
        envs_table = (
            "\n## Umgebungen\n\n"
            "| Umgebung | Arbeitsbereich | URL |\n"
            "|---|---|---|\n"
        )
        for e in m.environments:
            envs_table += f"| {e.name} | {e.workspace} | {e.url} |\n"

    links = ""
    if m.powerbi_service_url or m.sharepoint_folder_url:
        links = "\n## Links\n\n"
        if m.powerbi_service_url:
            links += f"- **Power BI Service:** {m.powerbi_service_url}\n"
        if m.sharepoint_folder_url:
            links += f"- **SharePoint-Ordner:** {m.sharepoint_folder_url}\n"

    return (
        f"# Übersicht – {m.report_name}\n\n"
        f"{m.short_description}\n\n"
        f"| Feld | Wert |\n"
        f"|---|---|\n"
        f"| Eigentümer | {m.owner} |\n"
        f"| Autor | {m.author} |\n"
        f"| Version | {m.version} |\n"
        f"| Datum | {m.date} |\n"
        f"| Zielgruppe | {m.audience} |\n"
        f"{envs_table}"
        f"{links}"
    )


def gen_kpis(p: Project) -> str:
    lines = [
        "# KPIs & Kennzahlen",
        "",
    ]
    if not p.kpis:
        lines.append("*Noch keine KPIs dokumentiert.*\n")
        return "\n".join(lines)

    lines += [
        "| # | Name | Granularität | Beschreibung |",
        "|---|---|---|---|",
    ]
    for i, k in enumerate(p.kpis, 1):
        lines.append(f"| {i} | {_esc(k.name)} | {_esc(k.granularity)} | {_esc(k.business_description)} |")

    lines.append("")
    for k in p.kpis:
        lines += [
            f"## {k.name}",
            "",
            f"**Fachliche Beschreibung:** {k.business_description}",
            "",
            f"**Technische Definition:** {k.technical_definition}",
            "",
            f"**Granularität:** {k.granularity}",
            "",
            f"**Filter / Kontext:** {k.filters_context}" if k.filters_context else "",
            "",
            f"**Einschränkungen / Hinweise:** {k.caveats}" if k.caveats else "",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def gen_data_sources(p: Project) -> str:
    lines = [
        "# Datenquellen",
        "",
    ]
    if not p.data_sources:
        lines.append("*Noch keine Datenquellen dokumentiert.*\n")
        return "\n".join(lines)

    lines += [
        "| Name | Typ | Verbindung | Aktualisierung | Gateway |",
        "|---|---|---|---|---|",
    ]
    for s in p.data_sources:
        gw = s.gateway_name if s.gateway_required else "–"
        lines.append(
            f"| {_esc(s.name)} | {_esc(s.source_type)} | {_esc(s.connection_info)} "
            f"| {_esc(s.refresh_cadence)} | {gw} |"
        )

    lines.append("")
    for s in p.data_sources:
        lines += [
            f"## {s.name}",
            "",
            f"- **Typ:** {s.source_type}",
            f"- **Verbindung:** {s.connection_info}",
            f"- **Aktualisierung:** {s.refresh_cadence}",
            f"- **Gateway:** {'Ja – ' + s.gateway_name if s.gateway_required else 'Nein'}",
            f"- **Verantwortlich:** {s.owner_contact}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def gen_queries(p: Project) -> str:
    lines = ["# Power Query (M) – Abfragen", ""]
    if not p.power_queries:
        lines.append("*Noch keine Abfragen dokumentiert.*\n")
        return "\n".join(lines)

    for q in p.power_queries:
        lines += [
            f"## {q.query_name}",
            "",
            f"**Zweck:** {q.purpose}",
            "",
            f"**Eingaben:** {q.inputs}" if q.inputs else "",
            "",
            f"**Wichtige Transformationen:** {q.major_transformations}" if q.major_transformations else "",
            "",
            f"**Ausgabetabelle:** `{q.output_table}`" if q.output_table else "",
            "",
        ]
        if q.m_code:
            lines += [
                "**M-Code:**",
                "",
                "```powerquery",
                q.m_code,
                "```",
                "",
            ]
        if q.notes:
            lines += [f"**Hinweise:** {q.notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_data_model(p: Project) -> str:
    dm = p.data_model
    lines = ["# Datenmodell", ""]

    if dm.tables:
        lines += [
            "## Tabellen",
            "",
            "| Tabelle | Typ | Schlüssel | Beschreibung |",
            "|---|---|---|---|",
        ]
        for t in dm.tables:
            lines.append(f"| {_esc(t.name)} | {_esc(t.table_type)} | {_esc(t.keys)} | {_esc(t.description)} |")
        lines.append("")

    if dm.relationships:
        lines += [
            "## Beziehungen",
            "",
            "| Von (Tabelle.Spalte) | Nach (Tabelle.Spalte) | Kardinalität | Filterrichtung |",
            "|---|---|---|---|",
        ]
        for r in dm.relationships:
            lines.append(
                f"| {r.from_table}.{r.from_column} | {r.to_table}.{r.to_column} "
                f"| {r.cardinality} | {r.filter_direction} |"
            )
        lines.append("")

    if dm.date_logic_notes:
        lines += ["## Datumslogik", "", dm.date_logic_notes, ""]

    if dm.screenshot_paths:
        lines += ["## Screenshots", ""]
        for sp in dm.screenshot_paths:
            lines.append(f"![Datenmodell]({sp})")
        lines.append("")

    if dm.notes:
        lines += ["## Anmerkungen", "", dm.notes, ""]

    if not dm.tables and not dm.relationships:
        lines.append("*Noch kein Datenmodell dokumentiert.*\n")

    return "\n".join(lines)


def gen_measures(p: Project) -> str:
    lines = ["# Measures (DAX)", ""]
    if not p.measures:
        lines.append("*Noch keine Measures dokumentiert.*\n")
        return "\n".join(lines)

    lines += [
        "| # | Name | Ordner | Beschreibung |",
        "|---|---|---|---|",
    ]
    for i, ms in enumerate(p.measures, 1):
        lines.append(f"| {i} | [{_esc(ms.name)}](#{ms.name.lower().replace(' ', '-')}) | {_esc(ms.display_folder)} | {_esc(ms.description)} |")
    lines.append("")

    for ms in p.measures:
        lines += [
            f"## {ms.name}",
            "",
            f"**Ordner:** {ms.display_folder}" if ms.display_folder else "",
            "",
            f"**Beschreibung:** {ms.description}",
            "",
            "**DAX-Code:**",
            "",
            "```dax",
            ms.dax_code,
            "```",
            "",
        ]
        if ms.dependencies:
            lines += [f"**Abhängigkeiten:** {ms.dependencies}", ""]
        if ms.filter_context_notes:
            lines += [f"**Filter-/Kontextverhalten:** {ms.filter_context_notes}", ""]
        if ms.validation_notes:
            lines += [f"**Validierung:** {ms.validation_notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_pages_visuals(p: Project) -> str:
    lines = ["# Berichtsseiten & Visuals", ""]
    if not p.report_pages:
        lines.append("*Noch keine Seiten dokumentiert.*\n")
        return "\n".join(lines)

    for pg in p.report_pages:
        lines += [
            f"## {pg.page_name}",
            "",
            f"**Zweck:** {pg.purpose}",
            "",
        ]
        if pg.visuals:
            lines += [
                "### Visuals",
                "",
                "| Visual | Beschreibung |",
                "|---|---|",
            ]
            for v in pg.visuals:
                lines.append(f"| {_esc(v.name)} | {_esc(v.description)} |")
            lines.append("")
        if pg.slicers_filters:
            lines += [f"**Slicer / Filter:** {pg.slicers_filters}", ""]
        if pg.notes:
            lines += [f"**Hinweise:** {pg.notes}", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def gen_refresh_gateway_rls(p: Project) -> str:
    g = p.governance
    lines = ["# Governance – Aktualisierung, Gateway & RLS", ""]
    lines += [
        "## Aktualisierungsplan",
        "",
        g.refresh_schedule or "*Nicht dokumentiert.*",
        "",
        "## Monitoring",
        "",
        g.monitoring_notes or "*Nicht dokumentiert.*",
        "",
        "## Row-Level Security (RLS)",
        "",
        g.rls_notes or "*Nicht konfiguriert / dokumentiert.*",
        "",
        "## Performance-Hinweise",
        "",
        g.performance_notes or "*Keine bekannten Engpässe dokumentiert.*",
        "",
    ]
    return "\n".join(lines)


def gen_assumptions_limitations(p: Project) -> str:
    g = p.governance
    lines = [
        "# Annahmen & Einschränkungen",
        "",
        "## Annahmen",
        "",
        g.assumptions or "*Keine dokumentiert.*",
        "",
        "## Einschränkungen",
        "",
        g.limitations or "*Keine dokumentiert.*",
        "",
    ]
    return "\n".join(lines)


def gen_change_log(p: Project) -> str:
    lines = ["# Änderungsprotokoll", ""]
    if not p.change_log:
        lines.append("*Noch keine Einträge.*\n")
        return "\n".join(lines)

    lines += [
        "| Version | Datum | Beschreibung | Autor | Auswirkung | Ticket |",
        "|---|---|---|---|---|---|",
    ]
    for c in p.change_log:
        lines.append(
            f"| {_esc(c.version)} | {c.date} | {_esc(c.description)} "
            f"| {_esc(c.author)} | {_esc(c.impact)} | {_esc(c.ticket_link)} |"
        )
    lines.append("")
    return "\n".join(lines)


def gen_permissions(p: Project) -> str:
    perm = p.permissions
    lines = [
        "# Berechtigungen",
        "",
        "## Best Practices",
        "",
        "- Verwende Workspace-Rollen statt individueller Freigaben",
        "- Setze Row-Level Security (RLS) fuer sensible Daten ein",
        "- Pruefe regelmaessig die Zugriffsrechte (mindestens quartalsweise)",
        "- Dokumentiere alle Berechtigungsaenderungen im Aenderungsprotokoll",
        "- Nutze Sicherheitsgruppen statt Einzelpersonen fuer Berechtigungen",
        "",
        "## Workspace-Rollen",
        "",
        perm.workspace_roles or "*Nicht dokumentiert.*",
        "",
        "## Row-Level Security (RLS)",
        "",
        perm.rls_details or "*Nicht konfiguriert / dokumentiert.*",
        "",
        "## Freigabe & Sharing",
        "",
        perm.sharing_permissions or "*Nicht dokumentiert.*",
        "",
        "## Datensensitivität / Klassifizierung",
        "",
        perm.data_sensitivity or "*Nicht dokumentiert.*",
        "",
        "## Erforderliche Rollen für Änderungen",
        "",
        perm.required_roles_for_changes or "*Nicht dokumentiert.*",
        "",
        "## Service Principal / App-Registrierung",
        "",
        perm.service_principal or "*Nicht konfiguriert.*",
        "",
    ]
    if perm.notes:
        lines += ["## Anmerkungen", "", perm.notes, ""]
    return "\n".join(lines)


def gen_storage(p: Project) -> str:
    st = p.storage_structure
    lines = [
        "# Ablagestruktur",
        "",
        "## Best Practices",
        "",
        "- Speichere PBIX-Dateien nie auf lokalen Laufwerken ohne Backup",
        "- Nutze SharePoint/OneDrive oder ein Git-Repository fuer Versionierung",
        "- Trenne Entwicklungs-, Test- und Produktionsumgebungen",
        "- Verwende Deployment Pipelines fuer kontrollierte Releases",
        "- Erstelle regelmaessige Backups der PBIX-Datei vor groesseren Aenderungen",
        "",
        "## PBIX-Speicherort",
        "",
        st.pbix_location or "*Nicht dokumentiert.*",
        "",
        "## Power BI Workspace",
        "",
        st.workspace_name or "*Nicht dokumentiert.*",
        "",
        "## SharePoint- / OneDrive-Pfad",
        "",
        st.sharepoint_path or "*Nicht dokumentiert.*",
        "",
        "## Data Gateway",
        "",
        st.data_gateway or "*Nicht konfiguriert.*",
        "",
        "## Backup-Strategie / Versionierung",
        "",
        st.backup_strategy or "*Nicht dokumentiert.*",
        "",
        "## Deployment Pipeline",
        "",
        st.deployment_pipeline or "*Nicht konfiguriert.*",
        "",
        "## Git-Repository",
        "",
        st.repo_url or "*Nicht konfiguriert.*",
        "",
    ]
    if st.notes:
        lines += ["## Anmerkungen", "", st.notes, ""]
    return "\n".join(lines)


def gen_naming_conventions(p: Project) -> str:
    nc = p.naming_conventions
    lines = [
        "# Namenskonzept",
        "",
        "## Best Practices",
        "",
        "- Verwende konsistente, sprechende Benennungen in einer einheitlichen Sprache",
        "- Nutze Praefix-Konventionen (z.B. `_` fuer Hilfsmeasures, `dim_` fuer Dimensionen)",
        "- Vermeide Leerzeichen und Sonderzeichen in technischen Namen",
        "- Gruppiere Measures in Display Folders nach Themengebiet",
        "- Dokumentiere alle Abweichungen von den Namensregeln",
        "",
        "## Allgemeine Regeln",
        "",
        nc.general_rules or "*Nicht dokumentiert.*",
        "",
        "## Measures",
        "",
        nc.measures or "*Nicht dokumentiert.*",
        "",
        "## Tabellen",
        "",
        nc.tables or "*Nicht dokumentiert.*",
        "",
        "## Spalten",
        "",
        nc.columns or "*Nicht dokumentiert.*",
        "",
        "## Berichtsseiten",
        "",
        nc.pages or "*Nicht dokumentiert.*",
        "",
        "## Berichte / Dateien",
        "",
        nc.reports or "*Nicht dokumentiert.*",
        "",
        "## Power Queries",
        "",
        nc.queries or "*Nicht dokumentiert.*",
        "",
    ]
    if nc.notes:
        lines += ["## Anmerkungen", "", nc.notes, ""]
    return "\n".join(lines)


def gen_change_guidance(p: Project) -> str:
    cg = p.change_guidance
    lines = [
        "# Änderungshinweise & Best Practices",
        "",
        "## Best Practices für Änderungen am Bericht",
        "",
        "- Erstelle immer ein Backup der PBIX-Datei vor Änderungen",
        "- Teste Änderungen in einer Entwicklungsumgebung vor dem Deployment",
        "- Dokumentiere jede Änderung im Änderungsprotokoll",
        "- Stimme grössere Änderungen vorher mit dem Eigentümer ab",
        "- Prüfe nach Änderungen alle betroffenen Measures und Visuals",
        "- Validiere die Datenaktualisierung nach Modell-Änderungen",
        "",
        "## Vor Änderungen zu beachten",
        "",
        cg.before_changes or "*Nicht dokumentiert.*",
        "",
        "## Test-Checkliste",
        "",
        cg.testing_checklist or "*Nicht dokumentiert.*",
        "",
        "## Deployment-Schritte",
        "",
        cg.deployment_steps or "*Nicht dokumentiert.*",
        "",
        "## Rollback-Plan",
        "",
        cg.rollback_plan or "*Nicht dokumentiert.*",
        "",
        "## Ansprechpartner",
        "",
        cg.contact_persons or "*Nicht dokumentiert.*",
        "",
    ]
    if cg.notes:
        lines += ["## Anmerkungen", "", cg.notes, ""]
    return "\n".join(lines)


# ===================================================================
# Main generator entry point
# ===================================================================

def generate_docs(project: Project, output_dir: Path | None = None) -> Path:
    """Generate the full /docs folder. Returns the output directory path."""
    root = output_dir or DOCS_ROOT
    files = {
        root / "index.md": gen_index(project),
        root / "01_overview" / "overview.md": gen_overview(project),
        root / "01_overview" / "kpis.md": gen_kpis(project),
        root / "02_data_sources" / "data_sources.md": gen_data_sources(project),
        root / "03_power_query" / "queries.md": gen_queries(project),
        root / "04_data_model" / "data_model.md": gen_data_model(project),
        root / "05_measures" / "measures.md": gen_measures(project),
        root / "06_report_design" / "pages_visuals.md": gen_pages_visuals(project),
        root / "07_governance" / "refresh_gateway_rls.md": gen_refresh_gateway_rls(project),
        root / "07_governance" / "assumptions_limitations.md": gen_assumptions_limitations(project),
        root / "08_change_log" / "change_log.md": gen_change_log(project),
        root / "09_permissions" / "permissions.md": gen_permissions(project),
        root / "10_storage" / "storage.md": gen_storage(project),
        root / "11_naming" / "naming_conventions.md": gen_naming_conventions(project),
        root / "12_change_guidance" / "change_guidance.md": gen_change_guidance(project),
    }
    for fpath, content in files.items():
        _write(fpath, content)

    return root
