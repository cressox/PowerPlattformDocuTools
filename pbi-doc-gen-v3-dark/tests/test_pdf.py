"""
Tests for PDF export module.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import (
    Project, ProjectMeta, Environment, KPI, DataSource, Measure,
    ChangeLogEntry, DataModel, ModelTable, ModelRelationship,
    PowerQuery, ReportPage, Visual, Governance,
)

try:
    from src.pdf_export import generate_pdf, default_pdf_filename
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@unittest.skipUnless(HAS_REPORTLAB, "reportlab not installed")
class TestPDFExport(unittest.TestCase):

    def _make_project(self) -> Project:
        p = Project()
        p.meta = ProjectMeta(
            report_name="Test PDF Report",
            short_description="Ein Test-PDF",
            owner="Tester",
            author="Tester",
            version="1.0.0",
            audience="QA Team",
            environments=[Environment(name="PROD", workspace="WS", url="http://pbi")],
        )
        p.kpis = [KPI(name="KPI A", business_description="Desc", granularity="Monat",
                       technical_definition="SUM(x)", filters_context="Filter A")]
        p.data_sources = [DataSource(name="SQL", source_type="SQL", connection_info="host/db",
                                      refresh_cadence="Daily", gateway_required=True, gateway_name="GW")]
        p.measures = [Measure(name="Total", dax_code="SUM(T[Val])", display_folder="F",
                               description="Total sum")]
        p.power_queries = [PowerQuery(query_name="qry_1", purpose="Load data",
                                       m_code='let\n    Source = 1\nin\n    Source')]
        p.data_model = DataModel(
            tables=[ModelTable(name="Fact", table_type="Fakt", keys="PK: ID")],
            relationships=[ModelRelationship(from_table="Fact", from_column="DimID",
                                              to_table="Dim", to_column="ID",
                                              cardinality="N:1", filter_direction="Single")],
            date_logic_notes="ISO weeks",
        )
        p.report_pages = [ReportPage(page_name="Overview", purpose="Main page",
                                      visuals=[Visual(name="Chart", description="Shows data")])]
        p.governance = Governance(refresh_schedule="Daily 6am", rls_notes="RLS active")
        p.change_log = [ChangeLogEntry(version="1.0", description="Init", author="T", impact="major")]
        return p

    def test_generate_pdf_creates_file(self):
        p = self._make_project()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test_output.pdf"
            result = generate_pdf(p, path)
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 1000)  # Should be a real PDF

    def test_generate_pdf_empty_project(self):
        p = Project()
        p.meta.report_name = "Empty"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "empty.pdf"
            result = generate_pdf(p, path)
            self.assertTrue(result.exists())

    def test_default_filename(self):
        p = Project()
        p.meta.report_name = "HR Zeitkonten Report"
        name = default_pdf_filename(p)
        self.assertIn("HR_Zeitkonten_Report", name)
        self.assertTrue(name.endswith(".pdf"))

    def test_default_filename_special_chars(self):
        p = Project()
        p.meta.report_name = "Report/Test (v2)"
        name = default_pdf_filename(p)
        self.assertNotIn("/", name)
        self.assertTrue(name.endswith(".pdf"))


if __name__ == "__main__":
    unittest.main()
