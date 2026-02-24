"""
Umfassende Unit-Tests fuer PBIX-Parser, BIM-Parser und Import-Manager.

Run:  python -m pytest tests/test_parsers.py -v
  or: python -m unittest tests/test_parsers.py -v
"""

import io
import json
import os
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import (
    Project, DataSource, Measure, PowerQuery, ModelTable,
    ModelRelationship, ReportPage, Visual,
)
from src.pbix_parser import (
    PbixImportResult, parse_pbix, VISUAL_TYPE_MAP, _visual_type_label,
    _split_m_queries, _detect_sources,
)
from src.bim_parser import (
    BimImportResult, parse_bim, is_bim_format,
    _detect_dependencies, _detect_filter_context,
)
from src.import_manager import (
    ImportOptions, ImportReport, ImportPreview,
    import_file, preview_import, detect_file_type, _merge_list,
)
from src.pbitools_parser import pbitools_available


# ══════════════════════════════════════════════════════════════════
# Test-Daten-Helfer
# ══════════════════════════════════════════════════════════════════

def _create_test_pbix(tmp_path: Path, include_mashup: bool = True,
                      include_schema: bool = False) -> Path:
    """Erzeugt eine minimale .pbix-Datei als ZIP fuer Tests."""
    pbix = tmp_path / "test_report.pbix"

    with zipfile.ZipFile(str(pbix), "w", zipfile.ZIP_DEFLATED) as zf:
        # Report/Layout
        layout = {
            "sections": [
                {
                    "name": "Section1",
                    "displayName": "Uebersicht",
                    "visualContainers": [
                        {"config": json.dumps({
                            "singleVisual": {
                                "visualType": "clusteredBarChart",
                                "projections": {
                                    "Values": [{"queryRef": "Sum_Revenue"}],
                                    "Category": [{"queryRef": "Dim_Product.Name"}],
                                },
                            }
                        })},
                        {"config": json.dumps({
                            "singleVisual": {
                                "visualType": "slicer",
                                "projections": {
                                    "Values": [{"queryRef": "Dim_Date.Year"}],
                                },
                            }
                        })},
                        {"config": json.dumps({
                            "singleVisual": {
                                "visualType": "card",
                                "projections": {
                                    "Values": [{"queryRef": "Total_Revenue"}],
                                },
                            }
                        })},
                    ],
                },
                {
                    "name": "Section2",
                    "displayName": "Details",
                    "visualContainers": [
                        {"config": json.dumps({
                            "singleVisual": {
                                "visualType": "tableEx",
                                "projections": {
                                    "Values": [
                                        {"queryRef": "OrderDate"},
                                        {"queryRef": "Amount"},
                                    ],
                                },
                            }
                        })},
                    ],
                },
            ],
        }
        zf.writestr("Report/Layout", json.dumps(layout))

        # DataMashup als inneres ZIP
        if include_mashup:
            m_code = '''section Section1;

shared Fact_Sales = let
    Source = Sql.Database("sql-server-01", "SalesDB"),
    Sales = Source{[Schema="dbo",Item="Sales"]}[Data]
in
    Sales;

shared Dim_Product = let
    Source = Excel.Workbook(File.Contents("C:\\Data\\Products.xlsx")),
    Sheet1 = Source{[Item="Sheet1"]}[Data]
in
    Sheet1;

shared Dim_Region = let
    Source = SharePoint.Tables("https://contoso.sharepoint.com/sites/data"),
    RegionTable = Source{[Title="Regions"]}[Data]
in
    RegionTable;

shared Web_Data = let
    Source = Web.Contents("https://api.example.com/data"),
    Json = Json.Document(Source)
in
    Json;

shared OData_Feed = let
    Source = OData.Feed("https://odata.example.com/service")
in
    Source;
'''
            mashup_inner = io.BytesIO()
            with zipfile.ZipFile(mashup_inner, "w") as inner_zf:
                inner_zf.writestr("Formulas/Section1.m", m_code)
            mashup_bytes = mashup_inner.getvalue()

            # DataMashup hat einen kleinen Header vor dem ZIP
            header = struct.pack("<I", len(mashup_bytes))
            zf.writestr("DataMashup", header + mashup_bytes)

        # DataModelSchema (optional)
        if include_schema:
            schema = {
                "model": {
                    "tables": [
                        {
                            "name": "Fact_Sales",
                            "columns": [
                                {"name": "SalesID", "dataType": "int64", "isKey": True},
                                {"name": "Revenue", "dataType": "decimal"},
                                {"name": "DateKey", "dataType": "int64"},
                            ],
                        },
                        {
                            "name": "Dim_Date",
                            "columns": [
                                {"name": "DateKey", "dataType": "int64", "isKey": True},
                                {"name": "Date", "dataType": "dateTime"},
                                {"name": "Year", "dataType": "int64"},
                            ],
                        },
                    ],
                },
            }
            zf.writestr("DataModelSchema", json.dumps(schema))

    return pbix


