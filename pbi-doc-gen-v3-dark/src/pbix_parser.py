"""
PBIX-Direkt-Import – pure Python, keine externen Tools.

Eine .pbix-Datei ist ein ZIP-Archiv mit folgender Struktur:
  - Report/Layout          (JSON – Seiten, Visuals, Slicer)
  - DataMashup             (ZIP-in-ZIP, OPC Package mit M-Code)
  - DataModelSchema        (JSON – optionales Tabellenschema, neuere Versionen)
  - [Content_Types].xml    (OPC-Manifest, ignoriert)

Hinweis: DAX-Measures und Relationships koennen aus .pbix NICHT ohne
externes Tool (pbi-tools / Tabular Editor) extrahiert werden.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable, Match

from .models import (
    ReportPage, Visual, PowerQuery, DataSource, ModelTable, _new_id,
)

# ══════════════════════════════════════════════════════════════════
# Visual-Type-Mapping
# ══════════════════════════════════════════════════════════════════

VISUAL_TYPE_MAP: dict[str, str] = {
    "clusteredBarChart": "Balkendiagramm (gruppiert)",
    "clusteredColumnChart": "Saeulendiagramm (gruppiert)",
    "stackedBarChart": "Balkendiagramm (gestapelt)",
    "stackedColumnChart": "Saeulendiagramm (gestapelt)",
    "hundredPercentStackedBarChart": "Balkendiagramm (100 % gestapelt)",
    "hundredPercentStackedColumnChart": "Saeulendiagramm (100 % gestapelt)",
    "lineChart": "Liniendiagramm",
    "areaChart": "Flaechendiagramm",
    "stackedAreaChart": "Flaechendiagramm (gestapelt)",
    "lineStackedColumnComboChart": "Kombidiagramm (Linie + Saeule)",
    "lineClusteredColumnComboChart": "Kombidiagramm (Linie + gruppierte Saeule)",
    "pieChart": "Kreisdiagramm",
    "donutChart": "Ringdiagramm",
    "treemap": "Treemap",
    "waterfallChart": "Wasserfalldiagramm",
    "funnel": "Trichterdiagramm",
    "scatterChart": "Streudiagramm",
    "card": "Karte (einzelner Wert)",
    "multiRowCard": "Karte (mehrere Zeilen)",
    "kpi": "KPI-Visual",
    "gauge": "Tachometerdiagramm",
    "slicer": "Slicer / Filter",
    "tableEx": "Tabelle",
    "pivotTable": "Matrix / Pivot",
    "map": "Karte (geografisch)",
    "filledMap": "Choroplethenkarte",
    "shape": "Form",
    "textbox": "Textfeld",
    "image": "Bild",
    "actionButton": "Schaltflaeche",
    "bookmarkNavigator": "Lesezeichen-Navigator",
    "decompositionTreeVisual": "Analysebaum",
    "keyDriversVisual": "Key Influencers",
    "qnaVisual": "Q&A Visual",
    "ribbonChart": "Menueband-Diagramm",
    "scriptVisual": "R/Python Visual",
    "ArcGISMap": "ArcGIS-Karte",
    "paginator": "Seitennavigator",
}


def _visual_type_label(raw: str) -> str:
    """Menschenlesbaren Namen fuer einen Visual-Typ zurueckgeben."""
    return VISUAL_TYPE_MAP.get(raw, raw)


# ══════════════════════════════════════════════════════════════════
# M-Code Datenquellen-Patterns
# ══════════════════════════════════════════════════════════════════

def _make_source_patterns() -> list[tuple[re.Pattern, Callable[[Match], DataSource]]]:
    """Erzeugt kompilierte Regex fuer Datenquellen-Erkennung aus M-Code."""
    return [
        (re.compile(r'Sql\.Database\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"'),
         lambda m: DataSource(source_type="SQL",
                              connection_info=f"{m.group(1)}/{m.group(2)}",
                              name=m.group(2),
                              gateway_required=True)),
        (re.compile(r'SapHana\.Database\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="SAP HANA",
                              connection_info=m.group(1),
                              name=f"SAP HANA: {m.group(1)}",
                              gateway_required=True)),
        (re.compile(r'Excel\.Workbook\s*\(\s*File\.Contents\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="Excel",
                              connection_info=m.group(1),
                              name=Path(m.group(1)).stem)),
        (re.compile(r'SharePoint\.Tables\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="SharePoint List",
                              connection_info=m.group(1),
                              name="SharePoint")),
        (re.compile(r'SharePoint\.Files\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="SharePoint Files",
                              connection_info=m.group(1),
                              name="SharePoint Files")),
        (re.compile(r'Web\.Contents\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="API/Web",
                              connection_info=m.group(1),
                              name="Web API")),
        (re.compile(r'OData\.Feed\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="OData",
                              connection_info=m.group(1),
                              name="OData Feed")),
        (re.compile(r'Csv\.Document\s*\(\s*File\.Contents\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="CSV",
                              connection_info=m.group(1),
                              name=Path(m.group(1)).stem)),
        (re.compile(r'Oracle\.Database\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="Oracle",
                              connection_info=m.group(1),
                              name=f"Oracle: {m.group(1)}",
                              gateway_required=True)),
        (re.compile(r'Odbc\.DataSource\s*\(\s*"([^"]+)"'),
         lambda m: DataSource(source_type="ODBC",
                              connection_info=m.group(1),
                              name="ODBC",
                              gateway_required=True)),
        (re.compile(r'AnalysisServices\.Database\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"'),
         lambda m: DataSource(source_type="SSAS",
                              connection_info=f"{m.group(1)}/{m.group(2)}",
                              name=m.group(2),
                              gateway_required=True)),
        (re.compile(r'Dataverse\.Contents\s*\(\s*"([^"]*)"'),
         lambda m: DataSource(source_type="Dataverse",
                              connection_info=m.group(1) or "Default",
                              name="Dataverse")),
    ]


SOURCE_PATTERNS = _make_source_patterns()

# On-Premises-Quellen, die typischerweise ein Gateway erfordern
_ONPREM_TYPES = {"SQL", "SAP HANA", "Oracle", "ODBC", "SSAS"}


# ══════════════════════════════════════════════════════════════════
# Import-Ergebnis
# ══════════════════════════════════════════════════════════════════

@dataclass
class PbixImportResult:
    """Strukturiertes Ergebnis des PBIX-Parsers."""
    report_pages: List[ReportPage] = field(default_factory=list)
    power_queries: List[PowerQuery] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    tables: List[ModelTable] = field(default_factory=list)
    report_name: str = ""
    warnings: List[str] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════
# Report/Layout parsen
# ══════════════════════════════════════════════════════════════════

def _parse_layout(layout_json: dict, warnings: List[str]) -> tuple[List[ReportPage], str]:
    """Parst die Seitenstruktur aus dem Report/Layout JSON."""
    pages: List[ReportPage] = []
    report_name = ""

    # Reportname aus Metadaten
    try:
        config = layout_json.get("config", "")
        if isinstance(config, str) and config:
            cfg = json.loads(config)
            report_name = cfg.get("name", "") or cfg.get("displayName", "")
    except Exception:
        pass

    sections = layout_json.get("sections", [])
    if not sections:
        warnings.append("Report/Layout enthaelt keine Seiten (sections).")
        return pages, report_name

    for section in sections:
        try:
            page = _parse_section(section, warnings)
            pages.append(page)
        except Exception as exc:
            sec_name = section.get("displayName", section.get("name", "?"))
            warnings.append(f"Seite '{sec_name}' konnte nicht verarbeitet werden: {exc}")

    return pages, report_name


def _parse_section(section: dict, warnings: List[str]) -> ReportPage:
    """Einzelne Berichtsseite parsen."""
    display_name = section.get("displayName", section.get("name", "Unbenannt"))
    visuals: List[Visual] = []
    slicers: List[str] = []

    containers = section.get("visualContainers", [])
    for vc in containers:
        try:
            config_str = vc.get("config", "")
            if not config_str:
                continue
            if isinstance(config_str, str):
                config = json.loads(config_str)
            else:
                config = config_str

            sv = config.get("singleVisual", {})
            if not sv:
                continue

            visual_type_raw = sv.get("visualType", "unknown")
            visual_type_label = _visual_type_label(visual_type_raw)

            # Felder extrahieren
            projections = sv.get("projections", {})
            field_refs = _extract_field_refs(projections)
            field_str = ", ".join(field_refs) if field_refs else ""

            # Name zusammenbauen
            title = ""
            obj = sv.get("objects", {})
            if obj:
                title_props = obj.get("title", [{}])
                if isinstance(title_props, list) and title_props:
                    props = title_props[0].get("properties", {})
                    text_prop = props.get("text", {})
                    if isinstance(text_prop, dict):
                        title = text_prop.get("expr", {}).get("Literal", {}).get("Value", "")
                        if title.startswith("'") and title.endswith("'"):
                            title = title[1:-1]

            visual_name = title or visual_type_label
            desc_parts = [f"Typ: {visual_type_label}"]
            if field_str:
                desc_parts.append(f"Felder: {field_str}")

            if visual_type_raw == "slicer":
                slicer_desc = f"{visual_name}"
                if field_str:
                    slicer_desc += f" ({field_str})"
                slicers.append(slicer_desc)
            else:
                visuals.append(Visual(
                    name=visual_name,
                    description=" | ".join(desc_parts),
                ))
        except Exception as exc:
            warnings.append(f"Visual auf Seite '{display_name}' uebersprungen: {exc}")

    slicer_text = "; ".join(slicers) if slicers else ""

    return ReportPage(
        page_name=display_name,
        visuals=visuals,
        slicers_filters=slicer_text,
    )


def _extract_field_refs(projections: dict) -> List[str]:
    """Feldnamen aus projections-Objekt extrahieren."""
    refs: List[str] = []
    if not isinstance(projections, dict):
        return refs
    for _role, items in projections.items():
        if not isinstance(items, list):
            continue
        for item in items:
            qr = item.get("queryRef", "")
            if qr:
                refs.append(qr)
    return refs


# ══════════════════════════════════════════════════════════════════
# DataMashup parsen (ZIP-in-ZIP mit M-Code)
# ══════════════════════════════════════════════════════════════════

def _parse_datamashup(raw: bytes, warnings: List[str]) -> tuple[List[PowerQuery], List[DataSource]]:
    """
    DataMashup ist ein OPC-Package (ZIP).
    Darin: Formulas/Section1.m  enthaelt alle Power Query Abfragen.
    """
    queries: List[PowerQuery] = []
    sources: List[DataSource] = []

    # DataMashup beginnt mit einem 4-byte oder 8-byte Header, danach kommt das ZIP.
    # Wir suchen die ZIP-Signatur.
    zip_start = raw.find(b"PK\x03\x04")
    if zip_start < 0:
        warnings.append("DataMashup: Kein ZIP-Archiv gefunden.")
        return queries, sources

    mashup_bytes = raw[zip_start:]
    try:
        with zipfile.ZipFile(io.BytesIO(mashup_bytes)) as inner_zip:
            m_code = _read_section1_m(inner_zip, warnings)
    except zipfile.BadZipFile:
        warnings.append("DataMashup: ZIP konnte nicht gelesen werden.")
        return queries, sources

    if not m_code:
        warnings.append("DataMashup: Kein M-Code (Section1.m) gefunden.")
        return queries, sources

    queries = _split_m_queries(m_code)
    sources = _detect_sources(m_code)

    return queries, sources


def _read_section1_m(zf: zipfile.ZipFile, warnings: List[str]) -> str:
    """Liest den M-Code aus dem Mashup-ZIP."""
    # Verschiedene Pfade in verschiedenen PBI-Versionen
    candidates = [
        "Formulas/Section1.m",
        "Section1.m",
        "Formulas/Section1.m/Section1.m",
    ]
    for name in zf.namelist():
        if name.lower().endswith("section1.m"):
            candidates.insert(0, name)

    for candidate in candidates:
        try:
            raw = zf.read(candidate)
            # Versuche verschiedene Encodings
            for encoding in ("utf-8", "utf-16-le", "utf-16-be", "latin-1"):
                try:
                    text = raw.decode(encoding)
                    if "shared" in text.lower() or "let" in text.lower() or "section" in text.lower():
                        return text
                except (UnicodeDecodeError, UnicodeError):
                    continue
        except KeyError:
            continue

    warnings.append("DataMashup: Section1.m nicht in erwartetem Pfad gefunden.")
    return ""


def _split_m_queries(m_code: str) -> List[PowerQuery]:
    """Trennt shared-Statements in einzelne Queries auf."""
    queries: List[PowerQuery] = []

    # Pattern: shared QueryName = ... ;
    # Erlaubt mehrzeiliges Matching bis zum naechsten ; auf Top-Level
    pattern = re.compile(
        r'shared\s+#?"?([^"=\s]+)"?\s*=\s*(.*?);',
        re.DOTALL,
    )
    matches = list(pattern.finditer(m_code))

    if matches:
        for match in matches:
            name = match.group(1).strip().strip('"')
            code = match.group(2).strip()
            queries.append(PowerQuery(
                query_name=name,
                m_code=code,
                output_table=name,
            ))
    else:
        # Fallback: ganzen Code als eine Query
        clean = m_code.strip()
        if clean:
            # Versuche "section Section1;" Header zu entfernen
            clean = re.sub(r'^section\s+\w+\s*;', '', clean, flags=re.IGNORECASE).strip()
            if clean:
                queries.append(PowerQuery(
                    query_name="Hauptabfrage",
                    m_code=clean,
                    output_table="Hauptabfrage",
                ))

    return queries


def _detect_sources(m_code: str) -> List[DataSource]:
    """Erkennt Datenquellen aus dem M-Code anhand bekannter Muster."""
    sources: List[DataSource] = []
    seen: set[str] = set()  # Duplikaterkennung ueber connection_info

    for pattern, factory in SOURCE_PATTERNS:
        for match in pattern.finditer(m_code):
            ds = factory(match)
            key = f"{ds.source_type}::{ds.connection_info}"
            if key not in seen:
                seen.add(key)
                # Gateway-Erkennung
                if ds.source_type in _ONPREM_TYPES:
                    ds.gateway_required = True
                sources.append(ds)

    return sources


# ══════════════════════════════════════════════════════════════════
# DataModelSchema parsen (optional, neuere pbix-Versionen)
# ══════════════════════════════════════════════════════════════════

def _parse_data_model_schema(raw: bytes, warnings: List[str]) -> List[ModelTable]:
    """Parst DataModelSchema JSON fuer Tabellenmetadaten."""
    tables: List[ModelTable] = []
    try:
        # Encoding: kann UTF-16-LE mit BOM sein
        for enc in ("utf-8-sig", "utf-16-le", "utf-16-be", "utf-8", "latin-1"):
            try:
                text = raw.decode(enc)
                schema = json.loads(text)
                break
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        else:
            warnings.append("DataModelSchema: Encoding nicht erkannt.")
            return tables

        model = schema.get("model", schema)
        for tbl in model.get("tables", []):
            name = tbl.get("name", "")
            if not name or name.startswith("LocalDateTable") or name.startswith("DateTableTemplate"):
                continue
            cols = tbl.get("columns", [])
            col_names = [c.get("name", "") for c in cols if c.get("name")]
            keys = [c.get("name", "") for c in cols if c.get("isKey")]

            key_str = f"PK: {', '.join(keys)}" if keys else ""
            desc = f"Spalten: {', '.join(col_names[:10])}"
            if len(col_names) > 10:
                desc += f" (+{len(col_names) - 10} weitere)"

            tables.append(ModelTable(
                name=name,
                description=desc,
                keys=key_str,
            ))
    except Exception as exc:
        warnings.append(f"DataModelSchema: Fehler beim Parsen: {exc}")

    return tables


# ══════════════════════════════════════════════════════════════════
# Hauptfunktion
# ══════════════════════════════════════════════════════════════════

def parse_pbix(pbix_path: Path) -> PbixImportResult:
    """
    Parst eine .pbix-Datei und gibt ein strukturiertes Ergebnis zurueck.
    Kein externes Tool noetig – pure Python mit zipfile + json.

    Unterstuetzt auch .pbit (Power BI Template, gleiche Struktur).
    """
    result = PbixImportResult()

    if not pbix_path.exists():
        result.warnings.append(f"Datei nicht gefunden: {pbix_path}")
        return result

    try:
        with zipfile.ZipFile(str(pbix_path), "r") as zf:
            names = zf.namelist()

            # ── Report/Layout ─────────────────────────────
            layout_data = None
            for candidate in ("Report/Layout", "Report\\Layout"):
                if candidate in names:
                    try:
                        raw = zf.read(candidate)
                        # Layout kann UTF-16-LE mit BOM sein
                        for enc in ("utf-16-le", "utf-8-sig", "utf-8"):
                            try:
                                text = raw.decode(enc)
                                layout_data = json.loads(text)
                                break
                            except (UnicodeDecodeError, json.JSONDecodeError):
                                continue
                    except Exception as exc:
                        result.warnings.append(f"Report/Layout Lesefehler: {exc}")
                    break

            if layout_data:
                pages, rname = _parse_layout(layout_data, result.warnings)
                result.report_pages = pages
                if rname:
                    result.report_name = rname
            else:
                result.warnings.append("Report/Layout nicht gefunden oder nicht lesbar.")

            # Fallback: Dateiname als Reportname
            if not result.report_name:
                result.report_name = pbix_path.stem

            # ── DataMashup ────────────────────────────────
            mashup_raw = None
            for candidate in ("DataMashup", "DataMashup/DataMashup"):
                if candidate in names:
                    try:
                        mashup_raw = zf.read(candidate)
                    except Exception as exc:
                        result.warnings.append(f"DataMashup Lesefehler: {exc}")
                    break

            if mashup_raw:
                queries, sources = _parse_datamashup(mashup_raw, result.warnings)
                result.power_queries = queries
                result.data_sources = sources
            else:
                result.warnings.append("DataMashup nicht gefunden – Power Queries nicht verfuegbar.")

            # ── DataModelSchema (optional) ─────────────────
            for candidate in ("DataModelSchema", "DataModelSchema/DataModelSchema"):
                if candidate in names:
                    try:
                        schema_raw = zf.read(candidate)
                        result.tables = _parse_data_model_schema(schema_raw, result.warnings)
                    except Exception as exc:
                        result.warnings.append(f"DataModelSchema Lesefehler: {exc}")
                    break

    except zipfile.BadZipFile:
        result.warnings.append(f"'{pbix_path.name}' ist kein gueltiges ZIP-Archiv.")
    except Exception as exc:
        result.warnings.append(f"Allgemeiner Fehler: {exc}")

    return result
