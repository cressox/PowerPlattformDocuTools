"""
Main window – wires all pages, sidebar, toolbar, and actions together.
"""

from __future__ import annotations
import os, sys, traceback
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QMessageBox,
    QProgressDialog, QApplication, QFrame, QColorDialog, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor

try:
    from .theme import *
    from .widgets import (
        CodeEditor, ScreenshotPanel, Sidebar, FormPage, ListEditorPage,
        SCREENSHOTS_DIR,
    )
    from .preview import PreviewPage

    from ..models import (
        Project, ProjectMeta, Environment, CIBranding, Screenshot,
        KPI, DataSource, PowerQuery, DataModel, ModelTable, ModelRelationship,
        Measure, Visual, ReportPage, Governance, ChangeLogEntry,
        _new_id, _today,
    )
    from ..storage import save_project, load_project, project_exists, DEFAULT_PROJECT_FILE
    from ..generator import generate_docs
    from ..pdf_export import generate_pdf, default_pdf_filename
except ImportError:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.ui.theme import *
    from src.ui.widgets import (
        CodeEditor, ScreenshotPanel, Sidebar, FormPage, ListEditorPage,
        SCREENSHOTS_DIR,
    )
    from src.ui.preview import PreviewPage

    from src.models import (
        Project, ProjectMeta, Environment, CIBranding, Screenshot,
        KPI, DataSource, PowerQuery, DataModel, ModelTable, ModelRelationship,
        Measure, Visual, ReportPage, Governance, ChangeLogEntry,
        _new_id, _today,
    )
    from src.storage import save_project, load_project, project_exists, DEFAULT_PROJECT_FILE
    from src.generator import generate_docs
    from src.pdf_export import generate_pdf, default_pdf_filename


# ══════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════

class DashboardPage(FormPage):
    open_project_signal = QApplication.instance().__class__  # placeholder
    new_project_signal = QApplication.instance().__class__

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtCore import Signal
        self.add_title("Dashboard")
        self.add_subtitle("Willkommen beim Power BI Documentation Generator")

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("➕  Neues Projekt")
        self.btn_new.setObjectName("primary")
        self.btn_new.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(self.btn_new)

        self.btn_open = QPushButton("📂  Projekt oeffnen …")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(self.btn_open)
        btn_row.addStretch()
        self._layout.addLayout(btn_row)

        # Stats cards
        cards_row = QHBoxLayout()
        self.stat_cards = {}
        for key, icon, label in [
            ("kpis", "🎯", "KPIs"), ("sources", "🗄️", "Datenquellen"),
            ("measures", "📐", "Measures"), ("pages", "📊", "Seiten"),
            ("queries", "⚙️", "Queries"), ("changes", "📝", "Aenderungen"),
        ]:
            card = QGroupBox()
            card.setFixedSize(150, 80)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 12, 12, 8)
            num_lbl = QLabel("0")
            num_lbl.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {ACCENT}; background: transparent;")
            cl.addWidget(num_lbl)
            name_lbl = QLabel(f"{icon} {label}")
            name_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;")
            cl.addWidget(name_lbl)
            cards_row.addWidget(card)
            self.stat_cards[key] = num_lbl
        cards_row.addStretch()
        self._layout.addLayout(cards_row)

        # Project info card
        self.card = QGroupBox("Aktuelles Projekt")
        card_layout = QFormLayout(self.card)
        card_layout.setLabelAlignment(Qt.AlignRight)
        self.lbl_name = QLabel("-")
        self.lbl_owner = QLabel("-")
        self.lbl_version = QLabel("-")
        self.lbl_date = QLabel("-")
        self.lbl_path = QLabel("-")
        self.lbl_path.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        card_layout.addRow("Berichtsname:", self.lbl_name)
        card_layout.addRow("Eigentuemer:", self.lbl_owner)
        card_layout.addRow("Version:", self.lbl_version)
        card_layout.addRow("Datum:", self.lbl_date)
        card_layout.addRow("Projektdatei:", self.lbl_path)
        self._layout.addWidget(self.card)
        self._layout.addStretch()

    def refresh(self, project: Project, path: str):
        m = project.meta
        self.lbl_name.setText(m.report_name or "-")
        self.lbl_owner.setText(m.owner or "-")
        self.lbl_version.setText(m.version or "-")
        self.lbl_date.setText(m.date or "-")
        self.lbl_path.setText(path)
        self.stat_cards["kpis"].setText(str(len(project.kpis)))
        self.stat_cards["sources"].setText(str(len(project.data_sources)))
        self.stat_cards["measures"].setText(str(len(project.measures)))
        self.stat_cards["pages"].setText(str(len(project.report_pages)))
        self.stat_cards["queries"].setText(str(len(project.power_queries)))
        self.stat_cards["changes"].setText(str(len(project.change_log)))


# ══════════════════════════════════════════════════════════════════
# METADATA PAGE
# ══════════════════════════════════════════════════════════════════