def _create_test_bim(tmp_path: Path) -> Path:
    """Erzeugt eine minimale .bim-Datei fuer Tests."""
    bim = {
        "model": {
            "name": "TestModel",
            "tables": [
                {
                    "name": "Fact_Sales",
                    "description": "Verkaufsdaten",
                    "columns": [
                        {"name": "SalesID", "dataType": "int64", "isKey": True,
                         "sourceColumn": "SalesID"},
                        {"name": "Revenue", "dataType": "decimal",
                         "sourceColumn": "Revenue"},
                        {"name": "Quantity", "dataType": "int64",
                         "sourceColumn": "Quantity"},
                        {"name": "DateKey", "dataType": "int64",
                         "sourceColumn": "DateKey"},
                        {"name": "ProductKey", "dataType": "int64",
                         "sourceColumn": "ProductKey"},
                    ],
                    "measures": [
                        {
                            "name": "Total Revenue",
                            "expression": "SUM(Fact_Sales[Revenue])",
                            "displayFolder": "Revenue",
                            "description": "Gesamtumsatz",
                            "formatString": "#,##0.00",
                        },
                        {
                            "name": "Revenue YoY",
                            "expression": [
                                "VAR CurrentYear = [Total Revenue]",
                                "VAR PriorYear = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date]))",
                                "RETURN DIVIDE(CurrentYear - PriorYear, PriorYear)"
                            ],
                            "displayFolder": "Revenue",
                            "description": "Umsatzveraenderung im Vergleich zum Vorjahr",
                        },
                        {
                            "name": "Total Quantity",
                            "expression": "SUM(Fact_Sales[Quantity])",
                            "displayFolder": "Volume",
                        },
                        {
                            "name": "Avg Revenue per Unit",
                            "expression": "DIVIDE([Total Revenue], [Total Quantity])",
                            "displayFolder": "Revenue",
                        },
                    ],
                    "partitions": [
                        {
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    "    Source = Sql.Database(\"sql-server-01\", \"SalesDB\"),",
                                    "    Sales = Source{[Schema=\"dbo\",Item=\"Sales\"]}[Data]",
                                    "in",
                                    "    Sales"
                                ],
                            },
                        },
                    ],
                },
                {
                    "name": "Dim_Date",
                    "columns": [
                        {"name": "DateKey", "dataType": "int64", "isKey": True},
                        {"name": "Date", "dataType": "dateTime"},
                        {"name": "Year", "dataType": "int64"},
                        {"name": "Month", "dataType": "int64"},
                        {"name": "Quarter", "dataType": "int64"},
                    ],
                    "annotations": [
                        {"name": "description", "value": "Datumsdimension / Kalendertabelle"},
                    ],
                },
                {
                    "name": "Dim_Product",
                    "columns": [
                        {"name": "ProductKey", "dataType": "int64", "isKey": True},
                        {"name": "ProductName", "dataType": "string"},
                        {"name": "Category", "dataType": "string"},
                    ],
                },
                {
                    "name": "Hidden_Helper",
                    "isHidden": True,
                    "columns": [
                        {"name": "ID", "dataType": "int64"},
                    ],
                },
            ],
            "relationships": [
                {
                    "name": "rel_sales_date",
                    "fromTable": "Fact_Sales",
                    "fromColumn": "DateKey",
                    "toTable": "Dim_Date",
                    "toColumn": "DateKey",
                    "fromCardinality": "many",
                    "toCardinality": "one",
                    "crossFilteringBehavior": "oneDirection",
                    "isActive": True,
                },
                {
                    "name": "rel_sales_product",
                    "fromTable": "Fact_Sales",
                    "fromColumn": "ProductKey",
                    "toTable": "Dim_Product",
                    "toColumn": "ProductKey",
                    "fromCardinality": "many",
                    "toCardinality": "one",
                    "crossFilteringBehavior": "bothDirections",
                    "isActive": True,
                },
                {
                    "name": "rel_inactive",
                    "fromTable": "Fact_Sales",
                    "fromColumn": "ShipDateKey",
                    "toTable": "Dim_Date",
                    "toColumn": "DateKey",
                    "fromCardinality": "many",
                    "toCardinality": "one",
                    "crossFilteringBehavior": "oneDirection",
                    "isActive": False,
                },
            ],
            "roles": [
                {
                    "name": "RegionFilter",
                    "modelPermission": "read",
                    "tablePermissions": [
                        {
                            "name": "Dim_Region",
                            "filterExpression": "[RegionID] = USERPRINCIPALNAME()",
                        },
                    ],
                },
                {
                    "name": "ManagerRole",
                    "modelPermission": "read",
                    "tablePermissions": [
                        {
                            "name": "Fact_Sales",
                            "filterExpression": "[ManagerEmail] = USERPRINCIPALNAME()",
                        },
                    ],
                },
            ],
        },
    }
    path = tmp_path / "TestModel.bim"
    path.write_text(json.dumps(bim, indent=2), encoding="utf-8")
    return path


