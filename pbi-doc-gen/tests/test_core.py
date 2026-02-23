"""
Unit tests for the Power BI Documentation Generator.

Run:  python -m pytest tests/ -v
  or: python -m unittest tests/test_core.py -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Project, ProjectMeta, KPI, DataSource, Measure, ChangeLogEntry, Environment
from src.storage import save_project, load_project
from src.generator import gen_measures, gen_data_sources, gen_kpis, gen_change_log, generate_docs
from src.importers import import_measures_from_file, export_measures_to_file


class TestModelsRoundTrip(unittest.TestCase):
    """Test that Project can round-trip through dict serialization."""

    def _make_project(self) -> Project:
        p = Project()
        p.meta = ProjectMeta(
            report_name="Test Report",
            owner="Tester",
            author="Tester",
            version="1.0.0",
            environments=[Environment(name="DEV", workspace="WS-DEV", url="http://dev")],
        )
        p.kpis = [KPI(name="KPI A", business_description="Desc A", granularity="Monat")]
        p.data_sources = [DataSource(name="SQL Source", source_type="SQL", connection_info="host/db")]
        p.measures = [Measure(name="Total", dax_code="SUM(T[Value])", display_folder="Folder")]
        p.change_log = [ChangeLogEntry(version="1.0", description="Init", impact="major")]
        return p

    def test_to_dict_and_back(self):
        p = self._make_project()
        d = p.to_dict()
        p2 = Project.from_dict(d)
        self.assertEqual(p2.meta.report_name, "Test Report")
        self.assertEqual(len(p2.kpis), 1)
        self.assertEqual(p2.kpis[0].name, "KPI A")
        self.assertEqual(len(p2.measures), 1)
        self.assertEqual(p2.measures[0].dax_code, "SUM(T[Value])")

    def test_empty_project(self):
        p = Project()
        d = p.to_dict()
        p2 = Project.from_dict(d)
        self.assertEqual(p2.meta.report_name, "")
        self.assertEqual(len(p2.kpis), 0)


class TestStorage(unittest.TestCase):
    """Test save/load project to YAML and JSON."""

    def _make_project(self) -> Project:
        p = Project()
        p.meta.report_name = "Storage Test"
        p.measures = [Measure(name="M1", dax_code="1+1")]
        return p

    def test_save_load_json(self):
        p = self._make_project()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.json"
            save_project(p, path)
            self.assertTrue(path.exists())
            p2 = load_project(path)
            self.assertEqual(p2.meta.report_name, "Storage Test")
            self.assertEqual(p2.measures[0].name, "M1")

    def test_save_load_yaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        p = self._make_project()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.yml"
            save_project(p, path)
            self.assertTrue(path.exists())
            p2 = load_project(path)
            self.assertEqual(p2.meta.report_name, "Storage Test")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_project(Path("/nonexistent/path.yml"))


class TestGenerator(unittest.TestCase):
    """Test Markdown generation."""

    def _make_project(self) -> Project:
        p = Project()
        p.meta = ProjectMeta(report_name="Gen Test", owner="O", author="A", version="1.0")
        p.data_sources = [
            DataSource(name="SAP", source_type="SQL", connection_info="host:30015",
                       refresh_cadence="Täglich", gateway_required=True, gateway_name="GW1"),
            DataSource(name="Excel", source_type="Excel", connection_info="SharePoint/file.xlsx",
                       refresh_cadence="Wöchentlich"),
        ]
        p.measures = [
            Measure(name="Total Hours", dax_code="SUM(F[Hours])", display_folder="Time",
                    description="Gesamtstunden"),
            Measure(name="Avg Hours", dax_code="AVERAGE(F[Hours])", display_folder="Time",
                    description="Durchschnitt"),
        ]
        p.change_log = [
            ChangeLogEntry(version="1.0", date="2025-01-01", description="Start",
                           author="A", impact="major"),
        ]
        return p

    def test_gen_measures_contains_dax(self):
        md = gen_measures(self._make_project())
        self.assertIn("```dax", md)
        self.assertIn("SUM(F[Hours])", md)
        self.assertIn("Total Hours", md)
        self.assertIn("Avg Hours", md)

    def test_gen_data_sources_table(self):
        md = gen_data_sources(self._make_project())
        self.assertIn("| SAP |", md)
        self.assertIn("GW1", md)
        self.assertIn("| Excel |", md)

    def test_gen_change_log_table(self):
        md = gen_change_log(self._make_project())
        self.assertIn("| 1.0 |", md)
        self.assertIn("major", md)

    def test_gen_kpis_empty(self):
        p = Project()
        md = gen_kpis(p)
        self.assertIn("Noch keine KPIs dokumentiert", md)

    def test_generate_docs_creates_files(self):
        p = self._make_project()
        with tempfile.TemporaryDirectory() as td:
            out = generate_docs(p, Path(td) / "docs")
            self.assertTrue((out / "index.md").exists())
            self.assertTrue((out / "05_measures" / "measures.md").exists())
            self.assertTrue((out / "02_data_sources" / "data_sources.md").exists())
            self.assertTrue((out / "08_change_log" / "change_log.md").exists())


class TestImporters(unittest.TestCase):
    """Test measure import/export."""

    def test_import_measures(self):
        content = """MEASURE: Total Sales
FOLDER: Sales
DESCRIPTION: Sum of all sales
DAX:
Total Sales = SUM( Sales[Amount] )

MEASURE: Avg Sales
DAX:
Avg Sales = AVERAGE( Sales[Amount] )
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            measures = import_measures_from_file(Path(f.name))
        os.unlink(f.name)

        self.assertEqual(len(measures), 2)
        self.assertEqual(measures[0].name, "Total Sales")
        self.assertEqual(measures[0].display_folder, "Sales")
        self.assertIn("SUM", measures[0].dax_code)
        self.assertEqual(measures[1].name, "Avg Sales")

    def test_export_roundtrip(self):
        measures = [
            Measure(name="M1", dax_code="1+1", display_folder="F1", description="Desc1"),
            Measure(name="M2", dax_code="2+2"),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "export.txt"
            export_measures_to_file(measures, path)
            imported = import_measures_from_file(path)
            self.assertEqual(len(imported), 2)
            self.assertEqual(imported[0].name, "M1")
            self.assertEqual(imported[1].dax_code, "2+2")


if __name__ == "__main__":
    unittest.main()