class MetadataPage(FormPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_title("Projekt-Metadaten")
        self.add_subtitle("Allgemeine Informationen zum Power BI Bericht")

        grp = QGroupBox("Bericht")
        form = QFormLayout(grp)
        form.setLabelAlignment(Qt.AlignRight)
        self.ed_name = QLineEdit(); self.ed_name.setPlaceholderText("z.B. HR Zeitkonten Report")
        self.ed_desc = QTextEdit(); self.ed_desc.setMaximumHeight(80)
        self.ed_audience = QLineEdit()
        self.ed_owner = QLineEdit()
        self.ed_author = QLineEdit()
        self.ed_version = QLineEdit()
        self.ed_date = QLineEdit(); self.ed_date.setPlaceholderText("YYYY-MM-DD")
        self.ed_pbi_url = QLineEdit(); self.ed_pbi_url.setPlaceholderText("https://app.powerbi.com/…")
        self.ed_sp_url = QLineEdit()
        form.addRow("Berichtsname *:", self.ed_name)
        form.addRow("Beschreibung:", self.ed_desc)
        form.addRow("Zielgruppe:", self.ed_audience)
        form.addRow("Eigentuemer:", self.ed_owner)
        form.addRow("Autor:", self.ed_author)
        form.addRow("Version:", self.ed_version)
        form.addRow("Datum:", self.ed_date)
        form.addRow("Power BI URL:", self.ed_pbi_url)
        form.addRow("SharePoint URL:", self.ed_sp_url)
        self._layout.addWidget(grp)

        # Environments table
        self.env_grp = QGroupBox("Umgebungen")
        env_lay = QVBoxLayout(self.env_grp)
        self.env_table = QTableWidget(0, 3)
        self.env_table.setHorizontalHeaderLabels(["Umgebung", "Arbeitsbereich", "URL"])
        self.env_table.horizontalHeader().setStretchLastSection(True)
        self.env_table.setMaximumHeight(140)
        self.env_table.verticalHeader().setVisible(False)
        env_lay.addWidget(self.env_table)
        eb = QHBoxLayout()
        b1 = QPushButton("➕ Umgebung"); b1.clicked.connect(self._add_env)
        b2 = QPushButton("🗑️ Entfernen"); b2.clicked.connect(self._del_env)
        eb.addWidget(b1); eb.addWidget(b2); eb.addStretch()
        env_lay.addLayout(eb)
        self._layout.addWidget(self.env_grp)
        self._layout.addStretch()

    def _add_env(self):
        r = self.env_table.rowCount(); self.env_table.insertRow(r)
        for c in range(3): self.env_table.setItem(r, c, QTableWidgetItem(""))
    def _del_env(self):
        r = self.env_table.currentRow()
        if r >= 0: self.env_table.removeRow(r)

    def load(self, m: ProjectMeta):
        self.ed_name.setText(m.report_name); self.ed_desc.setPlainText(m.short_description)
        self.ed_audience.setText(m.audience); self.ed_owner.setText(m.owner)
        self.ed_author.setText(m.author); self.ed_version.setText(m.version)
        self.ed_date.setText(m.date); self.ed_pbi_url.setText(m.powerbi_service_url)
        self.ed_sp_url.setText(m.sharepoint_folder_url)
        self.env_table.setRowCount(0)
        for env in m.environments:
            r = self.env_table.rowCount(); self.env_table.insertRow(r)
            self.env_table.setItem(r, 0, QTableWidgetItem(env.name))
            self.env_table.setItem(r, 1, QTableWidgetItem(env.workspace))
            self.env_table.setItem(r, 2, QTableWidgetItem(env.url))

    def save(self, m: ProjectMeta):
        m.report_name = self.ed_name.text().strip()
        m.short_description = self.ed_desc.toPlainText().strip()
        m.audience = self.ed_audience.text().strip(); m.owner = self.ed_owner.text().strip()
        m.author = self.ed_author.text().strip(); m.version = self.ed_version.text().strip()
        m.date = self.ed_date.text().strip(); m.powerbi_service_url = self.ed_pbi_url.text().strip()
        m.sharepoint_folder_url = self.ed_sp_url.text().strip()
        m.environments = []
        for r in range(self.env_table.rowCount()):
            n = (self.env_table.item(r,0) or QTableWidgetItem("")).text().strip()
            if n:
                m.environments.append(Environment(
                    name=n,
                    workspace=(self.env_table.item(r,1) or QTableWidgetItem("")).text().strip(),
                    url=(self.env_table.item(r,2) or QTableWidgetItem("")).text().strip()))

    def validate(self) -> Optional[str]:
        if not self.ed_name.text().strip(): return "Berichtsname ist erforderlich."
        return None


# ══════════════════════════════════════════════════════════════════
# CI / BRANDING PAGE
# ══════════════════════════════════════════════════════════════════

class CIBrandingPage(FormPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_title("CI / Branding")
        self.add_subtitle("Corporate-Design-Einstellungen fuer kundenspezifische Dokumentation")

        grp = QGroupBox("Firmendaten")
        form = QFormLayout(grp)
        form.setLabelAlignment(Qt.AlignRight)
        self.ed_company = QLineEdit(); self.ed_company.setPlaceholderText("z.B. Contoso GmbH")
        self.ed_footer = QLineEdit()
        self.ed_header = QLineEdit()
        self.ed_subtitle = QLineEdit()
        self.ed_confidential = QLineEdit(); self.ed_confidential.setPlaceholderText("z.B. Vertraulich")
        self.ed_font = QLineEdit(); self.ed_font.setPlaceholderText("Optional: Schriftart")
        form.addRow("Firmenname:", self.ed_company)
        form.addRow("Footer-Text:", self.ed_footer)
        form.addRow("Header-Text:", self.ed_header)
        form.addRow("Untertitel Cover:", self.ed_subtitle)
        form.addRow("Vertraulichkeit:", self.ed_confidential)
        form.addRow("Schriftart:", self.ed_font)
        self._layout.addWidget(grp)

        # Colours
        col_grp = QGroupBox("Farben")
        col_lay = QHBoxLayout(col_grp)
        self.color_btns = {}
        for key, label, default in [
            ("primary", "Primaer", "#1B3A5C"),
            ("accent", "Akzent", "#F2C811"),
            ("secondary", "Sekundaer", "#2563EB"),
        ]:
            vl = QVBoxLayout()
            btn = QPushButton()
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"background: {default}; border-radius: 8px; border: 2px solid {BORDER};")
            btn.clicked.connect(lambda checked, k=key: self._pick_color(k))
            vl.addWidget(btn, alignment=Qt.AlignCenter)
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
            vl.addWidget(lbl)
            col_lay.addLayout(vl)
            self.color_btns[key] = (btn, default)
        col_lay.addStretch()
        self._layout.addWidget(col_grp)

        # Logo
        logo_grp = QGroupBox("Firmenlogo")
        logo_lay = QHBoxLayout(logo_grp)
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(120, 60)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setStyleSheet(f"background: {BG_INPUT}; border-radius: {RADIUS_SM}; border: 1px solid {BORDER};")
        logo_lay.addWidget(self.logo_preview)
        self.btn_logo = QPushButton("📂 Logo waehlen …")
        self.btn_logo.clicked.connect(self._pick_logo)
        logo_lay.addWidget(self.btn_logo)
        self.lbl_logo_path = QLabel("Kein Logo")
        self.lbl_logo_path.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        logo_lay.addWidget(self.lbl_logo_path)
        logo_lay.addStretch()
        self._layout.addWidget(logo_grp)
        self._layout.addStretch()

        self._logo_path = ""
        self._colors = {"primary": "#1B3A5C", "accent": "#F2C811", "secondary": "#2563EB"}

    def _pick_color(self, key: str):
        btn, current = self.color_btns[key]
        color = QColorDialog.getColor(QColor(self._colors.get(key, current)), self)
        if color.isValid():
            hex_c = color.name()
            self._colors[key] = hex_c
            btn.setStyleSheet(f"background: {hex_c}; border-radius: 8px; border: 2px solid {BORDER};")

    def _pick_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Logo waehlen", "",
                    "Bilder (*.png *.jpg *.jpeg *.svg);;Alle (*)")
        if path:
            self._logo_path = path
            self.lbl_logo_path.setText(Path(path).name)
            pm = QPixmap(path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(pm)

    def load(self, ci: CIBranding):
        self.ed_company.setText(ci.company_name)
        self.ed_footer.setText(ci.footer_text)
        self.ed_header.setText(ci.header_text)
        self.ed_subtitle.setText(ci.cover_subtitle)
        self.ed_confidential.setText(ci.confidentiality_notice)
        self.ed_font.setText(ci.font_name)
        self._logo_path = ci.logo_path
        if ci.logo_path and Path(ci.logo_path).exists():
            self.lbl_logo_path.setText(Path(ci.logo_path).name)
            pm = QPixmap(ci.logo_path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(pm)
        for key, attr in [("primary", "primary_color"), ("accent", "accent_color"), ("secondary", "secondary_color")]:
            val = getattr(ci, attr, "")
            if val:
                self._colors[key] = val
                btn, _ = self.color_btns[key]
                btn.setStyleSheet(f"background: {val}; border-radius: 8px; border: 2px solid {BORDER};")

    def save(self, ci: CIBranding):
        ci.company_name = self.ed_company.text().strip()
        ci.footer_text = self.ed_footer.text().strip()
        ci.header_text = self.ed_header.text().strip()
        ci.cover_subtitle = self.ed_subtitle.text().strip()
        ci.confidentiality_notice = self.ed_confidential.text().strip()
        ci.font_name = self.ed_font.text().strip()
        ci.logo_path = self._logo_path
        ci.primary_color = self._colors.get("primary", "#1B3A5C")
        ci.accent_color = self._colors.get("accent", "#F2C811")
        ci.secondary_color = self._colors.get("secondary", "#2563EB")


# ══════════════════════════════════════════════════════════════════
# SECTION PAGES (KPIs, DataSources, Queries, Measures, Pages, ChangeLog)
# ══════════════════════════════════════════════════════════════════

class KPIPage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("KPIs & Kennzahlen", "Fachliche und technische KPI-Definitionen",
                         ["Name", "Granularitaet", "Beschreibung"], p)
    def _build_form(self, form):
        self.f_name = QLineEdit()
        self.f_desc = QTextEdit(); self.f_desc.setMaximumHeight(60)
        self.f_tech = QTextEdit(); self.f_tech.setMaximumHeight(60)
        self.f_gran = QLineEdit(); self.f_gran.setPlaceholderText("z.B. ISO-Woche / Person")
        self.f_filter = QLineEdit(); self.f_caveats = QLineEdit()
        form.addRow("Name *:", self.f_name); form.addRow("Beschreibung *:", self.f_desc)
        form.addRow("Techn. Definition:", self.f_tech); form.addRow("Granularitaet:", self.f_gran)
        form.addRow("Filter / Kontext:", self.f_filter); form.addRow("Einschraenkungen:", self.f_caveats)
    def _validate(self):
        if not self.f_name.text().strip(): return "KPI-Name ist erforderlich."
        if not self.f_desc.toPlainText().strip(): return "Beschreibung ist erforderlich."
        return None
    def _clear_form(self):
        for w in (self.f_name, self.f_gran, self.f_filter, self.f_caveats): w.clear()
        self.f_desc.clear(); self.f_tech.clear()
    def _item_to_row(self, k: KPI): return [k.name, k.granularity, k.business_description[:80]]
    def form_to_item(self, existing=None):
        k = existing or KPI()
        k.name=self.f_name.text().strip(); k.business_description=self.f_desc.toPlainText().strip()
        k.technical_definition=self.f_tech.toPlainText().strip(); k.granularity=self.f_gran.text().strip()
        k.filters_context=self.f_filter.text().strip(); k.caveats=self.f_caveats.text().strip()
        return k
    def load_to_form(self, k: KPI):
        self.f_name.setText(k.name); self.f_desc.setPlainText(k.business_description)
        self.f_tech.setPlainText(k.technical_definition); self.f_gran.setText(k.granularity)
        self.f_filter.setText(k.filters_context); self.f_caveats.setText(k.caveats)


class DataSourcePage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("Datenquellen", "Verbindungen und Datenherkunft",
                         ["Name", "Typ", "Aktualisierung", "Gateway"], p)
    def _build_form(self, form):
        self.f_name = QLineEdit()
        self.f_type = QComboBox(); self.f_type.setEditable(True)
        self.f_type.addItems(["SQL", "SQL (SAP HANA)", "API", "Excel", "Excel (SharePoint)",
                               "SharePoint List", "CSV", "OData", "Dataverse"])
        self.f_conn = QLineEdit(); self.f_conn.setPlaceholderText("Host/DB – keine Passwoerter!")
        self.f_refresh = QLineEdit()
        self.f_gw = QCheckBox("Gateway erforderlich"); self.f_gw_name = QLineEdit()
        self.f_gw_name.setEnabled(False); self.f_gw.toggled.connect(self.f_gw_name.setEnabled)
        self.f_owner = QLineEdit()
        form.addRow("Name *:", self.f_name); form.addRow("Typ *:", self.f_type)
        form.addRow("Verbindung:", self.f_conn); form.addRow("Aktualisierung:", self.f_refresh)
        form.addRow("", self.f_gw); form.addRow("Gateway:", self.f_gw_name)
        form.addRow("Verantwortlich:", self.f_owner)
    def _validate(self):
        if not self.f_name.text().strip(): return "Quellenname ist erforderlich."
        return None
    def _clear_form(self):
        self.f_name.clear(); self.f_type.setCurrentIndex(0); self.f_conn.clear()
        self.f_refresh.clear(); self.f_gw.setChecked(False); self.f_gw_name.clear(); self.f_owner.clear()
    def _item_to_row(self, s):
        gw = s.gateway_name if s.gateway_required else "-"
        return [s.name, s.source_type, s.refresh_cadence, gw]
    def form_to_item(self, existing=None):
        s = existing or DataSource()
        s.name=self.f_name.text().strip(); s.source_type=self.f_type.currentText().strip()
        s.connection_info=self.f_conn.text().strip(); s.refresh_cadence=self.f_refresh.text().strip()
        s.gateway_required=self.f_gw.isChecked(); s.gateway_name=self.f_gw_name.text().strip()
        s.owner_contact=self.f_owner.text().strip()
        return s
    def load_to_form(self, s):
        self.f_name.setText(s.name); self.f_type.setCurrentText(s.source_type)
        self.f_conn.setText(s.connection_info); self.f_refresh.setText(s.refresh_cadence)
        self.f_gw.setChecked(s.gateway_required); self.f_gw_name.setText(s.gateway_name)
        self.f_owner.setText(s.owner_contact)


class PowerQueryPage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("Power Query (M)", "Abfragen dokumentieren",
                         ["Abfrage", "Zweck", "Ausgabetabelle"], p)
    def _build_form(self, form):
        self.f_name = QLineEdit(); self.f_purpose = QLineEdit()
        self.f_inputs = QLineEdit()
        self.f_transforms = QTextEdit(); self.f_transforms.setMaximumHeight(60)
        self.f_mcode = CodeEditor("let\n    Source = ...\nin\n    Source")
        self.f_mcode.setMinimumHeight(150)
        self.f_output = QLineEdit(); self.f_notes = QLineEdit()
        form.addRow("Abfragename *:", self.f_name); form.addRow("Zweck:", self.f_purpose)
        form.addRow("Eingaben:", self.f_inputs); form.addRow("Transformationen:", self.f_transforms)
        form.addRow("M-Code:", self.f_mcode)
        form.addRow("Ausgabetabelle:", self.f_output); form.addRow("Hinweise:", self.f_notes)
    def _validate(self):
        if not self.f_name.text().strip(): return "Abfragename ist erforderlich."
        return None
    def _clear_form(self):
        for w in (self.f_name, self.f_purpose, self.f_inputs, self.f_output, self.f_notes): w.clear()
        self.f_transforms.clear(); self.f_mcode.clear()
    def _item_to_row(self, q): return [q.query_name, q.purpose, q.output_table]
    def form_to_item(self, existing=None):
        q = existing or PowerQuery()
        q.query_name=self.f_name.text().strip(); q.purpose=self.f_purpose.text().strip()
        q.inputs=self.f_inputs.text().strip(); q.major_transformations=self.f_transforms.toPlainText().strip()
        q.m_code=self.f_mcode.toPlainText(); q.output_table=self.f_output.text().strip()
        q.notes=self.f_notes.text().strip()
        return q
    def load_to_form(self, q):
        self.f_name.setText(q.query_name); self.f_purpose.setText(q.purpose)
        self.f_inputs.setText(q.inputs); self.f_transforms.setPlainText(q.major_transformations)
        self.f_mcode.setPlainText(q.m_code); self.f_output.setText(q.output_table)
        self.f_notes.setText(q.notes)


class DataModelPage(FormPage):
    def __init__(self, p=None):
        super().__init__(p)
        self.add_title("Datenmodell")
        self.add_subtitle("Tabellen, Beziehungen und Datumslogik")
        g1 = QGroupBox("Tabellen"); t1 = QVBoxLayout(g1)
        self.tbl = QTableWidget(0,4)
        self.tbl.setHorizontalHeaderLabels(["Name","Typ","Schluessel","Beschreibung"])
        self.tbl.horizontalHeader().setStretchLastSection(True); self.tbl.setMaximumHeight(180)
        self.tbl.verticalHeader().setVisible(False); t1.addWidget(self.tbl)
        b = QHBoxLayout()
        b1=QPushButton("➕"); b1.clicked.connect(lambda: self._ar(self.tbl,4))
        b2=QPushButton("🗑️"); b2.clicked.connect(lambda: self._dr(self.tbl))
        b.addWidget(b1); b.addWidget(b2); b.addStretch(); t1.addLayout(b)
        self._layout.addWidget(g1)
        g2 = QGroupBox("Beziehungen"); t2 = QVBoxLayout(g2)
        self.rel = QTableWidget(0,6)
        self.rel.setHorizontalHeaderLabels(["Von-Tab","Von-Sp","Nach-Tab","Nach-Sp","Kard.","Filter"])
        self.rel.horizontalHeader().setStretchLastSection(True); self.rel.setMaximumHeight(180)
        self.rel.verticalHeader().setVisible(False); t2.addWidget(self.rel)
        b3 = QHBoxLayout()
        b4=QPushButton("➕"); b4.clicked.connect(lambda: self._ar(self.rel,6))
        b5=QPushButton("🗑️"); b5.clicked.connect(lambda: self._dr(self.rel))
        b3.addWidget(b4); b3.addWidget(b5); b3.addStretch(); t2.addLayout(b3)
        self._layout.addWidget(g2)
        g3 = QGroupBox("Hinweise"); n = QFormLayout(g3)
        self.f_date = QTextEdit(); self.f_date.setMaximumHeight(80)
        self.f_notes = QTextEdit(); self.f_notes.setMaximumHeight(80)
        n.addRow("Datumslogik:", self.f_date); n.addRow("Anmerkungen:", self.f_notes)
        self._layout.addWidget(g3)
        self.screenshots = ScreenshotPanel("data_model")
        self._layout.addWidget(self.screenshots)
        self._layout.addStretch()
    def _ar(self, t, c):
        r=t.rowCount(); t.insertRow(r)
        for i in range(c): t.setItem(r,i,QTableWidgetItem(""))
    def _dr(self, t):
        r=t.currentRow()
        if r>=0: t.removeRow(r)
    def _c(self,t,r,c):
        i=t.item(r,c); return i.text() if i else ""
    def load(self, dm):
        self.tbl.setRowCount(0)
        for t in dm.tables:
            r=self.tbl.rowCount(); self.tbl.insertRow(r)
            for c,v in enumerate([t.name,t.table_type,t.keys,t.description]):
                self.tbl.setItem(r,c,QTableWidgetItem(v))
        self.rel.setRowCount(0)
        for rl in dm.relationships:
            r=self.rel.rowCount(); self.rel.insertRow(r)
            for c,v in enumerate([rl.from_table,rl.from_column,rl.to_table,rl.to_column,rl.cardinality,rl.filter_direction]):
                self.rel.setItem(r,c,QTableWidgetItem(v))
        self.f_date.setPlainText(dm.date_logic_notes); self.f_notes.setPlainText(dm.notes)
        self.screenshots.load_filenames(dm.screenshot_paths)
    def save(self, dm):
        dm.tables=[]
        for r in range(self.tbl.rowCount()):
            n=self._c(self.tbl,r,0).strip()
            if n: dm.tables.append(ModelTable(name=n, table_type=self._c(self.tbl,r,1),
                                               keys=self._c(self.tbl,r,2), description=self._c(self.tbl,r,3)))
        dm.relationships=[]
        for r in range(self.rel.rowCount()):
            ft=self._c(self.rel,r,0).strip()
            if ft: dm.relationships.append(ModelRelationship(from_table=ft,from_column=self._c(self.rel,r,1),
                    to_table=self._c(self.rel,r,2),to_column=self._c(self.rel,r,3),
                    cardinality=self._c(self.rel,r,4),filter_direction=self._c(self.rel,r,5)))
        dm.date_logic_notes=self.f_date.toPlainText().strip(); dm.notes=self.f_notes.toPlainText().strip()
        dm.screenshot_paths=self.screenshots.get_filenames()


class MeasuresPage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("Measures (DAX)", "DAX-Measures dokumentieren",
                         ["Name", "Ordner", "Beschreibung"], p)
    def _build_form(self, form):
        self.f_name = QLineEdit(); self.f_folder = QLineEdit(); self.f_desc = QLineEdit()
        self.f_dax = CodeEditor("Measure = SUM( Table[Column] )")
        self.f_dax.setMinimumHeight(150)
        self.f_deps = QLineEdit(); self.f_filter = QLineEdit(); self.f_val = QLineEdit()
        form.addRow("Name *:", self.f_name); form.addRow("Ordner:", self.f_folder)
        form.addRow("Beschreibung:", self.f_desc); form.addRow("DAX-Code *:", self.f_dax)
        form.addRow("Abhaengigkeiten:", self.f_deps); form.addRow("Filterverhalten:", self.f_filter)
        form.addRow("Validierung:", self.f_val)
    def _validate(self):
        if not self.f_name.text().strip(): return "Measure-Name ist erforderlich."
        if not self.f_dax.toPlainText().strip(): return "DAX-Code ist erforderlich."
        return None
    def _clear_form(self):
        for w in (self.f_name,self.f_folder,self.f_desc,self.f_deps,self.f_filter,self.f_val): w.clear()
        self.f_dax.clear()
    def _item_to_row(self, m): return [m.name, m.display_folder, m.description[:80]]
    def form_to_item(self, existing=None):
        m = existing or Measure()
        m.name=self.f_name.text().strip(); m.display_folder=self.f_folder.text().strip()
        m.description=self.f_desc.text().strip(); m.dax_code=self.f_dax.toPlainText()
        m.dependencies=self.f_deps.text().strip(); m.filter_context_notes=self.f_filter.text().strip()
        m.validation_notes=self.f_val.text().strip()
        return m
    def load_to_form(self, m):
        self.f_name.setText(m.name); self.f_folder.setText(m.display_folder)
        self.f_desc.setText(m.description); self.f_dax.setPlainText(m.dax_code)
        self.f_deps.setText(m.dependencies); self.f_filter.setText(m.filter_context_notes)
        self.f_val.setText(m.validation_notes)


class ReportPagesPage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("Berichtsseiten & Visuals", "Seiten und Visuals",
                         ["Seite", "Zweck", "Visuals"], p)
    def _build_form(self, form):
        self.f_name = QLineEdit(); self.f_purpose = QLineEdit()
        self.f_vis = QTextEdit(); self.f_vis.setMaximumHeight(80)
        self.f_vis.setPlaceholderText("Ein Visual pro Zeile: Name | Beschreibung")
        self.f_slicers = QLineEdit(); self.f_notes = QLineEdit()
        self.screenshots = ScreenshotPanel("report_page")
        form.addRow("Seitenname *:", self.f_name); form.addRow("Zweck:", self.f_purpose)
        form.addRow("Visuals:", self.f_vis); form.addRow("Slicer/Filter:", self.f_slicers)
        form.addRow("Hinweise:", self.f_notes); form.addRow("Screenshots:", self.screenshots)
    def _validate(self):
        if not self.f_name.text().strip(): return "Seitenname ist erforderlich."
        return None
    def _clear_form(self):
        for w in (self.f_name,self.f_purpose,self.f_slicers,self.f_notes): w.clear()
        self.f_vis.clear()
    def _item_to_row(self, pg):
        return [pg.page_name, pg.purpose, f"{len(pg.visuals)} Visual(s)"]
    def _parse_visuals(self):
        visuals = []
        for line in self.f_vis.toPlainText().strip().split("\n"):
            line = line.strip()
            if not line: continue
            if "|" in line:
                parts = line.split("|", 1)
                visuals.append(Visual(name=parts[0].strip(), description=parts[1].strip()))
            else:
                visuals.append(Visual(name=line, description=""))
        return visuals
    def form_to_item(self, existing=None):
        pg = existing or ReportPage()
        pg.page_name=self.f_name.text().strip(); pg.purpose=self.f_purpose.text().strip()
        pg.visuals=self._parse_visuals(); pg.slicers_filters=self.f_slicers.text().strip()
        pg.notes=self.f_notes.text().strip()
        fns = self.screenshots.get_filenames()
        pg.screenshot_path = fns[0] if fns else ""
        return pg
    def load_to_form(self, pg):
        self.f_name.setText(pg.page_name); self.f_purpose.setText(pg.purpose)
        lines = [f"{v.name} | {v.description}" if v.description else v.name for v in pg.visuals]
        self.f_vis.setPlainText("\n".join(lines))
        self.f_slicers.setText(pg.slicers_filters); self.f_notes.setText(pg.notes)
        if pg.screenshot_path:
            self.screenshots.load_filenames([pg.screenshot_path])


class GovernancePage(FormPage):
    def __init__(self, p=None):
        super().__init__(p)
        self.add_title("Governance")
        self.add_subtitle("Aktualisierung, RLS, Performance, Annahmen & Einschraenkungen")
        grp = QGroupBox("Details"); form = QFormLayout(grp)
        self.f_ref = QTextEdit(); self.f_ref.setMaximumHeight(80)
        self.f_mon = QTextEdit(); self.f_mon.setMaximumHeight(60)
        self.f_rls = QTextEdit(); self.f_rls.setMaximumHeight(80)
        self.f_perf = QTextEdit(); self.f_perf.setMaximumHeight(60)
        self.f_assum = QTextEdit(); self.f_assum.setMaximumHeight(80)
        self.f_lim = QTextEdit(); self.f_lim.setMaximumHeight(80)
        form.addRow("Aktualisierungsplan:", self.f_ref); form.addRow("Monitoring:", self.f_mon)
        form.addRow("RLS-Hinweise:", self.f_rls); form.addRow("Performance:", self.f_perf)
        form.addRow("Annahmen:", self.f_assum); form.addRow("Einschraenkungen:", self.f_lim)
        self._layout.addWidget(grp); self._layout.addStretch()
    def load(self, g):
        self.f_ref.setPlainText(g.refresh_schedule); self.f_mon.setPlainText(g.monitoring_notes)
        self.f_rls.setPlainText(g.rls_notes); self.f_perf.setPlainText(g.performance_notes)
        self.f_assum.setPlainText(g.assumptions); self.f_lim.setPlainText(g.limitations)
    def save(self, g):
        g.refresh_schedule=self.f_ref.toPlainText().strip(); g.monitoring_notes=self.f_mon.toPlainText().strip()
        g.rls_notes=self.f_rls.toPlainText().strip(); g.performance_notes=self.f_perf.toPlainText().strip()
        g.assumptions=self.f_assum.toPlainText().strip(); g.limitations=self.f_lim.toPlainText().strip()


class ChangeLogPage(ListEditorPage):
    def __init__(self, p=None):
        super().__init__("Aenderungsprotokoll", "Versionsverlauf",
                         ["Version", "Datum", "Beschreibung", "Autor", "Auswirkung"], p)
    def _build_form(self, form):
        self.f_ver = QLineEdit(); self.f_date = QLineEdit()
        self.f_date.setPlaceholderText("YYYY-MM-DD")
        self.f_desc = QLineEdit(); self.f_author = QLineEdit()
        self.f_impact = QComboBox(); self.f_impact.addItems(["minor","major","breaking"])
        self.f_ticket = QLineEdit()
        form.addRow("Version *:", self.f_ver); form.addRow("Datum:", self.f_date)
        form.addRow("Beschreibung *:", self.f_desc); form.addRow("Autor:", self.f_author)
        form.addRow("Auswirkung:", self.f_impact); form.addRow("Ticket:", self.f_ticket)
    def _validate(self):
        if not self.f_ver.text().strip(): return "Version ist erforderlich."
        if not self.f_desc.text().strip(): return "Beschreibung ist erforderlich."
        return None
    def _clear_form(self):
        for w in (self.f_ver,self.f_date,self.f_desc,self.f_author,self.f_ticket): w.clear()
        self.f_impact.setCurrentIndex(0)
    def _item_to_row(self, c): return [c.version, c.date, c.description, c.author, c.impact]
    def form_to_item(self, existing=None):
        c = existing or ChangeLogEntry()
        c.version=self.f_ver.text().strip(); c.date=self.f_date.text().strip() or _today()
        c.description=self.f_desc.text().strip(); c.author=self.f_author.text().strip()
        c.impact=self.f_impact.currentText(); c.ticket_link=self.f_ticket.text().strip()
        return c
    def load_to_form(self, c):
        self.f_ver.setText(c.version); self.f_date.setText(c.date)
        self.f_desc.setText(c.description); self.f_author.setText(c.author)
        idx=self.f_impact.findText(c.impact)
        if idx>=0: self.f_impact.setCurrentIndex(idx)
        self.f_ticket.setText(c.ticket_link)


# ══════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════

def _make_list_wiring(main_win, page, project_list_attr):
    """Generic wiring for ListEditorPage add/edit/delete to project model list."""
    def get_list(): return getattr(main_win.project, project_list_attr)

    def sync():
        rows = page.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row(); page._editing_row = idx
            lst = get_list()
            if idx < len(lst): page.load_to_form(lst[idx])

    def add():
        err = page._validate()
        if err: QMessageBox.warning(main_win, "Validierung", err); return
        item = page.form_to_item()
        get_list().append(item)
        page.load_items(get_list()); page._clear_form()
        main_win._toast(f"Hinzugefuegt")

    def apply():
        idx = page._editing_row; lst = get_list()
        if idx < 0 or idx >= len(lst):
            QMessageBox.information(main_win, "Hinweis", "Bitte Zeile auswaehlen."); return
        err = page._validate()
        if err: QMessageBox.warning(main_win, "Validierung", err); return
        page.form_to_item(lst[idx]); page.load_items(lst)
        main_win._toast("Aktualisiert")

    def delete():
        idx = page._editing_row; lst = get_list()
        if idx < 0 or idx >= len(lst):
            QMessageBox.information(main_win, "Hinweis", "Bitte Zeile auswaehlen."); return
        del lst[idx]; page.load_items(lst); page._editing_row = -1; page._clear_form()
        main_win._toast("Geloescht")

    page.table.itemSelectionChanged.connect(sync)
    page.btn_add.clicked.connect(add)
    page.btn_edit.clicked.connect(apply)
    page.btn_del.clicked.connect(delete)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Power BI Documentation Generator")
        self.setMinimumSize(1150, 780)
        self.resize(1350, 870)
        self.project = Project()
        self.project_path = DEFAULT_PROJECT_FILE

        central = QWidget(); self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0,0,0,0); main_lay.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.nav_clicked.connect(self._navigate)
        main_lay.addWidget(self.sidebar)

        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0,0,0,0); content_lay.setSpacing(0)

        # Toolbar
        tb = QWidget(); tb.setFixedHeight(54)
        tb.setStyleSheet(f"background: {BG_SURFACE}; border-bottom: 1px solid {BORDER};")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(18,8,18,8)

        self.btn_save = QPushButton("💾  Speichern"); self.btn_save.setObjectName("primary")
        self.btn_save.setCursor(Qt.PointingHandCursor); self.btn_save.clicked.connect(self._save)
        tbl.addWidget(self.btn_save)

        self.btn_md = QPushButton("📄  Markdown"); self.btn_md.setCursor(Qt.PointingHandCursor)
        self.btn_md.clicked.connect(self._gen_md); tbl.addWidget(self.btn_md)

        self.btn_pdf = QPushButton("📕  PDF-Report"); self.btn_pdf.setObjectName("accent")
        self.btn_pdf.setCursor(Qt.PointingHandCursor); self.btn_pdf.clicked.connect(self._gen_pdf)
        tbl.addWidget(self.btn_pdf)

        tbl.addStretch()
        self.toast_lbl = QLabel(""); self.toast_lbl.setStyleSheet(f"color:{SUCCESS}; font-size:12px;")
        tbl.addWidget(self.toast_lbl)
        content_lay.addWidget(tb)

        self.stack = QStackedWidget(); content_lay.addWidget(self.stack)
        main_lay.addWidget(content)

        # Create pages
        self.pg_dash = DashboardPage()
        self.pg_dash.btn_new.clicked.connect(self._new_project)
        self.pg_dash.btn_open.clicked.connect(self._open_file)
        self.pg_meta = MetadataPage()
        self.pg_ci = CIBrandingPage()
        self.pg_kpis = KPIPage()
        self.pg_ds = DataSourcePage()
        self.pg_pq = PowerQueryPage()
        self.pg_dm = DataModelPage()
        self.pg_measures = MeasuresPage()
        self.pg_pages = ReportPagesPage()
        self.pg_gov = GovernancePage()
        self.pg_cl = ChangeLogPage()
        self.pg_preview = PreviewPage()

        for pg in [self.pg_dash, self.pg_meta, self.pg_ci, self.pg_kpis, self.pg_ds,
                   self.pg_pq, self.pg_dm, self.pg_measures, self.pg_pages, self.pg_gov,
                   self.pg_cl, self.pg_preview]:
            self.stack.addWidget(pg)

        # Wire list editors
        _make_list_wiring(self, self.pg_kpis, "kpis")
        _make_list_wiring(self, self.pg_ds, "data_sources")
        _make_list_wiring(self, self.pg_pq, "power_queries")
        _make_list_wiring(self, self.pg_measures, "measures")
        _make_list_wiring(self, self.pg_pages, "report_pages")
        _make_list_wiring(self, self.pg_cl, "change_log")

        self.statusBar().showMessage("Bereit")
        self.sidebar.select(0)
        self._try_load()

    def _toast(self, msg, ms=3000):
        self.toast_lbl.setText(f"✅ {msg}")
        QTimer.singleShot(ms, lambda: self.toast_lbl.setText(""))

    def _navigate(self, idx):
        cur = self.stack.currentWidget()
        if cur == self.pg_meta: self.pg_meta.save(self.project.meta)
        if cur == self.pg_ci: self.pg_ci.save(self.project.ci_branding)
        if cur == self.pg_dm: self.pg_dm.save(self.project.data_model)
        if cur == self.pg_gov: self.pg_gov.save(self.project.governance)
        self.stack.setCurrentIndex(idx)
        if idx == 0: self.pg_dash.refresh(self.project, str(self.project_path))
        if idx == 11:  # Preview
            self._collect_all()
            self.pg_preview.set_project(self.project)

    def _collect_all(self):
        self.pg_meta.save(self.project.meta)
        self.pg_ci.save(self.project.ci_branding)
        self.pg_dm.save(self.project.data_model)
        self.pg_gov.save(self.project.governance)

    def _try_load(self):
        if project_exists():
            try:
                self.project = load_project()
                self._refresh_all()
                self.statusBar().showMessage(f"Projekt geladen: {DEFAULT_PROJECT_FILE}")
            except Exception as e:
                self.statusBar().showMessage(f"Fehler: {e}")
        self.pg_dash.refresh(self.project, str(self.project_path))

    def _refresh_all(self):
        self.pg_meta.load(self.project.meta)
        self.pg_ci.load(self.project.ci_branding)
        self.pg_kpis.load_items(self.project.kpis)
        self.pg_ds.load_items(self.project.data_sources)
        self.pg_pq.load_items(self.project.power_queries)
        self.pg_dm.load(self.project.data_model)
        self.pg_measures.load_items(self.project.measures)
        self.pg_pages.load_items(self.project.report_pages)
        self.pg_gov.load(self.project.governance)
        self.pg_cl.load_items(self.project.change_log)

    def _new_project(self):
        if self.project.meta.report_name:
            r = QMessageBox.question(self, "Neues Projekt", "Aktuelles Projekt verwerfen?",
                                      QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes: return
        self.project = Project(); self.project.meta.date = _today()
        self._refresh_all(); self.sidebar.select(1); self.stack.setCurrentIndex(1)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Projektdatei oeffnen", str(Path.cwd()),
                    "Projekte (*.yml *.yaml *.json);;Alle (*)")
        if path:
            try:
                self.project = load_project(Path(path))
                self.project_path = Path(path)
                self._refresh_all(); self.pg_dash.refresh(self.project, path)
                self.sidebar.select(0); self.stack.setCurrentIndex(0)
                self.statusBar().showMessage(f"Geladen: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _save(self):
        self._collect_all()
        err = self.pg_meta.validate()
        if err: QMessageBox.warning(self, "Validierung", err); return
        try:
            p = save_project(self.project, self.project_path)
            self.project_path = p
            self.statusBar().showMessage(f"Gespeichert: {p}")
            self._toast("Projekt gespeichert")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def _gen_md(self):
        self._save()
        try:
            out = generate_docs(self.project)
            QMessageBox.information(self, "Erfolg",
                f"Markdown generiert:\n{out.resolve()}\n\nOeffne docs/index.md als Einstiegspunkt.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def _gen_pdf(self):
        self._save()
        default = default_pdf_filename(self.project)
        path, _ = QFileDialog.getSaveFileName(self, "PDF speichern", str(Path.cwd() / default),
                    "PDF (*.pdf)")
        if not path: return
        prog = QProgressDialog("PDF wird generiert …", None, 0, 0, self)
        prog.setWindowTitle("PDF-Export"); prog.setWindowModality(Qt.WindowModal)
        prog.setMinimumDuration(0); prog.show(); QApplication.processEvents()
        try:
            result = generate_pdf(self.project, Path(path))
            prog.close()
            reply = QMessageBox.information(self, "PDF erstellt",
                f"PDF gespeichert:\n{result}\n\nOeffnen?",
                QMessageBox.Open | QMessageBox.Ok, QMessageBox.Ok)
            if reply == QMessageBox.Open:
                import subprocess
                if sys.platform == "win32": os.startfile(str(result))
                elif sys.platform == "darwin": subprocess.run(["open", str(result)])
                else: subprocess.run(["xdg-open", str(result)])
        except Exception as e:
            prog.close()
            QMessageBox.critical(self, "PDF-Fehler", f"{e}\n\n{traceback.format_exc()}")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_QSS)
    font = QFont(FONT_FAMILY, FONT_SIZE)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