# ══════════════════════════════════════════════════════════════════
# PBIX Parser Tests
# ══════════════════════════════════════════════════════════════════

class TestPbixParser(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_parse_report_layout_pages(self):
        """Test: Report-Layout-Seiten werden korrekt extrahiert."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        self.assertEqual(len(result.report_pages), 2)
        self.assertEqual(result.report_pages[0].page_name, "Uebersicht")
        self.assertEqual(result.report_pages[1].page_name, "Details")

    def test_parse_visuals(self):
        """Test: Visuals werden mit Typ und Feldern extrahiert."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        page1 = result.report_pages[0]
        # 2 echte Visuals + 1 Slicer (Slicer wird separat erfasst)
        self.assertEqual(len(page1.visuals), 2)  # bar chart + card
        self.assertTrue(page1.slicers_filters)  # Slicer vorhanden

    def test_slicer_detection(self):
        """Test: Slicer werden separat erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        page1 = result.report_pages[0]
        self.assertIn("Dim_Date.Year", page1.slicers_filters)

    def test_visual_type_mapping(self):
        """Test: Visual-Typen haben menschenlesbare Namen."""
        self.assertEqual(_visual_type_label("clusteredBarChart"), "Balkendiagramm (gruppiert)")
        self.assertEqual(_visual_type_label("slicer"), "Slicer / Filter")
        self.assertEqual(_visual_type_label("tableEx"), "Tabelle")
        self.assertEqual(_visual_type_label("unknownType"), "unknownType")

    def test_m_code_extraction(self):
        """Test: M-Code wird aus DataMashup extrahiert."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        self.assertGreater(len(result.power_queries), 0)
        # Mindestens die benannten Queries
        query_names = [q.query_name for q in result.power_queries]
        self.assertIn("Fact_Sales", query_names)
        self.assertIn("Dim_Product", query_names)

    def test_data_source_detection_sql(self):
        """Test: SQL-Datenquelle wird aus M-Code erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        sql_sources = [s for s in result.data_sources if s.source_type == "SQL"]
        self.assertGreater(len(sql_sources), 0)
        self.assertIn("sql-server-01/SalesDB", sql_sources[0].connection_info)

    def test_data_source_detection_excel(self):
        """Test: Excel-Datenquelle wird erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        excel_sources = [s for s in result.data_sources if s.source_type == "Excel"]
        self.assertGreater(len(excel_sources), 0)

    def test_data_source_detection_sharepoint(self):
        """Test: SharePoint-Datenquelle wird erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        sp_sources = [s for s in result.data_sources if s.source_type == "SharePoint List"]
        self.assertGreater(len(sp_sources), 0)

    def test_data_source_detection_web(self):
        """Test: Web-API-Datenquelle wird erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        web_sources = [s for s in result.data_sources if s.source_type == "API/Web"]
        self.assertGreater(len(web_sources), 0)

    def test_data_source_detection_odata(self):
        """Test: OData-Datenquelle wird erkannt."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        odata_sources = [s for s in result.data_sources if s.source_type == "OData"]
        self.assertGreater(len(odata_sources), 0)

    def test_gateway_detection(self):
        """Test: On-Premises-Quellen werden mit gateway_required markiert."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        sql_sources = [s for s in result.data_sources if s.source_type == "SQL"]
        self.assertTrue(sql_sources[0].gateway_required)

    def test_no_datamashup(self):
        """Test: Fehlender DataMashup erzeugt Warnung, kein Crash."""
        pbix = _create_test_pbix(self.tmp, include_mashup=False)
        result = parse_pbix(pbix)
        self.assertTrue(any("DataMashup" in w for w in result.warnings))
        self.assertEqual(len(result.power_queries), 0)

    def test_report_name_fallback(self):
        """Test: Dateiname als Fallback fuer Report-Name."""
        pbix = _create_test_pbix(self.tmp)
        result = parse_pbix(pbix)
        self.assertTrue(result.report_name)

    def test_data_model_schema(self):
        """Test: DataModelSchema wird geparst (optionaler Eintrag)."""
        pbix = _create_test_pbix(self.tmp, include_schema=True)
        result = parse_pbix(pbix)
        self.assertGreater(len(result.tables), 0)
        table_names = [t.name for t in result.tables]
        self.assertIn("Fact_Sales", table_names)
        self.assertIn("Dim_Date", table_names)

    def test_nonexistent_file(self):
        """Test: Nicht existierende Datei erzeugt Warnung."""
        result = parse_pbix(self.tmp / "nonexistent.pbix")
        self.assertTrue(len(result.warnings) > 0)

    def test_invalid_zip(self):
        """Test: Ungueltige ZIP-Datei erzeugt Warnung."""
        bad_file = self.tmp / "bad.pbix"
        bad_file.write_bytes(b"This is not a zip file")
        result = parse_pbix(bad_file)
        self.assertTrue(len(result.warnings) > 0)

    def test_empty_layout(self):
        """Test: Leerer Layout erzeugt keine Seiten, aber keine Exception."""
        pbix = self.tmp / "empty.pbix"
        with zipfile.ZipFile(str(pbix), "w") as zf:
            zf.writestr("Report/Layout", json.dumps({"sections": []}))
        result = parse_pbix(pbix)
        self.assertEqual(len(result.report_pages), 0)


class TestMCodeParsing(unittest.TestCase):
    """Tests fuer M-Code-Aufspaltung und Quellerkennung."""

    def test_split_shared_queries(self):
        """Test: shared-Statements werden korrekt getrennt."""
        m_code = '''section Section1;

shared Query1 = let
    Source = "test"
in
    Source;

shared Query2 = let
    Source = "test2"
in
    Source;
'''
        queries = _split_m_queries(m_code)
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0].query_name, "Query1")
        self.assertEqual(queries[1].query_name, "Query2")

    def test_detect_multiple_sources(self):
        """Test: Mehrere Datenquellen aus einem M-Code-Block."""
        m_code = '''
Sql.Database("server1", "db1")
Excel.Workbook(File.Contents("C:\\file.xlsx"))
Web.Contents("https://api.example.com")
'''
        sources = _detect_sources(m_code)
        types = {s.source_type for s in sources}
        self.assertIn("SQL", types)
        self.assertIn("Excel", types)
        self.assertIn("API/Web", types)

    def test_detect_sap_hana(self):
        """Test: SAP HANA wird erkannt."""
        m_code = 'SapHana.Database("hana-server-01")'
        sources = _detect_sources(m_code)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_type, "SAP HANA")

    def test_detect_csv(self):
        """Test: CSV-Quelle wird erkannt."""
        m_code = 'Csv.Document(File.Contents("C:\\data\\export.csv"))'
        sources = _detect_sources(m_code)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].source_type, "CSV")

    def test_no_duplicates(self):
        """Test: Gleiche Quelle wird nur einmal erkannt."""
        m_code = '''
Sql.Database("server", "db")
Sql.Database("server", "db")
'''
        sources = _detect_sources(m_code)
        self.assertEqual(len(sources), 1)


