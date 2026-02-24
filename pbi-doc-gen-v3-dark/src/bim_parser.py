"""
BIM/Tabular-Model-Import – JSON-basiert, 100 % Abdeckung.

Eine .bim-Datei ist reines JSON (Tabular Model Definition Language / TMDL).
Sie enthaelt das komplette Datenmodell eines Power BI / SSAS Tabular Models:

- Tabellen mit Spalten, Measures, Partitionen
- Relationships
- RLS-Rollen
- Annotations & Beschreibungen
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from .models import (
    ModelTable, ModelRelationship, Measure, PowerQuery, DataSource, _new_id,
)

# ══════════════════════════════════════════════════════════════════
# Import-Ergebnis
# ══════════════════════════════════════════════════════════════════

@dataclass
class BimImportResult:
    """Strukturiertes Ergebnis des BIM-Parsers."""
    tables: List[ModelTable] = field(default_factory=list)
    relationships: List[ModelRelationship] = field(default_factory=list)
    measures: List[Measure] = field(default_factory=list)
    power_queries: List[PowerQuery] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    rls_notes: str = ""
    report_name: str = ""
    date_logic_notes: str = ""
    warnings: List[str] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════
# Cardinality & Filter-Mapping
# ══════════════════════════════════════════════════════════════════

_CARDINALITY_MAP = {
    "manyToOne": "N:1",
    "oneToMany": "1:N",
    "manyToMany": "N:M",
    "oneToOne": "1:1",
    # Fallback fuer fromCardinality/toCardinality Paare
}

_FILTER_DIR_MAP = {
    "oneDirection": "Single",
    "bothDirections": "Both",
    "automatic": "Single",
}


def _map_cardinality_pair(from_card: str, to_card: str) -> str:
    """Mappt (fromCardinality, toCardinality) Paare auf lesbare Notation."""
    key = f"{from_card}To{to_card.capitalize()}"
    if key in _CARDINALITY_MAP:
        return _CARDINALITY_MAP[key]
    # Direktes Mapping
    combo = f"{from_card}:{to_card}"
    mapping = {
        "many:one": "N:1",
        "one:many": "1:N",
        "many:many": "N:M",
        "one:one": "1:1",
    }
    return mapping.get(combo.lower(), f"{from_card}:{to_card}")


# ══════════════════════════════════════════════════════════════════
# Datenquellen-Erkennung aus M-Code
# ══════════════════════════════════════════════════════════════════

# Import der Patterns aus pbix_parser (fuer Wiederverwendung)
def _detect_sources_from_m(m_code: str) -> List[DataSource]:
    """Erkennt Datenquellen aus M-Code (Wiederverwendung der pbix_parser-Logik)."""
    from .pbix_parser import SOURCE_PATTERNS, _ONPREM_TYPES
    sources: List[DataSource] = []
    seen: set[str] = set()
    for pattern, factory in SOURCE_PATTERNS:
        for match in pattern.finditer(m_code):
            ds = factory(match)
            key = f"{ds.source_type}::{ds.connection_info}"
            if key not in seen:
                seen.add(key)
                if ds.source_type in _ONPREM_TYPES:
                    ds.gateway_required = True
                sources.append(ds)
    return sources


# ══════════════════════════════════════════════════════════════════
# Tabellen parsen
# ══════════════════════════════════════════════════════════════════

def _parse_tables(
    model: dict,
    warnings: List[str],
    skip_hidden: bool = True,
    detect_types: bool = True,
) -> tuple[List[ModelTable], List[Measure], List[PowerQuery], List[DataSource], str]:
    """Parst Tabellen, Measures, Partitionen aus model.tables."""
    tables: List[ModelTable] = []
    measures: List[Measure] = []
    queries: List[PowerQuery] = []
    sources: List[DataSource] = []
    date_logic_parts: List[str] = []
    seen_sources: set[str] = set()

    all_measure_names: Set[str] = set()
    # Sammle zuerst alle Measure-Namen fuer Dependency-Erkennung
    for tbl in model.get("tables", []):
        for m in tbl.get("measures", []):
            name = m.get("name", "")
            if name:
                all_measure_names.add(name)

    for tbl_data in model.get("tables", []):
        try:
            tbl_name = tbl_data.get("name", "")
            if not tbl_name:
                continue

            # System-Tabellen ueberspringen
            if tbl_name.startswith("LocalDateTable") or tbl_name.startswith("DateTableTemplate"):
                continue

            is_hidden = tbl_data.get("isHidden", False)
            if is_hidden and skip_hidden:
                continue

            # Spalten
            columns = tbl_data.get("columns", [])
            col_names = []
            key_cols = []
            has_date_col = False
            numeric_count = 0

            for col in columns:
                col_name = col.get("name", "")
                if not col_name:
                    continue
                col_names.append(col_name)
                if col.get("isKey", False):
                    key_cols.append(col_name)
                dt = col.get("dataType", "").lower()
                if dt in ("dateTime", "datetime"):
                    has_date_col = True
                if col_name.lower() in ("date", "datum"):
                    has_date_col = True
                if dt in ("int64", "double", "decimal"):
                    numeric_count += 1

            key_str = ""
            if key_cols:
                key_str = f"PK: {', '.join(key_cols)}"

            # Beschreibung
            description = tbl_data.get("description", "")
            if not description:
                # Annotations pruefen
                for ann in tbl_data.get("annotations", []):
                    if ann.get("name", "").lower() in ("description", "desc"):
                        description = ann.get("value", "")
                        break

            if not description:
                desc_parts = [f"Spalten: {', '.join(col_names[:8])}"]
                if len(col_names) > 8:
                    desc_parts[0] += f" (+{len(col_names) - 8} weitere)"
                if is_hidden:
                    desc_parts.append("[versteckt]")
                description = " | ".join(desc_parts)

            # Tabellentyp-Heuristik
            table_type = ""
            if detect_types:
                table_type = _detect_table_type(tbl_name, tbl_data, columns, has_date_col)

            # Datumstabellen-Logik
            if table_type == "Kalender" or has_date_col:
                date_cols = [c.get("name", "") for c in columns
                             if c.get("dataType", "").lower() in ("datetime", "dateTime")
                             or c.get("name", "").lower() in ("date", "datum")]
                if date_cols:
                    date_logic_parts.append(
                        f"Datumstabelle '{tbl_name}': Spalten {', '.join(date_cols)}"
                    )

            tables.append(ModelTable(
                name=tbl_name,
                table_type=table_type,
                description=description,
                keys=key_str,
            ))

            # ── Measures ─────────────────────────────
            for m_data in tbl_data.get("measures", []):
                try:
                    m = _parse_measure(m_data, tbl_name, all_measure_names, warnings)
                    if m:
                        measures.append(m)
                except Exception as exc:
                    m_name = m_data.get("name", "?")
                    warnings.append(f"Measure '{m_name}' uebersprungen: {exc}")

            # ── Partitionen -> Power Queries / Data Sources ──
            for part in tbl_data.get("partitions", []):
                try:
                    pq, ds_list = _parse_partition(part, tbl_name, seen_sources, warnings)
                    if pq:
                        queries.append(pq)
                    sources.extend(ds_list)
                except Exception as exc:
                    warnings.append(f"Partition in '{tbl_name}' uebersprungen: {exc}")

        except Exception as exc:
            tbl_name = tbl_data.get("name", "?")
            warnings.append(f"Tabelle '{tbl_name}' uebersprungen: {exc}")

    date_logic = "\n".join(date_logic_parts) if date_logic_parts else ""
    return tables, measures, queries, sources, date_logic


def _detect_table_type(
    name: str,
    tbl_data: dict,
    columns: list,
    has_date_col: bool,
) -> str:
    """Heuristik fuer Tabellentyp-Erkennung."""
    name_lower = name.lower()

    # Kalender-Heuristik
    date_indicators = ("date", "datum", "calendar", "kalender", "zeit", "time")
    if any(ind in name_lower for ind in date_indicators):
        return "Kalender"
    if has_date_col:
        date_col_names = {"year", "month", "day", "quarter", "jahr", "monat", "tag", "quartal"}
        col_names_lower = {c.get("name", "").lower() for c in columns}
        if len(date_col_names & col_names_lower) >= 2:
            return "Kalender"

    # Fakt-Heuristik
    fact_indicators = ("fact", "fakt", "fct_", "transact", "detail", "sales", "order")
    if any(ind in name_lower for ind in fact_indicators):
        return "Fakt"
    # Viele Measures deuten auf Fakt hin
    measure_count = len(tbl_data.get("measures", []))
    if measure_count >= 3:
        return "Fakt"

    # Dimension-Heuristik
    dim_indicators = ("dim", "lookup", "lkp", "master", "stamm")
    if any(ind in name_lower for ind in dim_indicators):
        return "Dimension"

    # Bridge-Heuristik
    bridge_indicators = ("bridge", "bruecke", "link", "map", "junction")
    if any(ind in name_lower for ind in bridge_indicators):
        return "Bridge"

    return ""


# ══════════════════════════════════════════════════════════════════
# Measures parsen
# ══════════════════════════════════════════════════════════════════

def _parse_measure(
    m_data: dict,
    table_name: str,
    all_measure_names: Set[str],
    warnings: List[str],
) -> Optional[Measure]:
    """Einzelnes Measure aus BIM-JSON parsen."""
    name = m_data.get("name", "")
    if not name:
        return None

    expression = m_data.get("expression", "")
    if isinstance(expression, list):
        expression = "\n".join(expression)

    display_folder = m_data.get("displayFolder", "")
    description = m_data.get("description", "")

    # Annotations als Fallback fuer description
    if not description:
        for ann in m_data.get("annotations", []):
            if ann.get("name", "").lower() in ("description", "desc"):
                description = ann.get("value", "")
                break

    format_string = m_data.get("formatString", "")
    if format_string and not description:
        description = f"Format: {format_string}"
    elif format_string and description:
        description = f"{description} (Format: {format_string})"

    # Dependencies erkennen
    deps = _detect_dependencies(expression, name, all_measure_names)

    # Filter-Kontext-Hinweise
    filter_notes = _detect_filter_context(expression)

    return Measure(
        name=name,
        dax_code=expression,
        display_folder=display_folder,
        description=description,
        dependencies=deps,
        filter_context_notes=filter_notes,
    )


def _detect_dependencies(dax: str, own_name: str, all_measure_names: Set[str]) -> str:
    """Erkennt referenzierte Measures und Spalten im DAX-Code."""
    deps: List[str] = []

    # Referenzierte Measures: [MeasureName]
    bracket_refs = re.findall(r'\[([^\[\]]+)\]', dax)
    for ref in bracket_refs:
        if ref in all_measure_names and ref != own_name:
            if ref not in deps:
                deps.append(ref)

    # Spaltenreferenzen: Table[Column]
    col_refs = re.findall(r"(\w+)\[(\w+)\]", dax)
    for tbl, col in col_refs:
        ref_str = f"{tbl}[{col}]"
        if ref_str not in deps:
            deps.append(ref_str)

    return ", ".join(deps) if deps else ""


def _detect_filter_context(dax: str) -> str:
    """Erkennt CALCULATE/FILTER/ALL etc. als Filter-Kontext-Hinweise."""
    hints: List[str] = []
    dax_upper = dax.upper()

    if "CALCULATE" in dax_upper:
        hints.append("CALCULATE (modifizierter Filterkontext)")
    if "FILTER" in dax_upper:
        hints.append("FILTER (zeilenweiser Filter)")
    if re.search(r'\bALL\s*\(', dax, re.IGNORECASE):
        hints.append("ALL (Filter entfernt)")
    if "ALLEXCEPT" in dax_upper:
        hints.append("ALLEXCEPT (selektiver Filter)")
    if "KEEPFILTERS" in dax_upper:
        hints.append("KEEPFILTERS")
    if "USERELATIONSHIP" in dax_upper:
        hints.append("USERELATIONSHIP (inaktive Beziehung aktiviert)")

    # Time Intelligence
    time_funcs = ["DATEADD", "SAMEPERIODLASTYEAR", "DATESYTD", "DATESQTD",
                  "DATESMTD", "TOTALYTD", "TOTALQTD", "TOTALMTD",
                  "PARALLELPERIOD", "PREVIOUSMONTH", "PREVIOUSYEAR"]
    for func in time_funcs:
        if func in dax_upper:
            hints.append(f"Time Intelligence ({func})")
            break  # Nur einmal erwaehnen

    return "; ".join(hints) if hints else ""


# ══════════════════════════════════════════════════════════════════
# Partitionen parsen
# ══════════════════════════════════════════════════════════════════

def _parse_partition(
    part: dict,
    table_name: str,
    seen_sources: set,
    warnings: List[str],
) -> tuple[Optional[PowerQuery], List[DataSource]]:
    """Partition -> PowerQuery + DataSource(s)."""
    source = part.get("source", {})
    source_type = source.get("type", "").lower()
    expression = source.get("expression", "")

    if isinstance(expression, list):
        expression = "\n".join(expression)

    if not expression:
        return None, []

    pq: Optional[PowerQuery] = None
    ds_list: List[DataSource] = []

    if source_type in ("m", "powerQuery"):
        pq = PowerQuery(
            query_name=table_name,
            m_code=expression,
            output_table=table_name,
        )
        ds_list = _detect_sources_from_m(expression)
        # Deduplizierung
        new_ds = []
        for ds in ds_list:
            key = f"{ds.source_type}::{ds.connection_info}"
            if key not in seen_sources:
                seen_sources.add(key)
                new_ds.append(ds)
        ds_list = new_ds

    elif source_type in ("query", "sql"):
        # Native SQL Query
        pq = PowerQuery(
            query_name=table_name,
            m_code=expression,
            output_table=table_name,
            notes="Native SQL Abfrage",
        )
        # DataSource aus der Query
        ds_data = source.get("dataSource", "")
        if ds_data and ds_data not in seen_sources:
            seen_sources.add(ds_data)
            ds_list.append(DataSource(
                source_type="SQL",
                name=f"SQL: {ds_data}",
                connection_info=ds_data,
                gateway_required=True,
            ))

    return pq, ds_list


# ══════════════════════════════════════════════════════════════════
# Relationships parsen
# ══════════════════════════════════════════════════════════════════

def _parse_relationships(model: dict, warnings: List[str]) -> List[ModelRelationship]:
    """Parst alle Beziehungen aus dem BIM-Modell."""
    rels: List[ModelRelationship] = []

    for rel_data in model.get("relationships", []):
        try:
            from_table = rel_data.get("fromTable", "")
            from_column = rel_data.get("fromColumn", "")
            to_table = rel_data.get("toTable", "")
            to_column = rel_data.get("toColumn", "")

            if not (from_table and to_table):
                continue

            # Cardinality
            cardinality_str = rel_data.get("cardinality", "")
            if cardinality_str:
                cardinality = _CARDINALITY_MAP.get(cardinality_str, cardinality_str)
            else:
                from_card = rel_data.get("fromCardinality", "many")
                to_card = rel_data.get("toCardinality", "one")
                cardinality = _map_cardinality_pair(from_card, to_card)

            # Filter-Richtung
            cross_filter = rel_data.get("crossFilteringBehavior", "oneDirection")
            filter_direction = _FILTER_DIR_MAP.get(cross_filter, cross_filter)

            # Inaktive Beziehungen
            is_active = rel_data.get("isActive", True)
            if not is_active:
                filter_direction += " [inaktiv]"

            rels.append(ModelRelationship(
                from_table=from_table,
                from_column=from_column,
                to_table=to_table,
                to_column=to_column,
                cardinality=cardinality,
                filter_direction=filter_direction,
            ))

        except Exception as exc:
            rel_name = rel_data.get("name", "?")
            warnings.append(f"Beziehung '{rel_name}' uebersprungen: {exc}")

    return rels


# ══════════════════════════════════════════════════════════════════
# RLS-Rollen parsen
# ══════════════════════════════════════════════════════════════════

def _parse_roles(model: dict, warnings: List[str]) -> str:
    """Parst RLS-Rollen und gibt formatierte Zusammenfassung zurueck."""
    roles = model.get("roles", [])
    if not roles:
        return ""

    parts: List[str] = []
    for role in roles:
        try:
            name = role.get("name", "Unbenannt")
            permission = role.get("modelPermission", "")
            table_perms = role.get("tablePermissions", [])

            role_desc = f"**{name}** (Berechtigung: {permission})"
            if table_perms:
                for tp in table_perms:
                    tbl = tp.get("name", "")
                    expr = tp.get("filterExpression", "")
                    if tbl and expr:
                        role_desc += f"\n  - {tbl}: `{expr}`"

            parts.append(role_desc)
        except Exception as exc:
            warnings.append(f"RLS-Rolle uebersprungen: {exc}")

    return "\n\n".join(parts) if parts else ""


# ══════════════════════════════════════════════════════════════════
# Tabellentyp verfeinern anhand von Relationships
# ══════════════════════════════════════════════════════════════════

def _refine_table_types(
    tables: List[ModelTable],
    relationships: List[ModelRelationship],
):
    """Verfeinert Tabellentypen anhand der Beziehungsstruktur."""
    table_map = {t.name: t for t in tables}
    outgoing: dict[str, int] = {}  # Tabelle -> Anzahl ausgehender FK-Beziehungen
    incoming: dict[str, int] = {}  # Tabelle -> Anzahl eingehender Beziehungen

    for rel in relationships:
        outgoing[rel.from_table] = outgoing.get(rel.from_table, 0) + 1
        incoming[rel.to_table] = incoming.get(rel.to_table, 0) + 1

    for name, tbl in table_map.items():
        if tbl.table_type:
            continue  # Bereits klassifiziert
        out = outgoing.get(name, 0)
        inc = incoming.get(name, 0)
        if out >= 2 and inc == 0:
            tbl.table_type = "Fakt"
        elif inc >= 1 and out == 0:
            tbl.table_type = "Dimension"


# ══════════════════════════════════════════════════════════════════
# Hauptfunktion
# ══════════════════════════════════════════════════════════════════

def parse_bim(
    bim_path: Path,
    skip_hidden_tables: bool = True,
    skip_hidden_measures: bool = False,
    detect_table_types: bool = True,
) -> BimImportResult:
    """
    Parst eine .bim-Datei (Tabular Model JSON) und gibt
    ein vollstaendig befuelltes Ergebnis zurueck.

    Unterstuetzt auch .json-Dateien die das BIM-Format haben
    (z.B. database.json aus pbi-tools).
    """
    result = BimImportResult()

    if not bim_path.exists():
        result.warnings.append(f"Datei nicht gefunden: {bim_path}")
        return result

    try:
        text = bim_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = bim_path.read_text(encoding="utf-8-sig")
        except Exception as exc:
            result.warnings.append(f"Datei nicht lesbar: {exc}")
            return result

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        result.warnings.append(f"Kein gueltiges JSON: {exc}")
        return result

    # BIM-Format erkennen: {"model": {...}} oder direkt {"tables": [...]}
    model = data.get("model", data)
    if "tables" not in model and "relationships" not in model:
        result.warnings.append("Kein BIM/Tabular-Model-Format erkannt (fehlende 'tables' oder 'model').")
        return result

    # Report-Name
    result.report_name = model.get("name", "") or model.get("description", "") or data.get("name", "")
    if not result.report_name:
        result.report_name = bim_path.stem

    # Tabellen, Measures, Queries, Sources
    tables, measures, queries, sources, date_logic = _parse_tables(
        model, result.warnings,
        skip_hidden=skip_hidden_tables,
        detect_types=detect_table_types,
    )
    result.tables = tables
    result.measures = measures
    result.power_queries = queries
    result.data_sources = sources
    result.date_logic_notes = date_logic

    # Hidden Measures filtern
    if skip_hidden_measures:
        for tbl_data in model.get("tables", []):
            for m_data in tbl_data.get("measures", []):
                if m_data.get("isHidden", False):
                    m_name = m_data.get("name", "")
                    result.measures = [m for m in result.measures if m.name != m_name]

    # Relationships
    result.relationships = _parse_relationships(model, result.warnings)

    # Tabellentypen verfeinern
    if detect_table_types:
        _refine_table_types(result.tables, result.relationships)

    # RLS
    result.rls_notes = _parse_roles(model, result.warnings)

    return result


def is_bim_format(path: Path) -> bool:
    """Prueft ob eine JSON-Datei das BIM/Tabular-Model-Format hat."""
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        model = data.get("model", data)
        return "tables" in model or "relationships" in model
    except Exception:
        return False
