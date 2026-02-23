"""
Interactive CLI prompts for collecting documentation data.

Supports multi-line paste mode (<<< … >>>) for code blocks.
All user-facing prompts are in German.
"""

from __future__ import annotations

import sys
from typing import List, Optional, Callable

from .models import (
    Project, ProjectMeta, Environment, KPI, DataSource,
    PowerQuery, DataModel, ModelTable, ModelRelationship,
    Measure, Visual, ReportPage, Governance, ChangeLogEntry,
    _today,
)


# ---------------------------------------------------------------------------
# Low-level input helpers
# ---------------------------------------------------------------------------

def _input(prompt: str, default: str = "", required: bool = False) -> str:
    """Single-line input with optional default."""
    suffix = f" [{default}]" if default else ""
    req = " *" if required else ""
    while True:
        val = input(f"  {prompt}{req}{suffix}: ").strip()
        if not val and default:
            return default
        if not val and required:
            print("  ⚠  Dieses Feld ist erforderlich.")
            continue
        return val


def _input_bool(prompt: str, default: bool = False) -> bool:
    d = "J/n" if default else "j/N"
    val = input(f"  {prompt} [{d}]: ").strip().lower()
    if not val:
        return default
    return val in ("j", "ja", "y", "yes", "1", "true")


def _input_multiline(prompt: str) -> str:
    """
    Multi-line input.  The user types <<< to start and >>> to finish.
    If the first line does NOT start with <<<, treat as single line.
    """
    first = input(f"  {prompt} (für Mehrzeiler <<< eingeben): ").strip()
    if first != "<<<":
        return first
    print("  📋 Mehrzeiliger Modus – Einfügen und mit >>> auf eigener Zeile beenden:")
    lines: list[str] = []
    while True:
        line = input()
        if line.strip() == ">>>":
            break
        lines.append(line)
    return "\n".join(lines)


def _section_header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Section prompts
# ---------------------------------------------------------------------------

def prompt_project_meta(existing: ProjectMeta | None = None) -> ProjectMeta:
    """Collect project / report metadata (Section A)."""
    _section_header("A) Projekt- / Bericht-Metadaten")
    m = existing or ProjectMeta()
    m.report_name = _input("Berichtsname", m.report_name, required=True)
    m.short_description = _input("Kurzbeschreibung", m.short_description)
    m.audience = _input("Zielgruppe", m.audience)
    m.owner = _input("Eigentümer", m.owner)
    m.author = _input("Autor", m.author)
    m.version = _input("Version", m.version or "0.1.0")
    m.date = _input("Datum (YYYY-MM-DD)", m.date or _today())
    m.powerbi_service_url = _input("Power BI Service URL", m.powerbi_service_url)
    m.sharepoint_folder_url = _input("SharePoint-Ordner URL", m.sharepoint_folder_url)

    # Environments
    if _input_bool("Umgebungen hinzufügen/bearbeiten?", default=bool(not m.environments)):
        m.environments = []
        for env_name in ("DEV", "TEST", "PROD"):
            if _input_bool(f"  Umgebung '{env_name}' hinzufügen?", default=True):
                ws = _input(f"    Arbeitsbereich für {env_name}")
                url = _input(f"    URL für {env_name}")
                m.environments.append(Environment(name=env_name, workspace=ws, url=url))
    return m


def prompt_kpi(existing: KPI | None = None) -> KPI:
    """Collect a single KPI definition (Section B)."""
    _section_header("B) KPI / Kennzahl hinzufügen")
    k = existing or KPI()
    k.name = _input("KPI-Name", k.name, required=True)
    k.business_description = _input("Fachliche Beschreibung", k.business_description, required=True)
    k.technical_definition = _input_multiline("Technische Definition (Überblick)")
    k.granularity = _input("Granularität (Woche/Monat/Person/…)", k.granularity)
    k.filters_context = _input("Filter / Kontexthinweise", k.filters_context)
    k.caveats = _input("Einschränkungen / Bekannte Probleme", k.caveats)
    return k


def prompt_data_source(existing: DataSource | None = None) -> DataSource:
    """Collect a single data source (Section C)."""
    _section_header("C) Datenquelle hinzufügen")
    s = existing or DataSource()
    s.name = _input("Quellenname", s.name, required=True)
    s.source_type = _input("Typ (SQL/API/Excel/SharePoint/…)", s.source_type, required=True)
    s.connection_info = _input("Verbindungsinfo (Host/DB/View – keine Passwörter!)", s.connection_info)
    s.refresh_cadence = _input("Aktualisierungsrhythmus", s.refresh_cadence)
    s.gateway_required = _input_bool("Gateway erforderlich?", s.gateway_required)
    if s.gateway_required:
        s.gateway_name = _input("Gateway-Name", s.gateway_name)
    s.owner_contact = _input("Verantwortlich / Kontakt", s.owner_contact)
    return s