# ══════════════════════════════════════════════════════════════════
# BIM Parser Tests
# ══════════════════════════════════════════════════════════════════

class TestBimParser(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_parse_tables(self):
        """Test: Tabellen werden korrekt geparst."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        table_names = [t.name for t in result.tables]
        self.assertIn("Fact_Sales", table_names)
        self.assertIn("Dim_Date", table_names)
        self.assertIn("Dim_Product", table_names)

    def test_hidden_table_skipped(self):
        """Test: Versteckte Tabellen werden standardmaessig uebersprungen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim, skip_hidden_tables=True)
        table_names = [t.name for t in result.tables]
        self.assertNotIn("Hidden_Helper", table_names)

    def test_hidden_table_included(self):
        """Test: Versteckte Tabellen werden mit Option eingeschlossen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim, skip_hidden_tables=False)
        table_names = [t.name for t in result.tables]
        self.assertIn("Hidden_Helper", table_names)

    def test_table_type_heuristic_calendar(self):
        """Test: Dim_Date wird als Kalender erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        date_table = [t for t in result.tables if t.name == "Dim_Date"][0]
        self.assertEqual(date_table.table_type, "Kalender")

    def test_table_type_heuristic_fact(self):
        """Test: Fact_Sales wird als Fakt erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        facts = [t for t in result.tables if t.name == "Fact_Sales"]
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].table_type, "Fakt")

    def test_table_type_heuristic_dimension(self):
        """Test: Dim_Product wird als Dimension erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        dim = [t for t in result.tables if t.name == "Dim_Product"][0]
        self.assertEqual(dim.table_type, "Dimension")

    def test_table_keys(self):
        """Test: Primaerschluessel werden erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        fact = [t for t in result.tables if t.name == "Fact_Sales"][0]
        self.assertIn("SalesID", fact.keys)

    def test_table_description(self):
        """Test: Tabellenbeschreibungen werden uebernommen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        fact = [t for t in result.tables if t.name == "Fact_Sales"][0]
        self.assertEqual(fact.description, "Verkaufsdaten")

    def test_relationships(self):
        """Test: Beziehungen werden korrekt geparst."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertEqual(len(result.relationships), 3)

    def test_relationship_cardinality(self):
        """Test: Cardinality wird korrekt gemappt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        sales_date = [r for r in result.relationships
                      if r.from_table == "Fact_Sales" and r.to_table == "Dim_Date" and "inaktiv" not in r.filter_direction]
        self.assertEqual(len(sales_date), 1)
        self.assertEqual(sales_date[0].cardinality, "N:1")

    def test_relationship_filter_direction(self):
        """Test: Filter-Richtung wird korrekt gemappt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        both_dir = [r for r in result.relationships
                    if r.filter_direction.startswith("Both")]
        self.assertGreater(len(both_dir), 0)

    def test_inactive_relationship(self):
        """Test: Inaktive Beziehungen werden gekennzeichnet."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        inactive = [r for r in result.relationships if "inaktiv" in r.filter_direction]
        self.assertEqual(len(inactive), 1)

    def test_measures_parsing(self):
        """Test: Measures werden mit DAX-Code geparst."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertEqual(len(result.measures), 4)
        total = [m for m in result.measures if m.name == "Total Revenue"][0]
        self.assertEqual(total.dax_code, "SUM(Fact_Sales[Revenue])")
        self.assertEqual(total.display_folder, "Revenue")

    def test_measure_description(self):
        """Test: Measure-Beschreibungen werden uebernommen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        total = [m for m in result.measures if m.name == "Total Revenue"][0]
        self.assertIn("Gesamtumsatz", total.description)

    def test_measure_expression_list(self):
        """Test: Measure-Expression als Liste wird korrekt zusammengefuegt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        yoy = [m for m in result.measures if m.name == "Revenue YoY"][0]
        self.assertIn("SAMEPERIODLASTYEAR", yoy.dax_code)
        self.assertIn("DIVIDE", yoy.dax_code)

    def test_measure_dependencies(self):
        """Test: Abhaengigkeiten werden aus DAX erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        avg = [m for m in result.measures if m.name == "Avg Revenue per Unit"][0]
        self.assertIn("Total Revenue", avg.dependencies)
        self.assertIn("Total Quantity", avg.dependencies)

    def test_measure_filter_context(self):
        """Test: Filter-Kontext-Hinweise werden erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        yoy = [m for m in result.measures if m.name == "Revenue YoY"][0]
        self.assertIn("CALCULATE", yoy.filter_context_notes)
        self.assertIn("Time Intelligence", yoy.filter_context_notes)

    def test_partition_power_query(self):
        """Test: Partitionen erzeugen PowerQuery-Eintraege."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertGreater(len(result.power_queries), 0)
        fact_pq = [q for q in result.power_queries if q.query_name == "Fact_Sales"]
        self.assertEqual(len(fact_pq), 1)
        self.assertIn("Sql.Database", fact_pq[0].m_code)

    def test_partition_data_source(self):
        """Test: Datenquellen werden aus Partitionen erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        sql_sources = [s for s in result.data_sources if s.source_type == "SQL"]
        self.assertGreater(len(sql_sources), 0)

    def test_rls_roles(self):
        """Test: RLS-Rollen werden geparst."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertIn("RegionFilter", result.rls_notes)
        self.assertIn("ManagerRole", result.rls_notes)
        self.assertIn("USERPRINCIPALNAME", result.rls_notes)

    def test_report_name(self):
        """Test: Modellname wird als Report-Name uebernommen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertEqual(result.report_name, "TestModel")

    def test_date_logic_notes(self):
        """Test: Datumstabellen-Logik wird erkannt."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        self.assertIn("Dim_Date", result.date_logic_notes)

    def test_is_bim_format(self):
        """Test: BIM-Format wird korrekt erkannt."""
        bim = _create_test_bim(self.tmp)
        self.assertTrue(is_bim_format(bim))

    def test_is_not_bim_format(self):
        """Test: Nicht-BIM-JSON wird korrekt erkannt."""
        json_file = self.tmp / "other.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")
        self.assertFalse(is_bim_format(json_file))

    def test_nonexistent_bim(self):
        """Test: Nicht existierende BIM-Datei erzeugt Warnung."""
        result = parse_bim(self.tmp / "nonexistent.bim")
        self.assertTrue(len(result.warnings) > 0)

    def test_invalid_json(self):
        """Test: Ungueltige JSON-Datei erzeugt Warnung."""
        bad = self.tmp / "bad.bim"
        bad.write_text("not json{{{", encoding="utf-8")
        result = parse_bim(bad)
        self.assertTrue(len(result.warnings) > 0)

    def test_annotations_as_description(self):
        """Test: Annotations werden als Beschreibung uebernommen."""
        bim = _create_test_bim(self.tmp)
        result = parse_bim(bim)
        dim_date = [t for t in result.tables if t.name == "Dim_Date"][0]
        self.assertIn("Kalendertabelle", dim_date.description)


