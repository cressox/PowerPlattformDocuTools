"""
Import-Manager – Orchestrierung und Merge-Logik.

Zentrale Schnittstelle fuer den Import von .pbix, .bim, .pbit und .json
Dateien in das bestehende Projekt-Datenmodell.

Unterstuetzte Merge-Modi:
  - replace: Bestehende Daten komplett ersetzen
  - merge:   Nur fehlende Eintraege ergaenzen (bestehende behalten)
  - append:  Alles hinzufuegen (Duplikate moeglich)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .models import (
    Project, KPI, Measure, DataSource, PowerQuery,
    ModelTable, ModelRelationship, ReportPage, _new_id,
)
from .pbix_parser import PbixImportResult, parse_pbix
from .bim_parser import BimImportResult, parse_bim, is_bim_format
from .pbitools_parser import pbitools_available, parse_pbix_with_pbitools


# ══════════════════════════════════════════════════════════════════
# Optionen und Ergebnis
# ══════════════════════════════════════════════════════════════════

@dataclass
class ImportOptions:
    """Steuerung des Import-Verhaltens."""
    merge_mode: str = "replace"             # "replace" | "merge" | "append"
    import_measures_as_kpis: bool = False    # Measures auch als KPIs anlegen?
    skip_hidden_tables: bool = True          # Versteckte Tabellen ignorieren?
    skip_hidden_measures: bool = False
    detect_table_types: bool = True          # Heuristik fuer Fakt/Dim-Erkennung
    extract_data_sources: bool = True
    use_pbitools: bool = True               # pbi-tools verwenden falls verfuegbar?


@dataclass
class ImportReport:
    """Bericht ueber den abgeschlossenen Import."""
    success: bool = True
    file_type: str = ""                     # "pbix", "bim", "pbitools", "pbit"
    imported: dict = field(default_factory=dict)   # {"measures": 15, "tables": 8, ...}
    skipped: dict = field(default_factory=dict)    # {"hidden_tables": 3, ...}
    warnings: List[str] = field(default_factory=list)
    not_available: List[str] = field(default_factory=list)

    def summary_text(self) -> str:
        """Menschenlesbare Zusammenfassung."""
        parts: List[str] = []

        if self.imported:
            items = []
            labels = {
                "measures": "Measures",
                "tables": "Tabellen",
                "relationships": "Beziehungen",
                "queries": "Queries",
                "data_sources": "Datenquellen",
                "report_pages": "Berichtsseiten",
                "kpis": "KPIs",
            }
            for key, count in self.imported.items():
                if count > 0:
                    label = labels.get(key, key)
                    items.append(f"{count} {label}")
            if items:
                parts.append("Importiert: " + ", ".join(items) + ".")

        if self.skipped:
            items = []
            for key, count in self.skipped.items():
                if count > 0:
                    items.append(f"{count} {key}")
            if items:
                parts.append("Uebersprungen: " + ", ".join(items) + ".")

        if self.not_available:
            parts.append(
                "⚠️ Nicht verfuegbar bei diesem Dateityp: "
                + ", ".join(self.not_available) + "."
            )

        if self.warnings:
            parts.append(f"⚠️ {len(self.warnings)} Warnung(en).")

        return "\n".join(parts) if parts else "Import abgeschlossen."


# ══════════════════════════════════════════════════════════════════
# Dateityp-Erkennung
# ══════════════════════════════════════════════════════════════════

def detect_file_type(file_path: Path) -> str:
    """
    Erkennt den Dateityp anhand der Endung und des Inhalts.

    Returns: "pbix", "pbit", "bim", "json_bim", "unknown"
    """
    suffix = file_path.suffix.lower()

    if suffix == ".pbix":
        return "pbix"
    elif suffix == ".pbit":
        return "pbit"
    elif suffix == ".bim":
        return "bim"
    elif suffix == ".json":
        if is_bim_format(file_path):
            return "json_bim"
        return "unknown"
    else:
        return "unknown"


# ══════════════════════════════════════════════════════════════════
# Vorschau (Preview ohne Import)
# ══════════════════════════════════════════════════════════════════

@dataclass
class ImportPreview:
    """Vorschau der erkannten Elemente ohne bestehende Daten zu aendern."""
    file_type: str = ""
    report_name: str = ""
    page_count: int = 0
    visual_count: int = 0
    query_count: int = 0
    source_count: int = 0
    measure_count: int = 0
    table_count: int = 0
    relationship_count: int = 0
    has_rls: bool = False
    pbitools_available: bool = False
    warnings: List[str] = field(default_factory=list)
    not_available: List[str] = field(default_factory=list)


def preview_import(file_path: Path) -> ImportPreview:
    """
    Erzeugt eine Vorschau ohne das Projekt zu veraendern.
    Schnelle Analyse fuer den Import-Dialog.
    """
    preview = ImportPreview()
    preview.pbitools_available = pbitools_available()

    ftype = detect_file_type(file_path)
    preview.file_type = ftype

    if ftype in ("pbix", "pbit"):
        result = parse_pbix(file_path)
        preview.report_name = result.report_name
        preview.page_count = len(result.report_pages)
        preview.visual_count = sum(len(p.visuals) for p in result.report_pages)
        preview.query_count = len(result.power_queries)
        preview.source_count = len(result.data_sources)
        preview.table_count = len(result.tables)

        preview.not_available.append("DAX Measures (nur mit .bim oder pbi-tools)")
        preview.not_available.append("Beziehungen (nur mit .bim oder pbi-tools)")
        preview.not_available.append("RLS-Rollen (nur mit .bim oder pbi-tools)")

        if preview.pbitools_available:
            try:
                bim_result = parse_pbix_with_pbitools(file_path)
                preview.measure_count = len(bim_result.measures)
                preview.relationship_count = len(bim_result.relationships)
                preview.table_count = max(preview.table_count, len(bim_result.tables))
                preview.query_count = max(preview.query_count, len(bim_result.power_queries))
                preview.source_count = max(preview.source_count, len(bim_result.data_sources))
                preview.has_rls = bool(bim_result.rls_notes)
                preview.not_available.clear()
                # pbi-tools Warnungen statt PBIX-Parser Warnungen
                preview.warnings = bim_result.warnings
            except Exception:
                # Fallback: PBIX-Parser Warnungen behalten
                preview.warnings = result.warnings
        else:
            preview.warnings = result.warnings

    elif ftype in ("bim", "json_bim"):
        result = parse_bim(file_path)
        preview.report_name = result.report_name
        preview.measure_count = len(result.measures)
        preview.table_count = len(result.tables)
        preview.relationship_count = len(result.relationships)
        preview.query_count = len(result.power_queries)
        preview.source_count = len(result.data_sources)
        preview.has_rls = bool(result.rls_notes)
        preview.warnings = result.warnings

        preview.not_available.append("Berichtsseiten/Visuals (nur in .pbix)")

    else:
        preview.warnings.append(f"Unbekannter Dateityp: {file_path.suffix}")

    return preview


# ══════════════════════════════════════════════════════════════════
# Merge-Logik
# ══════════════════════════════════════════════════════════════════

def _merge_list(existing: list, new_items: list, mode: str, key_attr: str) -> tuple[list, int]:
    """
    Merged eine Liste basierend auf dem Modus.
    Gibt (merged_list, skip_count) zurueck.
    """
    if mode == "replace":
        return list(new_items), 0

    if mode == "append":
        return existing + list(new_items), 0

    # mode == "merge": Nur fehlende ergaenzen
    existing_keys = set()
    for item in existing:
        key = getattr(item, key_attr, "")
        if key:
            existing_keys.add(key.lower())

    merged = list(existing)
    skipped = 0
    for item in new_items:
        key = getattr(item, key_attr, "")
        if key and key.lower() in existing_keys:
            skipped += 1
        else:
            merged.append(item)

    return merged, skipped


# ══════════════════════════════════════════════════════════════════
# Hauptfunktion
# ══════════════════════════════════════════════════════════════════

def import_file(
    file_path: Path,
    project: Project,
    options: Optional[ImportOptions] = None,
) -> ImportReport:
    """
    Zentrale Import-Funktion. Erkennt Dateityp und ruft den richtigen Parser auf.

    Unterstuetzte Dateitypen:
    - .pbix  -> pbix_parser (+ pbitools_parser falls verfuegbar)
    - .bim   -> bim_parser
    - .json  -> Erkennung ob BIM-Format oder pbi-tools-Extrakt
    - .pbit  -> Template, gleiche Struktur wie .pbix

    Args:
        file_path: Pfad zur Importdatei
        project: Bestehendes Projekt (wird in-place modifiziert)
        options: Import-Optionen (Standard: replace-Modus)

    Returns:
        ImportReport mit Zusammenfassung
    """
    if options is None:
        options = ImportOptions()

    report = ImportReport()
    ftype = detect_file_type(file_path)
    report.file_type = ftype

    if ftype == "unknown":
        report.success = False
        report.warnings.append(f"Unbekannter Dateityp: {file_path.suffix}")
        return report

    # ── Parsen ────────────────────────────────────────
    pbix_result: Optional[PbixImportResult] = None
    bim_result: Optional[BimImportResult] = None

    if ftype in ("pbix", "pbit"):
        # Immer erstmal pure Python parsen
        pbix_result = parse_pbix(file_path)

        # pbi-tools falls verfuegbar und gewuenscht
        if options.use_pbitools and pbitools_available():
            try:
                bim_result = parse_pbix_with_pbitools(file_path)
                report.file_type = "pbitools"
                report.warnings.extend(bim_result.warnings)
                # PBIX-Parser-Warnungen unterdruecken – pbi-tools hat alles
            except Exception as exc:
                report.warnings.append(f"pbi-tools Extraktion fehlgeschlagen: {exc}")
                report.warnings.append("Fallback auf reinen PBIX-Parser.")
                report.warnings.extend(pbix_result.warnings)
        else:
            report.warnings.extend(pbix_result.warnings)

    elif ftype in ("bim", "json_bim"):
        bim_result = parse_bim(
            file_path,
            skip_hidden_tables=options.skip_hidden_tables,
            skip_hidden_measures=options.skip_hidden_measures,
            detect_table_types=options.detect_table_types,
        )
        report.warnings.extend(bim_result.warnings)

    # ── Merge in Projekt ──────────────────────────────
    mode = options.merge_mode
    imported = {}
    skipped = {}

    # Report-Name
    name = ""
    if bim_result and bim_result.report_name:
        name = bim_result.report_name
    elif pbix_result and pbix_result.report_name:
        name = pbix_result.report_name
    if name and (mode == "replace" or not project.meta.report_name):
        project.meta.report_name = name

    # ── Report Pages (nur aus PBIX) ──────────────────
    if pbix_result and pbix_result.report_pages:
        merged, skip_count = _merge_list(
            project.report_pages, pbix_result.report_pages,
            mode, "page_name",
        )
        project.report_pages = merged
        imported["report_pages"] = len(pbix_result.report_pages)
        if skip_count:
            skipped["report_pages_existierend"] = skip_count
    elif ftype in ("bim", "json_bim"):
        report.not_available.append("Berichtsseiten/Visuals")

    # ── Tabellen ──────────────────────────────────────
    tables = []
    if bim_result and bim_result.tables:
        tables = bim_result.tables
    elif pbix_result and pbix_result.tables:
        tables = pbix_result.tables

    if tables:
        merged, skip_count = _merge_list(
            project.data_model.tables, tables,
            mode, "name",
        )
        project.data_model.tables = merged
        imported["tables"] = len(tables)
        if skip_count:
            skipped["tabellen_existierend"] = skip_count

    # ── Relationships (nur aus BIM) ───────────────────
    if bim_result and bim_result.relationships:
        if mode == "replace":
            project.data_model.relationships = list(bim_result.relationships)
        elif mode == "append":
            project.data_model.relationships.extend(bim_result.relationships)
        else:  # merge
            existing_keys = set()
            for r in project.data_model.relationships:
                existing_keys.add(f"{r.from_table}.{r.from_column}->{r.to_table}.{r.to_column}")
            for r in bim_result.relationships:
                key = f"{r.from_table}.{r.from_column}->{r.to_table}.{r.to_column}"
                if key not in existing_keys:
                    project.data_model.relationships.append(r)
        imported["relationships"] = len(bim_result.relationships)
    elif ftype in ("pbix", "pbit") and report.file_type != "pbitools":
        report.not_available.append("Beziehungen")

    # ── Measures (nur aus BIM) ────────────────────────
    if bim_result and bim_result.measures:
        merged, skip_count = _merge_list(
            project.measures, bim_result.measures,
            mode, "name",
        )
        project.measures = merged
        imported["measures"] = len(bim_result.measures)
        if skip_count:
            skipped["measures_existierend"] = skip_count

        # Optional: Measures auch als KPIs
        if options.import_measures_as_kpis:
            kpi_count = 0
            for m in bim_result.measures:
                kpi = KPI(
                    name=m.name,
                    business_description=m.description,
                    technical_definition=m.dax_code,
                    filters_context=m.filter_context_notes,
                )
                if mode == "merge":
                    existing_names = {k.name.lower() for k in project.kpis}
                    if kpi.name.lower() not in existing_names:
                        project.kpis.append(kpi)
                        kpi_count += 1
                else:
                    project.kpis.append(kpi)
                    kpi_count += 1
            if kpi_count:
                imported["kpis"] = kpi_count
    elif ftype in ("pbix", "pbit") and report.file_type != "pbitools":
        report.not_available.append("DAX Measures")

    # ── Power Queries ─────────────────────────────────
    queries = []
    if bim_result and bim_result.power_queries:
        queries = bim_result.power_queries
    elif pbix_result and pbix_result.power_queries:
        queries = pbix_result.power_queries

    if queries:
        merged, skip_count = _merge_list(
            project.power_queries, queries,
            mode, "query_name",
        )
        project.power_queries = merged
        imported["queries"] = len(queries)
        if skip_count:
            skipped["queries_existierend"] = skip_count

    # ── Datenquellen ──────────────────────────────────
    if options.extract_data_sources:
        sources = []
        if bim_result and bim_result.data_sources:
            sources = bim_result.data_sources
        elif pbix_result and pbix_result.data_sources:
            sources = pbix_result.data_sources

        if sources:
            merged, skip_count = _merge_list(
                project.data_sources, sources,
                mode, "connection_info",
            )
            project.data_sources = merged
            imported["data_sources"] = len(sources)
            if skip_count:
                skipped["datenquellen_existierend"] = skip_count

    # ── RLS ───────────────────────────────────────────
    if bim_result and bim_result.rls_notes:
        if mode == "replace" or not project.governance.rls_notes:
            project.governance.rls_notes = bim_result.rls_notes

    # ── Date Logic ────────────────────────────────────
    if bim_result and bim_result.date_logic_notes:
        if mode == "replace" or not project.data_model.date_logic_notes:
            project.data_model.date_logic_notes = bim_result.date_logic_notes

    report.imported = imported
    report.skipped = skipped
    return report