def prompt_power_query(existing: PowerQuery | None = None) -> PowerQuery:
    """Collect a single Power Query doc (Section D)."""
    _section_header("D) Power Query (M) Abfrage dokumentieren")
    q = existing or PowerQuery()
    q.query_name = _input("Abfragename", q.query_name, required=True)
    q.purpose = _input("Zweck", q.purpose)
    q.inputs = _input("Eingaben", q.inputs)
    q.major_transformations = _input_multiline("Wichtige Transformationen (Beschreibung)")
    q.m_code = _input_multiline("M-Code (optional, für Mehrzeiler <<<)")
    q.output_table = _input("Ausgabetabelle", q.output_table)
    q.notes = _input("Hinweise (Joins, Filter, Schlüssel)", q.notes)
    return q


def prompt_data_model(existing: DataModel | None = None) -> DataModel:
    """Collect data model information (Section E)."""
    _section_header("E) Datenmodell dokumentieren")
    dm = existing or DataModel()

    # Tables
    if _input_bool("Tabellen hinzufügen?", default=True):
        while True:
            t = ModelTable()
            t.name = _input("Tabellenname (leer = fertig)", "")
            if not t.name:
                break
            t.table_type = _input("Typ (Fakt/Dimension/Bridge/Sonstig)", "Dimension")
            t.description = _input("Beschreibung")
            t.keys = _input("Schlüssel (PK/SK)")
            dm.tables.append(t)

    # Relationships
    if _input_bool("Beziehungen hinzufügen?", default=True):
        while True:
            r = ModelRelationship()
            r.from_table = _input("Von-Tabelle (leer = fertig)", "")
            if not r.from_table:
                break
            r.from_column = _input("Von-Spalte", required=True)
            r.to_table = _input("Nach-Tabelle", required=True)
            r.to_column = _input("Nach-Spalte", required=True)
            r.cardinality = _input("Kardinalität (1:N, N:1, 1:1, N:N)", "1:N")
            r.filter_direction = _input("Filterrichtung (Single/Both)", "Single")
            dm.relationships.append(r)

    dm.date_logic_notes = _input_multiline("Datumslogik-Hinweise (ISO-Woche, YearWeekKey, …)")
    dm.notes = _input_multiline("Allgemeine Modell-Hinweise")

    if _input_bool("Screenshot-Pfad hinzufügen?", default=False):
        while True:
            sp = _input("Screenshot-Pfad (leer = fertig)")
            if not sp:
                break
            dm.screenshot_paths.append(sp)

    return dm


def prompt_measure(existing: Measure | None = None) -> Measure:
    """Collect a single DAX measure (Section F)."""
    _section_header("F) Measure (DAX) hinzufügen")
    ms = existing or Measure()
    ms.name = _input("Measure-Name", ms.name, required=True)
    ms.display_folder = _input("Anzeigeordner", ms.display_folder)
    ms.description = _input("Beschreibung", ms.description)
    ms.dax_code = _input_multiline("DAX-Code (Pflichtfeld, für Mehrzeiler <<<)")
    while not ms.dax_code.strip():
        print("  ⚠  DAX-Code ist erforderlich.")
        ms.dax_code = _input_multiline("DAX-Code")
    ms.dependencies = _input("Abhängigkeiten (andere Measures/Tabellen)", ms.dependencies)
    ms.filter_context_notes = _input("Filter-/Kontextverhalten", ms.filter_context_notes)
    ms.validation_notes = _input("Validierungshinweise", ms.validation_notes)
    return ms


def prompt_report_page(existing: ReportPage | None = None) -> ReportPage:
    """Collect a single report page (Section G)."""
    _section_header("G) Berichtsseite / Visuals hinzufügen")
    pg = existing or ReportPage()
    pg.page_name = _input("Seitenname", pg.page_name, required=True)
    pg.purpose = _input("Zweck der Seite", pg.purpose)

    if _input_bool("Visuals hinzufügen?", default=True):
        while True:
            v = Visual()
            v.name = _input("Visual-Name (leer = fertig)")
            if not v.name:
                break
            v.description = _input("Was zeigt dieses Visual?")
            pg.visuals.append(v)

    pg.slicers_filters = _input("Slicer / Filter auf dieser Seite", pg.slicers_filters)
    pg.notes = _input("Hinweise (Tooltips, Drillthrough, Bookmarks)", pg.notes)
    return pg


def prompt_governance(existing: Governance | None = None) -> Governance:
    """Collect governance info (Section H)."""
    _section_header("H) Governance")
    g = existing or Governance()
    g.refresh_schedule = _input_multiline("Aktualisierungsplan")
    g.monitoring_notes = _input_multiline("Monitoring-Hinweise")
    g.rls_notes = _input_multiline("RLS-Hinweise")
    g.performance_notes = _input_multiline("Performance-Hinweise")
    g.assumptions = _input_multiline("Annahmen")
    g.limitations = _input_multiline("Einschränkungen")
    return g


def prompt_change_log_entry(existing: ChangeLogEntry | None = None) -> ChangeLogEntry:
    """Collect a single change log entry (Section I)."""
    _section_header("I) Änderungsprotokoll-Eintrag")
    c = existing or ChangeLogEntry()
    c.version = _input("Version", c.version, required=True)
    c.date = _input("Datum (YYYY-MM-DD)", c.date or _today())
    c.description = _input("Beschreibung der Änderung", c.description, required=True)
    c.author = _input("Autor", c.author)
    c.impact = _input("Auswirkung (minor/major/breaking)", c.impact or "minor")
    c.ticket_link = _input("Ticket / Link", c.ticket_link)
    return c