class TestDependencyDetection(unittest.TestCase):
    """Tests fuer DAX-Dependency-Erkennung."""

    def test_measure_reference(self):
        """Test: Referenzierte Measures werden erkannt."""
        dax = "DIVIDE([Total Revenue], [Total Quantity])"
        deps = _detect_dependencies(dax, "Avg", {"Total Revenue", "Total Quantity", "Avg"})
        self.assertIn("Total Revenue", deps)
        self.assertIn("Total Quantity", deps)

    def test_column_reference(self):
        """Test: Spaltenreferenzen werden erkannt."""
        dax = "SUM(Fact_Sales[Revenue])"
        deps = _detect_dependencies(dax, "Total", set())
        self.assertIn("Fact_Sales[Revenue]", deps)

    def test_no_self_reference(self):
        """Test: Eigener Name wird nicht als Dependency gelistet."""
        dax = "[MyMeasure] + 1"
        deps = _detect_dependencies(dax, "MyMeasure", {"MyMeasure"})
        self.assertNotIn("MyMeasure", deps)


class TestFilterContextDetection(unittest.TestCase):
    """Tests fuer Filter-Kontext-Hinweise."""

    def test_calculate(self):
        notes = _detect_filter_context("CALCULATE(SUM(T[V]), ALL(T))")
        self.assertIn("CALCULATE", notes)
        self.assertIn("ALL", notes)

    def test_time_intelligence(self):
        notes = _detect_filter_context("TOTALYTD([M], Dim_Date[Date])")
        self.assertIn("Time Intelligence", notes)

    def test_userelationship(self):
        notes = _detect_filter_context("CALCULATE([M], USERELATIONSHIP(T[A], T2[B]))")
        self.assertIn("USERELATIONSHIP", notes)

    def test_no_hints(self):
        notes = _detect_filter_context("SUM(T[V])")
        self.assertEqual(notes, "")


# ══════════════════════════════════════════════════════════════════
# Import Manager Tests
# ══════════════════════════════════════════════════════════════════

class TestImportManager(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_detect_file_type_pbix(self):
        """Test: .pbix wird korrekt erkannt."""
        self.assertEqual(detect_file_type(Path("test.pbix")), "pbix")

    def test_detect_file_type_pbit(self):
        """Test: .pbit wird korrekt erkannt."""
        self.assertEqual(detect_file_type(Path("test.pbit")), "pbit")

    def test_detect_file_type_bim(self):
        """Test: .bim wird korrekt erkannt."""
        self.assertEqual(detect_file_type(Path("test.bim")), "bim")

    def test_detect_file_type_json_bim(self):
        """Test: BIM-Format in .json wird erkannt."""
        bim = _create_test_bim(self.tmp)
        json_bim = self.tmp / "database.json"
        import shutil
        shutil.copy2(bim, json_bim)
        self.assertEqual(detect_file_type(json_bim), "json_bim")

    def test_detect_file_type_unknown(self):
        """Test: Unbekannter Dateityp."""
        self.assertEqual(detect_file_type(Path("test.xlsx")), "unknown")

    def test_import_bim_replace(self):
        """Test: BIM-Import im Replace-Modus."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        project.measures.append(Measure(name="Existing"))

        options = ImportOptions(merge_mode="replace")
        report = import_file(bim, project, options)

        self.assertTrue(report.success)
        self.assertGreater(report.imported.get("measures", 0), 0)
        # Existing measure should be replaced
        existing = [m for m in project.measures if m.name == "Existing"]
        self.assertEqual(len(existing), 0)  # Replaced

    def test_import_bim_merge(self):
        """Test: BIM-Import im Merge-Modus behaelt bestehende Daten."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        project.measures.append(Measure(name="Total Revenue", dax_code="CUSTOM"))

        options = ImportOptions(merge_mode="merge")
        report = import_file(bim, project, options)

        # Der bestehende Measure sollte erhalten bleiben
        total = [m for m in project.measures if m.name == "Total Revenue"]
        self.assertEqual(len(total), 1)
        self.assertEqual(total[0].dax_code, "CUSTOM")  # Nicht ueberschrieben

    def test_import_bim_append(self):
        """Test: BIM-Import im Append-Modus fuegt alles hinzu."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        project.measures.append(Measure(name="Total Revenue", dax_code="CUSTOM"))

        options = ImportOptions(merge_mode="append")
        report = import_file(bim, project, options)

        # Beide Measures sollten vorhanden sein
        total = [m for m in project.measures if m.name == "Total Revenue"]
        self.assertEqual(len(total), 2)

    def test_import_pbix(self):
        """Test: PBIX-Import liefert Seiten und Queries."""
        pbix = _create_test_pbix(self.tmp)
        project = Project()
        options = ImportOptions(use_pbitools=False)
        report = import_file(pbix, project, options)

        self.assertTrue(report.success)
        self.assertEqual(report.file_type, "pbix")
        self.assertGreater(len(project.report_pages), 0)
        self.assertGreater(len(project.power_queries), 0)

    def test_import_pbix_not_available(self):
        """Test: PBIX ohne pbi-tools meldet fehlende Measures/Relationships."""
        pbix = _create_test_pbix(self.tmp)
        project = Project()
        options = ImportOptions(use_pbitools=False)
        report = import_file(pbix, project, options)

        self.assertTrue(any("Measures" in na for na in report.not_available)
                        or any("Beziehungen" in na for na in report.not_available))

    def test_import_measures_as_kpis(self):
        """Test: Measures werden auch als KPIs importiert."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        options = ImportOptions(import_measures_as_kpis=True)
        report = import_file(bim, project, options)

        self.assertGreater(len(project.kpis), 0)
        kpi_names = [k.name for k in project.kpis]
        self.assertIn("Total Revenue", kpi_names)

    def test_import_rls(self):
        """Test: RLS-Rollen werden in Governance uebernommen."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        import_file(bim, project)

        self.assertIn("RegionFilter", project.governance.rls_notes)

    def test_import_report(self):
        """Test: ImportReport summary_text funktioniert."""
        report = ImportReport(
            success=True,
            file_type="bim",
            imported={"measures": 5, "tables": 3},
            skipped={"hidden_tables": 2},
            not_available=["Berichtsseiten"],
        )
        text = report.summary_text()
        self.assertIn("5 Measures", text)
        self.assertIn("3 Tabellen", text)
        self.assertIn("Berichtsseiten", text)

    def test_import_unknown_file(self):
        """Test: Unbekannter Dateityp gibt Fehler zurueck."""
        txt = self.tmp / "test.txt"
        txt.write_text("hello")
        project = Project()
        report = import_file(txt, project)
        self.assertFalse(report.success)

    def test_import_date_logic(self):
        """Test: Datumslogik-Hinweise werden uebernommen."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        import_file(bim, project)
        self.assertIn("Dim_Date", project.data_model.date_logic_notes)

    def test_import_data_sources(self):
        """Test: Datenquellen werden aus BIM extrahiert."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        import_file(bim, project)
        self.assertGreater(len(project.data_sources), 0)

    def test_import_relationships(self):
        """Test: Beziehungen werden uebernommen."""
        bim = _create_test_bim(self.tmp)
        project = Project()
        import_file(bim, project)
        self.assertGreater(len(project.data_model.relationships), 0)


class TestMergeList(unittest.TestCase):
    """Tests fuer die _merge_list Hilfsfunktion."""

    def test_replace(self):
        existing = [Measure(name="A")]
        new = [Measure(name="B")]
        result, skipped = _merge_list(existing, new, "replace", "name")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "B")
        self.assertEqual(skipped, 0)

    def test_append(self):
        existing = [Measure(name="A")]
        new = [Measure(name="B")]
        result, skipped = _merge_list(existing, new, "append", "name")
        self.assertEqual(len(result), 2)
        self.assertEqual(skipped, 0)

    def test_merge_skip_existing(self):
        existing = [Measure(name="A")]
        new = [Measure(name="a"), Measure(name="B")]
        result, skipped = _merge_list(existing, new, "merge", "name")
        self.assertEqual(len(result), 2)  # A + B
        self.assertEqual(skipped, 1)  # 'a' skipped because 'A' exists

    def test_merge_case_insensitive(self):
        existing = [Measure(name="Total Revenue")]
        new = [Measure(name="total revenue")]
        result, skipped = _merge_list(existing, new, "merge", "name")
        self.assertEqual(len(result), 1)
        self.assertEqual(skipped, 1)


class TestPreviewImport(unittest.TestCase):
    """Tests fuer die Preview-Funktion."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_preview_pbix(self):
        """Test: PBIX-Vorschau zeigt Seitenanzahl."""
        pbix = _create_test_pbix(self.tmp)
        preview = preview_import(pbix)
        self.assertEqual(preview.file_type, "pbix")
        self.assertEqual(preview.page_count, 2)
        self.assertGreater(preview.visual_count, 0)

    def test_preview_bim(self):
        """Test: BIM-Vorschau zeigt Tabellenanzahl."""
        bim = _create_test_bim(self.tmp)
        preview = preview_import(bim)
        self.assertIn(preview.file_type, ("bim", "json_bim"))
        self.assertGreater(preview.table_count, 0)
        self.assertGreater(preview.measure_count, 0)
        self.assertGreater(preview.relationship_count, 0)


class TestPbiToolsAvailability(unittest.TestCase):
    """Tests fuer pbi-tools Verfuegbarkeitspruefung."""

    def test_pbitools_check(self):
        """Test: pbitools_available gibt bool zurueck (ohne Crash)."""
        result = pbitools_available()
        self.assertIsInstance(result, bool)


# ══════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main()
