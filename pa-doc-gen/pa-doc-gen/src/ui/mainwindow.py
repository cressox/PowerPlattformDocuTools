"""
ui/mainwindow.py – Hauptfenster mit allen Seiten.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit,
    QComboBox, QSpinBox, QSplitter, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QProgressBar,
    QFormLayout, QGroupBox, QCheckBox, QHeaderView, QTableWidget,
    QTableWidgetItem, QApplication, QGridLayout, QTabWidget,
)

from models import (
    PAProject, FlowAction, FlowConnection, FlowVariable,
    ErrorHandling, DataMapping, FlowDependency, ChangeLogEntry,
    Screenshot, EnvironmentInfo,
    FlowType, FlowStatus, LicenseType, EnvironmentType,
    ConnectorTier, VariableType, Criticality, ChangeImpact, RunAfterStatus,
)
from storage import save_project, load_project
from generator import generate_docs
from pdf_export import export_pdf
from flow_parser import FlowParser, load_from_file, load_from_string, get_flow_stats
from diagram import generate_mermaid_markdown, generate_mermaid_diagram
from diagram_renderer import render_flowchart
from solution_parser import SolutionParser, parse_solution, get_solution_stats, SolutionInfo
from solution_generator import generate_solution_docs
from ui.theme import ACCENT, BG_CARD, BG_INPUT, BORDER, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, ERROR
from ui.widgets import (
    Sidebar, FormPage, Toast, CodeEditor, ScreenshotPanel,
    Card, StatCard,
)
from ui.preview import PreviewWidget


DATA_DIR = Path("data")
PROJECT_PATH = DATA_DIR / "project.yml"


# ===========================================================================
# Import-Dialog
# ===========================================================================

class ImportDialog(QDialog):
    """Dialog zum Importieren von Flow-JSON-Dateien."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flow-JSON importieren")
        self.setMinimumSize(700, 500)
        self.result_project: PAProject | None = None
        self._source_filename: str = ""

        layout = QVBoxLayout(self)

        # Info
        info = QLabel("Flow-JSON importieren: Datei waehlen, per Drag & Drop oder JSON einfuegen (Strg+V)")
        info.setWordWrap(True)
        layout.addWidget(info)

        # JSON-Eingabe
        self.json_editor = CodeEditor(language="json")
        self.json_editor.setPlaceholderText("JSON hier einfuegen oder Datei waehlen …")
        self.json_editor.setMinimumHeight(250)
        layout.addWidget(self.json_editor)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_file = QPushButton("Datei waehlen …")
        self.btn_file.setProperty("class", "secondary")
        self.btn_file.clicked.connect(self._browse_file)
        btn_row.addWidget(self.btn_file)

        self.btn_parse = QPushButton("Parsen und Vorschau")
        self.btn_parse.clicked.connect(self._parse)
        btn_row.addWidget(self.btn_parse)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Vorschau
        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 8px;")
        layout.addWidget(self.preview_label)

        # Optionen
        opts = QHBoxLayout()
        self.chk_overwrite = QCheckBox("Bestehende Daten ueberschreiben")
        self.chk_overwrite.setChecked(True)
        opts.addWidget(self.chk_overwrite)
        opts.addStretch()
        layout.addLayout(opts)

        # Dialog-Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Flow-JSON waehlen", "",
            "JSON / ZIP Dateien (*.json *.zip);;Alle Dateien (*)"
        )
        if path:
            try:
                self._source_filename = Path(path).stem
                data = load_from_file(path)
                self.json_editor.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
                self._parse()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Datei konnte nicht gelesen werden:\n{e}")

    def _parse(self):
        text = self.json_editor.toPlainText().strip()
        if not text:
            self.preview_label.setText("Kein JSON eingegeben.")
            return
        try:
            data = json.loads(text)
            parser = FlowParser()
            project = parser.parse(data)
            # Flow-Name aus Dateiname ableiten, falls leer
            if not project.meta.flow_name and self._source_filename:
                project.meta.flow_name = self._source_filename
            self.result_project = project

            stats = get_flow_stats(project)
            info_lines = [
                f"✅ Flow erkannt: {project.meta.flow_name or '(kein Name)'}",
                f"   Trigger: {stats['trigger_type'] or '(keiner)'}",
                f"   Aktionen: {stats['total_actions']} ({stats['top_level_actions']} Top-Level)",
                f"   Konnektoren: {stats['connectors']}",
                f"   Variablen: {stats['variables']}",
            ]
            if stats['connector_names']:
                info_lines.append(f"   Connectors: {', '.join(stats['connector_names'])}")

            self.preview_label.setText("\n".join(info_lines))
            self.preview_label.setStyleSheet(f"color: {SUCCESS}; padding: 8px; font-family: monospace;")
        except json.JSONDecodeError as e:
            self.preview_label.setText(f"❌ JSON-Fehler: {e}")
            self.preview_label.setStyleSheet(f"color: {ERROR}; padding: 8px;")
        except Exception as e:
            self.preview_label.setText(f"❌ Parse-Fehler: {e}")
            self.preview_label.setStyleSheet(f"color: {ERROR}; padding: 8px;")

    def _accept(self):
        if self.result_project is None:
            self._parse()
        if self.result_project is not None:
            self.accept()


# ===========================================================================
# Solution-Import-Dialog
# ===========================================================================

class SolutionImportDialog(QDialog):
    """Dialog zum Importieren einer gesamten Power Platform Solution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Solution importieren")
        self.setMinimumSize(750, 550)
        self.result_solution: SolutionInfo | None = None

        layout = QVBoxLayout(self)

        # Info
        info = QLabel(
            "Power Platform Solution importieren (.zip).\n"
            "Alle Entitaeten werden erkannt: Flows, Canvas Apps, Custom Connectors, "
            "Connection References, Environment Variables, Dataverse Tables, "
            "Security Roles, Web Resources, Plugins und mehr."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Datei-Auswahl
        file_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Solution-ZIP-Datei waehlen …")
        self.path_edit.setReadOnly(True)
        file_row.addWidget(self.path_edit)

        btn_browse = QPushButton("Durchsuchen …")
        btn_browse.clicked.connect(self._browse_file)
        file_row.addWidget(btn_browse)
        layout.addLayout(file_row)

        # Parse-Button
        self.btn_parse = QPushButton("Solution analysieren")
        self.btn_parse.clicked.connect(self._parse)
        layout.addWidget(self.btn_parse)

        # Ergebnis-Ansicht
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["Komponente", "Typ", "Details"])
        self.result_tree.setColumnWidth(0, 250)
        self.result_tree.setColumnWidth(1, 150)
        self.result_tree.setAlternatingRowColors(True)
        layout.addWidget(self.result_tree)

        # Status
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 8px;")
        layout.addWidget(self.status_label)

        # Dialog-Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Solution-ZIP waehlen", "",
            "ZIP Dateien (*.zip);;Alle Dateien (*)"
        )
        if path:
            self.path_edit.setText(path)
            self._parse()

    def _parse(self):
        path = self.path_edit.text().strip()
        if not path:
            self.status_label.setText("Keine Datei ausgewaehlt.")
            return

        try:
            solution = parse_solution(path)
            self.result_solution = solution
            stats = get_solution_stats(solution)

            # Ergebnis-Baum fuellen
            self.result_tree.clear()

            def _add_group(name: str, entities: list, icon: str = ""):
                if not entities:
                    return
                parent = QTreeWidgetItem()
                parent.setText(0, f"{icon} {name}" if icon else name)
                parent.setText(1, f"({len(entities)})")
                self.result_tree.addTopLevelItem(parent)
                for e in entities:
                    child = QTreeWidgetItem()
                    child.setText(0, e.display_name or e.name)
                    child.setText(1, e.entity_type)
                    child.setText(2, e.description or "")
                    parent.addChild(child)
                parent.setExpanded(True)

            _add_group("Cloud Flows", solution.flows, "⚡")
            _add_group("Canvas Apps", solution.canvas_apps, "📱")
            _add_group("Model-Driven Apps", solution.model_apps, "🏢")
            _add_group("Custom Connectors", solution.custom_connectors, "🔌")
            _add_group("Connection References", solution.connection_references, "🔗")
            _add_group("Environment Variables", solution.env_variables, "⚙️")
            _add_group("Dataverse Tables", solution.tables, "🗄️")
            _add_group("Security Roles", solution.security_roles, "🛡️")
            _add_group("Web Resources", solution.web_resources, "🌐")
            _add_group("Plugins", solution.plugins, "🧩")
            _add_group("Workflows", solution.processes, "🔄")
            _add_group("Sonstige", solution.other_components, "📦")

            info_lines = [
                f"✅ Solution erkannt: {solution.display_name or solution.unique_name or '(unbekannt)'}",
                f"   Version: {solution.version}",
                f"   Publisher: {solution.publisher_name}",
                f"   Gesamt-Komponenten: {stats['total_components']}",
                f"   Flows: {stats['flows']}  |  Canvas Apps: {stats['canvas_apps']}",
                f"   Connectors: {stats['custom_connectors']}  |  Tables: {stats['tables']}",
                f"   Env Variables: {stats['env_variables']}",
            ]
            self.status_label.setText("\n".join(info_lines))
            self.status_label.setStyleSheet(f"color: {SUCCESS}; padding: 8px; font-family: monospace;")

        except Exception as e:
            self.status_label.setText(f"❌ Fehler: {e}")
            self.status_label.setStyleSheet(f"color: {ERROR}; padding: 8px;")

    def _accept(self):
        if self.result_solution is None:
            self._parse()
        if self.result_solution is not None:
            self.accept()


# ===========================================================================
# Seiten-Erstellung
# ===========================================================================

def _make_line(text: str = "", placeholder: str = "") -> QLineEdit:
    le = QLineEdit(text)
    if placeholder:
        le.setPlaceholderText(placeholder)
    return le


def _make_combo(items: list[str], current: str = "") -> QComboBox:
    cb = QComboBox()
    cb.addItems(items)
    if current and current in items:
        cb.setCurrentText(current)
    return cb


def _make_text(text: str = "", placeholder: str = "", height: int = 80) -> QTextEdit:
    te = QTextEdit()
    te.setPlainText(text)
    te.setPlaceholderText(placeholder)
    te.setMaximumHeight(height)
    return te


# ===========================================================================
# MainWindow
# ===========================================================================

class MainWindow(QMainWindow):
    """Hauptfenster des PA Documentation Generators."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Power Automate Documentation Generator")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.project = PAProject()
        self._unsaved = False
        self._current_solution: SolutionInfo | None = None
        # Solution-Modus: alle Flow-Projekte gespeichert
        self._solution_flows: dict[str, PAProject] = {}  # name -> PAProject
        self._current_flow_name: str = ""

        self._build_ui()
        self._load_existing()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.sidebar)

        # Stacked Widget
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Toast
        self.toast = Toast(self.stack)

        # Pages
        self._build_dashboard()       # 0
        self._build_solution_page()   # 1
        self._build_meta_page()       # 2
        self._build_branding_page()   # 3
        self._build_trigger_page()    # 4
        self._build_flowchart_page()  # 5
        self._build_actions_page()    # 6
        self._build_connectors_page() # 7
        self._build_variables_page()  # 8
        self._build_error_page()      # 9
        self._build_mappings_page()   # 10
        self._build_sla_page()        # 11
        self._build_governance_page() # 12
        self._build_dependencies_page() # 13
        self._build_changelog_page()  # 14
        self._build_preview_page()    # 15

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self._save)
        QShortcut(QKeySequence("Ctrl+I"), self, self._import_flow)

    def _on_page_changed(self, idx: int):
        self.stack.setCurrentIndex(idx)
        if idx == 1:   # Solution
            self._refresh_solution_page()
        if idx == 5:   # Flussdiagramm
            self._refresh_flowchart()
        if idx == 15:  # Vorschau
            self._refresh_preview()

    # -------------------------------------------------------------------
    # 0. Dashboard
    # -------------------------------------------------------------------
    def _build_dashboard(self):
        page = FormPage("Dashboard")

        # Buttons
        btn_row = QHBoxLayout()
        btn_new = QPushButton("Neues Projekt")
        btn_new.clicked.connect(self._new_project)
        btn_row.addWidget(btn_new)

        btn_open = QPushButton("Projekt oeffnen …")
        btn_open.setProperty("class", "secondary")
        btn_open.clicked.connect(self._open_project)
        btn_row.addWidget(btn_open)

        btn_import = QPushButton("Flow-JSON importieren …")
        btn_import.clicked.connect(self._import_flow)
        btn_row.addWidget(btn_import)

        btn_solution = QPushButton("Solution importieren …")
        btn_solution.setProperty("class", "secondary")
        btn_solution.clicked.connect(self._import_solution)
        btn_row.addWidget(btn_solution)

        btn_save = QPushButton("Speichern (Strg+S)")
        btn_save.setProperty("class", "secondary")
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()

        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_separator()

        # Statistik-Cards
        stats_row = QHBoxLayout()
        self.stat_actions = StatCard("Aktionen", "0")
        self.stat_connectors = StatCard("Konnektoren", "0", WARNING)
        self.stat_variables = StatCard("Variablen", "0", SUCCESS)
        self.stat_errors = StatCard("Fehlerbehandlung", "0", ERROR)
        stats_row.addWidget(self.stat_actions)
        stats_row.addWidget(self.stat_connectors)
        stats_row.addWidget(self.stat_variables)
        stats_row.addWidget(self.stat_errors)
        stats_row.addStretch()
        w2 = QWidget()
        w2.setLayout(stats_row)
        page.add_widget(w2)

        # Flow-Info
        self.dash_info = QLabel("Kein Projekt geladen.")
        self.dash_info.setWordWrap(True)
        self.dash_info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; padding: 8px;")
        page.add_widget(self.dash_info)

        # Export-Buttons
        page.add_separator()
        exp_row = QHBoxLayout()
        btn_md = QPushButton("Markdown generieren")
        btn_md.clicked.connect(self._generate_markdown)
        exp_row.addWidget(btn_md)
        btn_pdf = QPushButton("PDF exportieren")
        btn_pdf.clicked.connect(self._export_pdf)
        exp_row.addWidget(btn_pdf)
        btn_sol_md = QPushButton("Solution-Doku generieren")
        btn_sol_md.setProperty("class", "secondary")
        btn_sol_md.clicked.connect(self._generate_solution_markdown)
        exp_row.addWidget(btn_sol_md)
        exp_row.addStretch()
        w3 = QWidget()
        w3.setLayout(exp_row)
        page.add_widget(w3)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 1. Solution-Uebersicht
    # -------------------------------------------------------------------
    def _build_solution_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setContentsMargins(24, 20, 24, 20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Solution-Uebersicht")
        title.setProperty("class", "section-title")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_import_sol = QPushButton("Solution importieren …")
        btn_import_sol.clicked.connect(self._import_solution)
        hdr.addWidget(btn_import_sol)
        layout.addLayout(hdr)

        # Solution-Info
        self.sol_info = QLabel("Keine Solution geladen. Importieren Sie eine Solution-ZIP-Datei.")
        self.sol_info.setWordWrap(True)
        self.sol_info.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 8px; font-size: 12px;")
        layout.addWidget(self.sol_info)

        # Flow-Auswahl
        flow_group = QGroupBox("Flow-Auswahl")
        flow_group.setStyleSheet(f"QGroupBox {{ color: {ACCENT}; font-weight: bold; border: 1px solid {BORDER}; border-radius: 6px; margin-top: 12px; padding-top: 16px; }}")
        flow_layout = QVBoxLayout(flow_group)

        flow_sel_row = QHBoxLayout()
        flow_sel_row.addWidget(QLabel("Aktiver Flow:"))
        self.sol_flow_combo = QComboBox()
        self.sol_flow_combo.setMinimumWidth(350)
        self.sol_flow_combo.currentIndexChanged.connect(self._on_flow_selected)
        flow_sel_row.addWidget(self.sol_flow_combo)
        flow_sel_row.addStretch()
        flow_layout.addLayout(flow_sel_row)

        self.sol_flow_info = QLabel("")
        self.sol_flow_info.setWordWrap(True)
        self.sol_flow_info.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 4px;")
        flow_layout.addWidget(self.sol_flow_info)

        layout.addWidget(flow_group)

        # Komponenten-Baum
        comp_group = QGroupBox("Alle Komponenten")
        comp_group.setStyleSheet(f"QGroupBox {{ color: {ACCENT}; font-weight: bold; border: 1px solid {BORDER}; border-radius: 6px; margin-top: 12px; padding-top: 16px; }}")
        comp_layout = QVBoxLayout(comp_group)

        self.sol_tree = QTreeWidget()
        self.sol_tree.setHeaderLabels(["Komponente", "Typ", "Details"])
        self.sol_tree.setColumnWidth(0, 300)
        self.sol_tree.setColumnWidth(1, 160)
        self.sol_tree.setAlternatingRowColors(True)
        self.sol_tree.setMinimumHeight(300)
        self.sol_tree.itemDoubleClicked.connect(self._on_solution_item_dblclick)
        comp_layout.addWidget(self.sol_tree)

        layout.addWidget(comp_group)

        # Stats-Karten
        stats_row = QHBoxLayout()
        self.sol_stat_flows = StatCard("Flows", "0")
        self.sol_stat_apps = StatCard("Canvas Apps", "0", WARNING)
        self.sol_stat_connectors = StatCard("Connectors", "0", SUCCESS)
        self.sol_stat_tables = StatCard("Tables", "0", ACCENT)
        self.sol_stat_vars = StatCard("Env Variables", "0", ERROR)
        stats_row.addWidget(self.sol_stat_flows)
        stats_row.addWidget(self.sol_stat_apps)
        stats_row.addWidget(self.sol_stat_connectors)
        stats_row.addWidget(self.sol_stat_tables)
        stats_row.addWidget(self.sol_stat_vars)
        stats_row.addStretch()
        w = QWidget()
        w.setLayout(stats_row)
        layout.addWidget(w)

        layout.addStretch()
        self.stack.addWidget(page_widget)

    def _refresh_solution_page(self):
        """Aktualisiert die Solution-Seite."""
        sol = self._current_solution
        if sol is None:
            self.sol_info.setText("Keine Solution geladen. Importieren Sie eine Solution-ZIP-Datei.")
            self.sol_tree.clear()
            self.sol_flow_combo.clear()
            return

        stats = get_solution_stats(sol)
        self.sol_info.setText(
            f"<b>{sol.display_name or sol.unique_name}</b><br>"
            f"Version: {sol.version}  |  Publisher: {sol.publisher_name}  |  "
            f"{'Managed' if sol.managed else 'Unmanaged'}  |  "
            f"{stats['total_components']} Komponenten"
        )

        # Stats
        self.sol_stat_flows.set_value(stats["flows"])
        self.sol_stat_apps.set_value(stats["canvas_apps"])
        self.sol_stat_connectors.set_value(stats["custom_connectors"])
        self.sol_stat_tables.set_value(stats["tables"])
        self.sol_stat_vars.set_value(stats["env_variables"])

        # Komponenten-Baum
        self.sol_tree.clear()

        def _add_group(name: str, entities: list, icon: str = ""):
            if not entities:
                return
            parent = QTreeWidgetItem()
            parent.setText(0, f"{icon} {name}" if icon else name)
            parent.setText(1, f"({len(entities)})")
            self.sol_tree.addTopLevelItem(parent)
            for e in entities:
                child = QTreeWidgetItem()
                child.setText(0, e.display_name or e.name)
                child.setText(1, e.entity_type)
                desc = e.description or ""
                if e.details:
                    details_parts = []
                    for k, v in e.details.items():
                        if v:
                            details_parts.append(f"{k}: {v}")
                    if details_parts:
                        desc = " | ".join(details_parts[:3])
                child.setText(2, desc)
                child.setData(0, Qt.UserRole, e)
                parent.addChild(child)
            parent.setExpanded(True)

        _add_group("Cloud Flows", sol.flows, "⚡")
        _add_group("Canvas Apps", sol.canvas_apps, "📱")
        _add_group("Model-Driven Apps", sol.model_apps, "🏢")
        _add_group("Custom Connectors", sol.custom_connectors, "🔌")
        _add_group("Connection References", sol.connection_references, "🔗")
        _add_group("Environment Variables", sol.env_variables, "⚙️")
        _add_group("Dataverse Tables", sol.tables, "🗄️")
        _add_group("Security Roles", sol.security_roles, "🛡️")
        _add_group("Web Resources", sol.web_resources, "🌐")
        _add_group("Plugins", sol.plugins, "🧩")
        _add_group("Workflows", sol.processes, "🔄")
        _add_group("Sonstige", sol.other_components, "📦")

    def _on_solution_item_dblclick(self, item: QTreeWidgetItem, column: int):
        """Doppelklick auf eine Komponente im Solution-Baum."""
        entity = item.data(0, Qt.UserRole)
        if entity is None:
            return
        from solution_parser import SolutionEntity, SolutionComponentType
        if isinstance(entity, SolutionEntity):
            if entity.entity_type == SolutionComponentType.FLOW.value and entity.flow_project:
                # Flow laden
                self._switch_to_flow(entity.display_name or entity.name)
                self.sidebar.select_page(2)  # Metadaten-Seite
                self._on_page_changed(2)

    def _on_flow_selected(self, index: int):
        """Wird aufgerufen wenn ein anderer Flow im Combo ausgewaehlt wird."""
        if index < 0:
            return
        flow_name = self.sol_flow_combo.currentText()
        if flow_name and flow_name != self._current_flow_name:
            self._switch_to_flow(flow_name)

    def _switch_to_flow(self, flow_name: str):
        """Wechselt zum ausgewaehlten Flow und laedt dessen Daten."""
        # Aktuellen Flow speichern
        if self._current_flow_name and self._current_flow_name in self._solution_flows:
            self._collect_project()
            self._solution_flows[self._current_flow_name] = self.project

        # Neuen Flow laden
        if flow_name in self._solution_flows:
            self.project = self._solution_flows[flow_name]
            self._current_flow_name = flow_name
            self._populate_gui()
            self.setWindowTitle(f"PA Doc Gen – {flow_name}")

            # Combo aktualisieren ohne Signal
            self.sol_flow_combo.blockSignals(True)
            idx = self.sol_flow_combo.findText(flow_name)
            if idx >= 0:
                self.sol_flow_combo.setCurrentIndex(idx)
            self.sol_flow_combo.blockSignals(False)

            # Info
            stats = get_flow_stats(self.project)
            self.sol_flow_info.setText(
                f"Aktiver Flow: <b>{flow_name}</b>  |  "
                f"Aktionen: {stats['total_actions']}  |  "
                f"Trigger: {stats['trigger_type'] or '–'}  |  "
                f"Konnektoren: {stats['connectors']}"
            )

            self.toast.show_message(f"Flow gewechselt: {flow_name}")

    # -------------------------------------------------------------------
    # 2. Metadaten
    # -------------------------------------------------------------------
    def _build_meta_page(self):
        page = FormPage("Metadaten")
        self.meta_name = page.add_form_row("Flow-Name:", _make_line(placeholder="Name des Flows"))
        self.meta_desc = page.add_form_row("Beschreibung:", _make_text(placeholder="Was macht dieser Flow?"))
        self.meta_type = page.add_form_row("Typ:", _make_combo([e.value for e in FlowType]))
        self.meta_status = page.add_form_row("Status:", _make_combo([e.value for e in FlowStatus]))
        self.meta_owner = page.add_form_row("Eigentuemer:", _make_line())
        self.meta_author = page.add_form_row("Autor:", _make_line())
        self.meta_created = page.add_form_row("Erstellt:", _make_line(placeholder="YYYY-MM-DD"))
        self.meta_modified = page.add_form_row("Letzte Aenderung:", _make_line(placeholder="YYYY-MM-DD"))
        self.meta_solution = page.add_form_row("Solution-Name:", _make_line())
        self.meta_license = page.add_form_row("Lizenz:", _make_combo([e.value for e in LicenseType]))
        self.meta_services = page.add_form_row("Verbundene Dienste:", _make_text(placeholder="SharePoint, Teams, …", height=50))

        page.add_separator()
        # Umgebungen
        grp = page.add_group("Umgebungen")
        self.env_table = QTableWidget(0, 2)
        self.env_table.setHorizontalHeaderLabels(["Umgebung", "URL"])
        self.env_table.horizontalHeader().setStretchLastSection(True)
        self.env_table.setMaximumHeight(140)
        grp.addWidget(self.env_table)
        env_btns = QHBoxLayout()
        btn_add_env = QPushButton("+ Umgebung")
        btn_add_env.clicked.connect(lambda: self._add_table_row(self.env_table, ["Dev", ""]))
        env_btns.addWidget(btn_add_env)
        btn_del_env = QPushButton("- Entfernen")
        btn_del_env.setProperty("class", "danger")
        btn_del_env.clicked.connect(lambda: self._del_table_row(self.env_table))
        env_btns.addWidget(btn_del_env)
        env_btns.addStretch()
        grp.addLayout(env_btns)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 2. CI / Branding
    # -------------------------------------------------------------------
    def _build_branding_page(self):
        page = FormPage("CI / Branding")
        self.brand_company = page.add_form_row("Firmenname:", _make_line())
        self.brand_logo = page.add_form_row("Logo-Pfad:", _make_line(placeholder="Pfad zum Logo"))

        btn_logo = QPushButton("Logo waehlen …")
        btn_logo.setProperty("class", "secondary")
        btn_logo.clicked.connect(self._choose_logo)
        page.add_widget(btn_logo)

        self.brand_primary = page.add_form_row("Primaerfarbe:", _make_line("#5B8DEF"))
        self.brand_accent = page.add_form_row("Akzentfarbe:", _make_line("#E0A526"))
        self.brand_secondary = page.add_form_row("Sekundaerfarbe:", _make_line("#1A1D28"))
        self.brand_header = page.add_form_row("Header-Text:", _make_line())
        self.brand_footer = page.add_form_row("Footer-Text:", _make_line())
        self.brand_conf = page.add_form_row("Vertraulichkeit:", _make_text(placeholder="Vertraulichkeitsvermerk", height=50))

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 3. Trigger
    # -------------------------------------------------------------------
    def _build_trigger_page(self):
        page = FormPage("Trigger")
        self.trig_name = page.add_form_row("Name:", _make_line())
        self.trig_type = page.add_form_row("Trigger-Typ:", _make_line(placeholder="Recurrence, HTTP, SharePoint …"))
        self.trig_connector = page.add_form_row("Connector:", _make_line())
        self.trig_desc = page.add_form_row("Beschreibung:", _make_text(height=60))
        self.trig_freq = page.add_form_row("Frequenz:", _make_line())
        self.trig_interval = page.add_form_row("Intervall:", _make_line())
        self.trig_tz = page.add_form_row("Zeitzone:", _make_line())
        self.trig_auth = page.add_form_row("Authentifizierung:", _make_line(placeholder="Service Account, Managed Identity …"))

        page.add_separator()
        lbl = QLabel("Filter-Ausdruck:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        page.add_widget(lbl)
        self.trig_filter = CodeEditor(language="expression")
        self.trig_filter.setMaximumHeight(80)
        page.add_widget(self.trig_filter)

        lbl2 = QLabel("Input-Schema (JSON):")
        lbl2.setStyleSheet(f"color: {TEXT_SECONDARY};")
        page.add_widget(lbl2)
        self.trig_schema = CodeEditor(language="json")
        self.trig_schema.setMaximumHeight(150)
        page.add_widget(self.trig_schema)

        page.add_separator()
        self.trig_screenshot = ScreenshotPanel("trigger")
        page.add_widget(self.trig_screenshot)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 4. Flussdiagramm
    # -------------------------------------------------------------------
    def _build_flowchart_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setContentsMargins(24, 20, 24, 20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Flussdiagramm")
        title.setProperty("class", "section-title")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_refresh = QPushButton("Aktualisieren")
        btn_refresh.clicked.connect(self._refresh_flowchart)
        hdr.addWidget(btn_refresh)

        btn_copy = QPushButton("Mermaid kopieren")
        btn_copy.setProperty("class", "secondary")
        btn_copy.clicked.connect(self._copy_mermaid)
        hdr.addWidget(btn_copy)
        layout.addLayout(hdr)

        # Info
        info = QLabel(
            "Visuelle Darstellung des Flows als Flussdiagramm (Mermaid-Syntax). "
            "Das Diagramm wird automatisch aus den importierten Aktionen generiert."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 4px 0 8px 0;")
        layout.addWidget(info)

        # Tabs: Bild-Vorschau + Mermaid-Code
        tabs = QTabWidget()

        # Bild-Vorschau (gerendertes Diagramm)
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #13151E;")
        self.flowchart_image = QLabel()
        self.flowchart_image.setAlignment(Qt.AlignCenter)
        self.flowchart_image.setStyleSheet("background-color: #13151E; padding: 8px;")
        scroll.setWidget(self.flowchart_image)
        tabs.addTab(scroll, "Diagramm-Vorschau")

        # Mermaid-Code
        self.flowchart_code = QPlainTextEdit()
        self.flowchart_code.setReadOnly(True)
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.flowchart_code.setFont(font)
        tabs.addTab(self.flowchart_code, "Mermaid-Code")

        layout.addWidget(tabs)
        self.stack.addWidget(page_widget)

    def _refresh_flowchart(self):
        """Aktualisiert das Flussdiagramm basierend auf aktuellen Aktionen."""
        self._collect_project()
        try:
            mermaid_code = generate_mermaid_diagram(self.project)
            self.flowchart_code.setPlainText(mermaid_code)

            # Visuelles Diagramm rendern
            pixmap = render_flowchart(self.project, scale=1.5)
            self.flowchart_image.setPixmap(pixmap)
            self.flowchart_image.adjustSize()
        except Exception as e:
            self.flowchart_code.setPlainText(f"Fehler: {e}")
            self.flowchart_image.setText(f"Render-Fehler: {e}")

    def _copy_mermaid(self):
        """Kopiert den Mermaid-Code in die Zwischenablage."""
        code = self.flowchart_code.toPlainText()
        if code:
            QApplication.clipboard().setText(code)
            self.toast.show_message("Mermaid-Code kopiert ✓")
        else:
            self.toast.show_message("Kein Diagramm vorhanden", "warning")

    # -------------------------------------------------------------------
    # 5. Aktionen (Baumansicht + Detail-Editor)
    # -------------------------------------------------------------------
    def _build_actions_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Aktionen")
        title.setProperty("class", "section-title")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold; padding: 12px;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_add = QPushButton("+ Aktion")
        btn_add.clicked.connect(self._add_action)
        hdr.addWidget(btn_add)

        btn_add_child = QPushButton("+ Kind-Aktion")
        btn_add_child.setProperty("class", "secondary")
        btn_add_child.clicked.connect(self._add_child_action)
        hdr.addWidget(btn_add_child)

        btn_del = QPushButton("Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(self._del_action)
        hdr.addWidget(btn_del)

        layout.addLayout(hdr)

        # Splitter: Baum links, Detail rechts
        splitter = QSplitter(Qt.Horizontal)

        # Tree
        self.action_tree = QTreeWidget()
        self.action_tree.setHeaderLabels(["Aktion", "Typ", "Connector"])
        self.action_tree.setColumnWidth(0, 250)
        self.action_tree.setColumnWidth(1, 120)
        self.action_tree.setAlternatingRowColors(True)
        self.action_tree.setDragDropMode(QTreeWidget.InternalMove)
        self.action_tree.currentItemChanged.connect(self._on_action_selected)
        splitter.addWidget(self.action_tree)

        # Detail-Panel
        detail = QWidget()
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(12, 8, 12, 8)

        detail_title = QLabel("Aktions-Details")
        detail_title.setStyleSheet(f"color: {ACCENT}; font-weight: bold; font-size: 14px;")
        dl.addWidget(detail_title)

        form = QFormLayout()
        self.act_name = QLineEdit()
        form.addRow("Name:", self.act_name)
        self.act_type = QLineEdit()
        form.addRow("Typ:", self.act_type)
        self.act_connector = QLineEdit()
        form.addRow("Connector:", self.act_connector)
        self.act_desc = QTextEdit()
        self.act_desc.setMaximumHeight(60)
        form.addRow("Beschreibung:", self.act_desc)
        self.act_config = QTextEdit()
        self.act_config.setMaximumHeight(60)
        form.addRow("Konfiguration:", self.act_config)
        self.act_inputs = QLineEdit()
        form.addRow("Inputs:", self.act_inputs)
        self.act_outputs = QLineEdit()
        form.addRow("Outputs:", self.act_outputs)
        dl.addLayout(form)

        lbl = QLabel("Expression:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        dl.addWidget(lbl)
        self.act_expr = CodeEditor(language="expression")
        self.act_expr.setMaximumHeight(80)
        dl.addWidget(self.act_expr)

        # Run After
        ra_lbl = QLabel("Run After:")
        ra_lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        dl.addWidget(ra_lbl)
        ra_row = QHBoxLayout()
        self.act_ra_success = QCheckBox("Succeeded")
        self.act_ra_failed = QCheckBox("Failed")
        self.act_ra_skipped = QCheckBox("Skipped")
        self.act_ra_timeout = QCheckBox("Timed Out")
        ra_row.addWidget(self.act_ra_success)
        ra_row.addWidget(self.act_ra_failed)
        ra_row.addWidget(self.act_ra_skipped)
        ra_row.addWidget(self.act_ra_timeout)
        ra_row.addStretch()
        dl.addLayout(ra_row)

        btn_apply = QPushButton("Aenderungen uebernehmen")
        btn_apply.clicked.connect(self._apply_action_changes)
        dl.addWidget(btn_apply)

        dl.addStretch()
        splitter.addWidget(detail)
        splitter.setSizes([450, 550])

        layout.addWidget(splitter)
        self.stack.addWidget(page_widget)

    # -------------------------------------------------------------------
    # 5. Konnektoren
    # -------------------------------------------------------------------
    def _build_connectors_page(self):
        page = FormPage("Konnektoren & Verbindungen")
        self.conn_table = QTableWidget(0, 7)
        self.conn_table.setHorizontalHeaderLabels([
            "Connector", "Typ", "Verbindung", "Auth-Typ",
            "Service-Account", "Berechtigungen", "Gateway"
        ])
        self.conn_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.conn_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Konnektor")
        btn_add.clicked.connect(lambda: self._add_table_row(self.conn_table, ["", "Standard", "", "", "", "", ""]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.conn_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 6. Variablen
    # -------------------------------------------------------------------
    def _build_variables_page(self):
        page = FormPage("Variablen")
        self.var_table = QTableWidget(0, 6)
        self.var_table.setHorizontalHeaderLabels([
            "Name", "Typ", "Initialwert", "Beschreibung", "Gesetzt in", "Verwendet in"
        ])
        self.var_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.var_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Variable")
        btn_add.clicked.connect(lambda: self._add_table_row(self.var_table, ["", "String", "", "", "", ""]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.var_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 7. Fehlerbehandlung
    # -------------------------------------------------------------------
    def _build_error_page(self):
        page = FormPage("Fehlerbehandlung & Retry-Logik")
        self.err_table = QTableWidget(0, 8)
        self.err_table.setHorizontalHeaderLabels([
            "Scope", "Pattern", "Run After", "Retry-Anzahl",
            "Retry-Intervall", "Retry-Typ", "Benachrichtigung", "Timeout"
        ])
        self.err_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.err_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Fehlerbehandlung")
        btn_add.clicked.connect(lambda: self._add_table_row(self.err_table, ["", "", "", "0", "", "", "", ""]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.err_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 8. Datenmappings
    # -------------------------------------------------------------------
    def _build_mappings_page(self):
        page = FormPage("Datenmappings")
        self.map_table = QTableWidget(0, 5)
        self.map_table.setHorizontalHeaderLabels([
            "Quell-Aktion", "Ziel-Aktion", "Feldmapping", "Transformation", "Beschreibung"
        ])
        self.map_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.map_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Mapping")
        btn_add.clicked.connect(lambda: self._add_table_row(self.map_table, ["", "", "", "", ""]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.map_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 9. SLA & Performance
    # -------------------------------------------------------------------
    def _build_sla_page(self):
        page = FormPage("SLA & Performance")
        self.sla_expected = page.add_form_row("Erwartete Laufzeit:", _make_line(placeholder="z.B. 30 Sekunden"))
        self.sla_max = page.add_form_row("Maximale Laufzeit:", _make_line(placeholder="z.B. 5 Minuten"))
        self.sla_avg = page.add_form_row("Durchschnittl. Ausfuehrungen:", _make_line(placeholder="z.B. 50 pro Tag"))
        self.sla_crit = page.add_form_row("Kritikalitaet:", _make_combo([e.value for e in Criticality]))
        self.sla_escalation = page.add_form_row("Eskalationspfad:", _make_text(height=60))
        self.sla_desc = page.add_form_row("Beschreibung:", _make_text(height=60))

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 10. Governance
    # -------------------------------------------------------------------
    def _build_governance_page(self):
        page = FormPage("Governance & Betrieb")
        self.gov_dlp = page.add_form_row("DLP-Policy:", _make_line())
        self.gov_approval = page.add_form_row("Genehmigungs-Workflow:", _make_text(height=50))
        self.gov_monitor = page.add_form_row("Monitoring-Setup:", _make_text(height=50))
        self.gov_backup = page.add_form_row("Backup-Strategie:", _make_text(height=50))
        self.gov_test = page.add_form_row("Testverfahren:", _make_text(height=50))
        self.gov_testdata = page.add_form_row("Testdaten:", _make_text(height=50))
        self.gov_rollback = page.add_form_row("Rollback:", _make_text(height=50))

        page.add_separator()
        self.gov_assumptions = page.add_form_row("Annahmen:", _make_text(height=50))
        self.gov_limitations = page.add_form_row("Einschraenkungen:", _make_text(height=50))

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 11. Abhaengigkeiten
    # -------------------------------------------------------------------
    def _build_dependencies_page(self):
        page = FormPage("Abhaengigkeiten")
        self.dep_table = QTableWidget(0, 4)
        self.dep_table.setHorizontalHeaderLabels([
            "Typ", "Name", "Beschreibung", "Env-Variablen"
        ])
        self.dep_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.dep_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Abhaengigkeit")
        btn_add.clicked.connect(lambda: self._add_table_row(self.dep_table, ["", "", "", ""]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.dep_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 12. Aenderungsprotokoll
    # -------------------------------------------------------------------
    def _build_changelog_page(self):
        page = FormPage("Aenderungsprotokoll")
        self.cl_table = QTableWidget(0, 6)
        self.cl_table.setHorizontalHeaderLabels([
            "Version", "Datum", "Autor", "Beschreibung", "Auswirkung", "Ticket"
        ])
        self.cl_table.horizontalHeader().setStretchLastSection(True)
        page.add_widget(self.cl_table)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Eintrag")
        btn_add.clicked.connect(lambda: self._add_table_row(self.cl_table, [
            "1.0", datetime.now().strftime("%Y-%m-%d"), "", "", "minor", ""
        ]))
        btn_row.addWidget(btn_add)
        btn_del = QPushButton("- Entfernen")
        btn_del.setProperty("class", "danger")
        btn_del.clicked.connect(lambda: self._del_table_row(self.cl_table))
        btn_row.addWidget(btn_del)
        btn_row.addStretch()
        w = QWidget()
        w.setLayout(btn_row)
        page.add_widget(w)

        page.add_stretch()
        self.stack.addWidget(page)

    # -------------------------------------------------------------------
    # 13. Vorschau
    # -------------------------------------------------------------------
    def _build_preview_page(self):
        self.preview = PreviewWidget()
        self.stack.addWidget(self.preview)

    # ===================================================================
    # Daten <-> GUI Sync
    # ===================================================================

    def _collect_project(self):
        """Sammelt alle GUI-Daten ins Projekt-Objekt."""
        p = self.project

        # Meta
        p.meta.flow_name = self.meta_name.text()
        p.meta.description = self.meta_desc.toPlainText()
        p.meta.flow_type = self.meta_type.currentText()
        p.meta.status = self.meta_status.currentText()
        p.meta.owner = self.meta_owner.text()
        p.meta.author = self.meta_author.text()
        p.meta.created_date = self.meta_created.text()
        p.meta.last_modified = self.meta_modified.text()
        p.meta.solution_name = self.meta_solution.text()
        p.meta.license_requirement = self.meta_license.currentText()
        services_text = self.meta_services.toPlainText()
        p.meta.connected_services = [s.strip() for s in services_text.split(",") if s.strip()]

        # Environments
        p.meta.environments = []
        for r in range(self.env_table.rowCount()):
            it0 = self.env_table.item(r, 0)
            it1 = self.env_table.item(r, 1)
            p.meta.environments.append(EnvironmentInfo(
                env_type=it0.text() if it0 else "",
                url=it1.text() if it1 else "",
            ))

        # Branding
        p.branding.company_name = self.brand_company.text()
        p.branding.logo_path = self.brand_logo.text()
        p.branding.primary_color = self.brand_primary.text()
        p.branding.accent_color = self.brand_accent.text()
        p.branding.secondary_color = self.brand_secondary.text()
        p.branding.header_text = self.brand_header.text()
        p.branding.footer_text = self.brand_footer.text()
        p.branding.confidentiality_note = self.brand_conf.toPlainText()

        # Trigger
        p.trigger.name = self.trig_name.text()
        p.trigger.trigger_type = self.trig_type.text()
        p.trigger.connector = self.trig_connector.text()
        p.trigger.description = self.trig_desc.toPlainText()
        p.trigger.schedule_frequency = self.trig_freq.text()
        p.trigger.schedule_interval = self.trig_interval.text()
        p.trigger.schedule_timezone = self.trig_tz.text()
        p.trigger.authentication = self.trig_auth.text()
        p.trigger.filter_expression = self.trig_filter.toPlainText()
        p.trigger.input_schema = self.trig_schema.toPlainText()

        # Actions (already synced via tree)
        # Connectors
        p.connections = self._read_conn_table()
        # Variables
        p.variables = self._read_var_table()
        # Error handling
        p.error_handling = self._read_err_table()
        # Data Mappings
        p.data_mappings = self._read_map_table()

        # SLA
        p.sla.expected_runtime = self.sla_expected.text()
        p.sla.max_runtime = self.sla_max.text()
        p.sla.avg_executions = self.sla_avg.text()
        p.sla.criticality = self.sla_crit.currentText()
        p.sla.escalation_path = self.sla_escalation.toPlainText()
        p.sla.description = self.sla_desc.toPlainText()

        # Governance
        p.governance.dlp_policy = self.gov_dlp.text()
        p.governance.approval_workflow = self.gov_approval.toPlainText()
        p.governance.monitoring_setup = self.gov_monitor.toPlainText()
        p.governance.backup_strategy = self.gov_backup.toPlainText()
        p.governance.test_procedure = self.gov_test.toPlainText()
        p.governance.test_data = self.gov_testdata.toPlainText()
        p.governance.rollback_procedure = self.gov_rollback.toPlainText()
        p.governance.assumptions = self.gov_assumptions.toPlainText()
        p.governance.limitations = self.gov_limitations.toPlainText()

        # Dependencies
        p.dependencies = self._read_dep_table()
        # Changelog
        p.changelog = self._read_cl_table()

    def _populate_gui(self):
        """Fuellt die GUI aus dem Projekt-Objekt."""
        p = self.project

        # Meta
        self.meta_name.setText(p.meta.flow_name)
        self.meta_desc.setPlainText(p.meta.description)
        self.meta_type.setCurrentText(p.meta.flow_type)
        self.meta_status.setCurrentText(p.meta.status)
        self.meta_owner.setText(p.meta.owner)
        self.meta_author.setText(p.meta.author)
        self.meta_created.setText(p.meta.created_date)
        self.meta_modified.setText(p.meta.last_modified)
        self.meta_solution.setText(p.meta.solution_name)
        self.meta_license.setCurrentText(p.meta.license_requirement)
        self.meta_services.setPlainText(", ".join(p.meta.connected_services))

        # Environments
        self.env_table.setRowCount(0)
        for env in p.meta.environments:
            self._add_table_row(self.env_table, [env.env_type, env.url])

        # Branding
        self.brand_company.setText(p.branding.company_name)
        self.brand_logo.setText(p.branding.logo_path)
        self.brand_primary.setText(p.branding.primary_color)
        self.brand_accent.setText(p.branding.accent_color)
        self.brand_secondary.setText(p.branding.secondary_color)
        self.brand_header.setText(p.branding.header_text)
        self.brand_footer.setText(p.branding.footer_text)
        self.brand_conf.setPlainText(p.branding.confidentiality_note)

        # Trigger
        self.trig_name.setText(p.trigger.name)
        self.trig_type.setText(p.trigger.trigger_type)
        self.trig_connector.setText(p.trigger.connector)
        self.trig_desc.setPlainText(p.trigger.description)
        self.trig_freq.setText(p.trigger.schedule_frequency)
        self.trig_interval.setText(p.trigger.schedule_interval)
        self.trig_tz.setText(p.trigger.schedule_timezone)
        self.trig_auth.setText(p.trigger.authentication)
        self.trig_filter.setPlainText(p.trigger.filter_expression)
        self.trig_schema.setPlainText(p.trigger.input_schema)

        # Action tree
        self._populate_action_tree()

        # Connectors
        self.conn_table.setRowCount(0)
        for c in p.connections:
            self._add_table_row(self.conn_table, [
                c.connector_name, c.connector_type, c.connection_name,
                c.auth_type, c.service_account, c.required_permissions, c.gateway
            ])

        # Variables
        self.var_table.setRowCount(0)
        for v in p.variables:
            self._add_table_row(self.var_table, [
                v.name, v.var_type, v.initial_value, v.description, v.set_in, v.used_in
            ])

        # Error handling
        self.err_table.setRowCount(0)
        for eh in p.error_handling:
            self._add_table_row(self.err_table, [
                eh.scope_name, eh.pattern, eh.run_after_config,
                str(eh.retry_count), eh.retry_interval, eh.retry_type,
                eh.notification_method, eh.timeout
            ])

        # Data Mappings
        self.map_table.setRowCount(0)
        for m in p.data_mappings:
            self._add_table_row(self.map_table, [
                m.source_action, m.target_action, m.field_mapping,
                m.transformation, m.description
            ])

        # SLA
        self.sla_expected.setText(p.sla.expected_runtime)
        self.sla_max.setText(p.sla.max_runtime)
        self.sla_avg.setText(p.sla.avg_executions)
        self.sla_crit.setCurrentText(p.sla.criticality)
        self.sla_escalation.setPlainText(p.sla.escalation_path)
        self.sla_desc.setPlainText(p.sla.description)

        # Governance
        self.gov_dlp.setText(p.governance.dlp_policy)
        self.gov_approval.setPlainText(p.governance.approval_workflow)
        self.gov_monitor.setPlainText(p.governance.monitoring_setup)
        self.gov_backup.setPlainText(p.governance.backup_strategy)
        self.gov_test.setPlainText(p.governance.test_procedure)
        self.gov_testdata.setPlainText(p.governance.test_data)
        self.gov_rollback.setPlainText(p.governance.rollback_procedure)
        self.gov_assumptions.setPlainText(p.governance.assumptions)
        self.gov_limitations.setPlainText(p.governance.limitations)

        # Dependencies
        self.dep_table.setRowCount(0)
        for d in p.dependencies:
            self._add_table_row(self.dep_table, [
                d.dep_type, d.name, d.description, d.environment_variables
            ])

        # Changelog
        self.cl_table.setRowCount(0)
        for c in p.changelog:
            self._add_table_row(self.cl_table, [
                c.version, c.date, c.author, c.description, c.impact, c.ticket
            ])

        # Dashboard aktualisieren
        self._update_dashboard()

    def _update_dashboard(self):
        stats = get_flow_stats(self.project)
        self.stat_actions.set_value(stats["total_actions"])
        self.stat_connectors.set_value(stats["connectors"])
        self.stat_variables.set_value(stats["variables"])
        self.stat_errors.set_value(len(self.project.error_handling))

        name = self.project.meta.flow_name or "(Kein Name)"
        self.dash_info.setText(
            f"Flow: {name}  |  Typ: {self.project.meta.flow_type}  |  "
            f"Status: {self.project.meta.status}  |  "
            f"Trigger: {stats['trigger_type'] or '–'}"
        )

    # ===================================================================
    # Action Tree
    # ===================================================================

    def _populate_action_tree(self):
        self.action_tree.clear()
        self._add_actions_to_tree(self.project.actions, None)
        self.action_tree.expandAll()

    def _add_actions_to_tree(self, actions: list[FlowAction], parent_item):
        for action in actions:
            item = QTreeWidgetItem()
            item.setText(0, action.name)
            item.setText(1, action.action_type)
            item.setText(2, action.connector)
            item.setData(0, Qt.UserRole, action.id)
            # Tooltip
            item.setToolTip(0, action.description or action.name)

            if parent_item is None:
                self.action_tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            if action.children:
                self._add_actions_to_tree(action.children, item)

    def _find_action_by_id(self, action_id: str, actions: list[FlowAction] | None = None) -> FlowAction | None:
        if actions is None:
            actions = self.project.actions
        for a in actions:
            if a.id == action_id:
                return a
            found = self._find_action_by_id(action_id, a.children)
            if found:
                return found
        return None

    def _on_action_selected(self, current, previous):
        if current is None:
            return
        action_id = current.data(0, Qt.UserRole)
        action = self._find_action_by_id(action_id)
        if action:
            self.act_name.setText(action.name)
            self.act_type.setText(action.action_type)
            self.act_connector.setText(action.connector)
            self.act_desc.setPlainText(action.description)
            self.act_config.setPlainText(action.configuration)
            self.act_inputs.setText(action.inputs_summary)
            self.act_outputs.setText(action.outputs_summary)
            self.act_expr.setPlainText(action.expression)
            self.act_ra_success.setChecked("Succeeded" in action.run_after or "is successful" in action.run_after)
            self.act_ra_failed.setChecked("has failed" in action.run_after)
            self.act_ra_skipped.setChecked("is skipped" in action.run_after)
            self.act_ra_timeout.setChecked("has timed out" in action.run_after)

    def _apply_action_changes(self):
        current = self.action_tree.currentItem()
        if current is None:
            return
        action_id = current.data(0, Qt.UserRole)
        action = self._find_action_by_id(action_id)
        if action:
            action.name = self.act_name.text()
            action.action_type = self.act_type.text()
            action.connector = self.act_connector.text()
            action.description = self.act_desc.toPlainText()
            action.configuration = self.act_config.toPlainText()
            action.inputs_summary = self.act_inputs.text()
            action.outputs_summary = self.act_outputs.text()
            action.expression = self.act_expr.toPlainText()

            ra = []
            if self.act_ra_success.isChecked():
                ra.append("is successful")
            if self.act_ra_failed.isChecked():
                ra.append("has failed")
            if self.act_ra_skipped.isChecked():
                ra.append("is skipped")
            if self.act_ra_timeout.isChecked():
                ra.append("has timed out")
            action.run_after = ra

            # Tree-Item aktualisieren
            current.setText(0, action.name)
            current.setText(1, action.action_type)
            current.setText(2, action.connector)
            self.toast.show_message("Aktion aktualisiert")

    def _add_action(self):
        action = FlowAction(name="Neue Aktion")
        self.project.actions.append(action)
        self._populate_action_tree()

    def _add_child_action(self):
        current = self.action_tree.currentItem()
        if current is None:
            self._add_action()
            return
        action_id = current.data(0, Qt.UserRole)
        parent = self._find_action_by_id(action_id)
        if parent:
            child = FlowAction(name="Neue Kind-Aktion", parent_id=parent.id)
            parent.children.append(child)
            self._populate_action_tree()

    def _del_action(self):
        current = self.action_tree.currentItem()
        if current is None:
            return
        action_id = current.data(0, Qt.UserRole)
        self._remove_action_by_id(action_id, self.project.actions)
        self._populate_action_tree()

    def _remove_action_by_id(self, action_id: str, actions: list[FlowAction]) -> bool:
        for i, a in enumerate(actions):
            if a.id == action_id:
                actions.pop(i)
                return True
            if self._remove_action_by_id(action_id, a.children):
                return True
        return False

    # ===================================================================
    # Table Helpers
    # ===================================================================

    def _add_table_row(self, table: QTableWidget, values: list[str]):
        row = table.rowCount()
        table.insertRow(row)
        for col, val in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(str(val)))

    def _del_table_row(self, table: QTableWidget):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def _read_conn_table(self) -> list[FlowConnection]:
        result = []
        for r in range(self.conn_table.rowCount()):
            c = FlowConnection()
            c.connector_name = (self.conn_table.item(r, 0) or QTableWidgetItem()).text()
            c.connector_type = (self.conn_table.item(r, 1) or QTableWidgetItem()).text()
            c.connection_name = (self.conn_table.item(r, 2) or QTableWidgetItem()).text()
            c.auth_type = (self.conn_table.item(r, 3) or QTableWidgetItem()).text()
            c.service_account = (self.conn_table.item(r, 4) or QTableWidgetItem()).text()
            c.required_permissions = (self.conn_table.item(r, 5) or QTableWidgetItem()).text()
            c.gateway = (self.conn_table.item(r, 6) or QTableWidgetItem()).text()
            result.append(c)
        return result

    def _read_var_table(self) -> list[FlowVariable]:
        result = []
        for r in range(self.var_table.rowCount()):
            v = FlowVariable()
            v.name = (self.var_table.item(r, 0) or QTableWidgetItem()).text()
            v.var_type = (self.var_table.item(r, 1) or QTableWidgetItem()).text()
            v.initial_value = (self.var_table.item(r, 2) or QTableWidgetItem()).text()
            v.description = (self.var_table.item(r, 3) or QTableWidgetItem()).text()
            v.set_in = (self.var_table.item(r, 4) or QTableWidgetItem()).text()
            v.used_in = (self.var_table.item(r, 5) or QTableWidgetItem()).text()
            result.append(v)
        return result

    def _read_err_table(self) -> list[ErrorHandling]:
        result = []
        for r in range(self.err_table.rowCount()):
            eh = ErrorHandling()
            eh.scope_name = (self.err_table.item(r, 0) or QTableWidgetItem()).text()
            eh.pattern = (self.err_table.item(r, 1) or QTableWidgetItem()).text()
            eh.run_after_config = (self.err_table.item(r, 2) or QTableWidgetItem()).text()
            try:
                eh.retry_count = int((self.err_table.item(r, 3) or QTableWidgetItem()).text())
            except ValueError:
                eh.retry_count = 0
            eh.retry_interval = (self.err_table.item(r, 4) or QTableWidgetItem()).text()
            eh.retry_type = (self.err_table.item(r, 5) or QTableWidgetItem()).text()
            eh.notification_method = (self.err_table.item(r, 6) or QTableWidgetItem()).text()
            eh.timeout = (self.err_table.item(r, 7) or QTableWidgetItem()).text()
            result.append(eh)
        return result

    def _read_map_table(self) -> list[DataMapping]:
        result = []
        for r in range(self.map_table.rowCount()):
            m = DataMapping()
            m.source_action = (self.map_table.item(r, 0) or QTableWidgetItem()).text()
            m.target_action = (self.map_table.item(r, 1) or QTableWidgetItem()).text()
            m.field_mapping = (self.map_table.item(r, 2) or QTableWidgetItem()).text()
            m.transformation = (self.map_table.item(r, 3) or QTableWidgetItem()).text()
            m.description = (self.map_table.item(r, 4) or QTableWidgetItem()).text()
            result.append(m)
        return result

    def _read_dep_table(self) -> list[FlowDependency]:
        result = []
        for r in range(self.dep_table.rowCount()):
            d = FlowDependency()
            d.dep_type = (self.dep_table.item(r, 0) or QTableWidgetItem()).text()
            d.name = (self.dep_table.item(r, 1) or QTableWidgetItem()).text()
            d.description = (self.dep_table.item(r, 2) or QTableWidgetItem()).text()
            d.environment_variables = (self.dep_table.item(r, 3) or QTableWidgetItem()).text()
            result.append(d)
        return result

    def _read_cl_table(self) -> list[ChangeLogEntry]:
        result = []
        for r in range(self.cl_table.rowCount()):
            c = ChangeLogEntry()
            c.version = (self.cl_table.item(r, 0) or QTableWidgetItem()).text()
            c.date = (self.cl_table.item(r, 1) or QTableWidgetItem()).text()
            c.author = (self.cl_table.item(r, 2) or QTableWidgetItem()).text()
            c.description = (self.cl_table.item(r, 3) or QTableWidgetItem()).text()
            c.impact = (self.cl_table.item(r, 4) or QTableWidgetItem()).text()
            c.ticket = (self.cl_table.item(r, 5) or QTableWidgetItem()).text()
            result.append(c)
        return result

    # ===================================================================
    # Actions
    # ===================================================================

    def _save(self):
        self._collect_project()
        # Im Solution-Modus den aktuellen Flow zurueckschreiben
        if self._current_flow_name and self._current_flow_name in self._solution_flows:
            self._solution_flows[self._current_flow_name] = self.project
        save_project(self.project, PROJECT_PATH)
        self._update_dashboard()
        self.toast.show_message("Projekt gespeichert ✓")

    def _load_existing(self):
        if PROJECT_PATH.exists():
            self.project = load_project(PROJECT_PATH)
            self._populate_gui()

    def _new_project(self):
        reply = QMessageBox.question(
            self, "Neues Projekt",
            "Aktuelles Projekt verwerfen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.project = PAProject()
            self._populate_gui()
            self.toast.show_message("Neues Projekt erstellt")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Projekt oeffnen", "",
            "YAML (*.yml *.yaml);;JSON (*.json);;Alle (*)"
        )
        if path:
            self.project = load_project(path)
            self._populate_gui()
            self.toast.show_message("Projekt geladen ✓")

    def _import_flow(self):
        dlg = ImportDialog(self)
        if dlg.exec() == QDialog.Accepted and dlg.result_project:
            imported = dlg.result_project
            if dlg.chk_overwrite.isChecked():
                # Ueberschreiben (Metadaten + Aktionen + Variablen + Konnektoren)
                self.project.meta = imported.meta
                self.project.trigger = imported.trigger
                self.project.actions = imported.actions
                self.project.variables = imported.variables
                self.project.connections = imported.connections
            else:
                # Zusammenfuehren
                self.project.actions.extend(imported.actions)
                self.project.variables.extend(imported.variables)
                self.project.connections.extend(imported.connections)
                if not self.project.trigger.name:
                    self.project.trigger = imported.trigger
                if not self.project.meta.flow_name:
                    self.project.meta = imported.meta

            self._populate_gui()
            self.toast.show_message("Flow importiert ✓", "success")

    def _generate_markdown(self):
        self._collect_project()
        try:
            out = generate_docs(self.project)
            self.toast.show_message(f"Markdown generiert → {out}")
        except Exception as e:
            self.toast.show_message(f"Fehler: {e}", "error")

    def _export_pdf(self):
        self._collect_project()
        path, _ = QFileDialog.getSaveFileName(
            self, "PDF speichern", "flow_documentation.pdf",
            "PDF (*.pdf)"
        )
        if path:
            try:
                export_pdf(self.project, path)
                self.toast.show_message(f"PDF exportiert ✓")
            except Exception as e:
                self.toast.show_message(f"PDF-Fehler: {e}", "error")

    def _choose_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Logo waehlen", "",
            "Bilder (*.png *.jpg *.jpeg *.svg);;Alle (*)"
        )
        if path:
            self.brand_logo.setText(path)

    def _refresh_preview(self):
        self._collect_project()
        try:
            from generator import (
                _gen_index, _gen_overview, _gen_trigger, _gen_actions,
                _gen_variables, _gen_data_mappings, _gen_connectors,
                _gen_dependencies, _gen_error_handling, _gen_sla,
                _gen_governance, _gen_changelog, _gen_flowchart,
            )

            section = self.preview.section_combo.currentIndex()
            generators = [
                lambda: "\n\n".join([
                    _gen_index(self.project),
                    _gen_overview(self.project),
                    _gen_trigger(self.project),
                    _gen_flowchart(self.project),
                    _gen_actions(self.project),
                    _gen_variables(self.project),
                ]),
                lambda: _gen_overview(self.project),
                lambda: _gen_trigger(self.project),
                lambda: _gen_flowchart(self.project),
                lambda: _gen_actions(self.project),
                lambda: _gen_variables(self.project),
                lambda: _gen_data_mappings(self.project),
                lambda: _gen_connectors(self.project),
                lambda: _gen_dependencies(self.project),
                lambda: _gen_error_handling(self.project),
                lambda: _gen_sla(self.project),
                lambda: _gen_governance(self.project),
                lambda: _gen_changelog(self.project),
            ]
            md = generators[section]()
            self.preview.set_markdown(md)
        except Exception as e:
            self.preview.set_markdown(f"# Fehler\n\n```\n{e}\n```")

    # ===================================================================
    # Solution Import & Generierung
    # ===================================================================

    def _import_solution(self):
        """Oeffnet den Solution-Import-Dialog und laedt alle Entities."""
        dlg = SolutionImportDialog(self)
        if dlg.exec() == QDialog.Accepted and dlg.result_solution:
            self._current_solution = dlg.result_solution
            solution = dlg.result_solution

            # Alle Flows speichern
            self._solution_flows.clear()
            self.sol_flow_combo.blockSignals(True)
            self.sol_flow_combo.clear()

            for flow_entity in solution.flows:
                if flow_entity.flow_project:
                    flow_name = flow_entity.display_name or flow_entity.name or f"Flow {len(self._solution_flows) + 1}"
                    proj = flow_entity.flow_project
                    # Solution-Name automatisch setzen
                    proj.meta.solution_name = solution.display_name or solution.unique_name
                    self._solution_flows[flow_name] = proj
                    self.sol_flow_combo.addItem(flow_name)

            self.sol_flow_combo.blockSignals(False)

            # Dependencies und Connectors automatisch aus Solution fuellen
            self._auto_populate_from_solution(solution)

            # Ersten Flow laden
            if self._solution_flows:
                first_name = list(self._solution_flows.keys())[0]
                self._current_flow_name = first_name
                self.project = self._solution_flows[first_name]
                self._populate_gui()
                self.sol_flow_combo.setCurrentIndex(0)
            else:
                # Kein Flow vorhanden, leeres Projekt mit Solution-Metadaten
                self.project = PAProject()
                self.project.meta.solution_name = solution.display_name or solution.unique_name
                self._populate_gui()

            # Solution-Seite aktualisieren
            self._refresh_solution_page()

            self.toast.show_message(
                f"Solution importiert: {len(solution.flows)} Flows, "
                f"{len(solution.entities)} Komponenten ✓",
                "success"
            )

            # Zur Solution-Seite wechseln
            self.sidebar.select_page(1)
            self._on_page_changed(1)

    def _auto_populate_from_solution(self, solution: SolutionInfo):
        """Fuellt automatisch Daten aus der Solution in alle Flow-Projekte."""
        # Connection References als Connectors hinzufuegen
        for flow_name, proj in self._solution_flows.items():
            # Environment Variables als Dependencies
            if solution.env_variables:
                for ev in solution.env_variables:
                    dep = FlowDependency(
                        dep_type="Environment Variable",
                        name=ev.display_name or ev.name,
                        description=ev.description or "",
                        environment_variables=ev.details.get("default_value", "") if ev.details else "",
                    )
                    # Pruefen ob schon vorhanden
                    existing_names = {d.name for d in proj.dependencies}
                    if dep.name not in existing_names:
                        proj.dependencies.append(dep)

            # Connection References als Connectors
            if solution.connection_references:
                for cr in solution.connection_references:
                    conn_name = cr.display_name or cr.name
                    existing_conn_names = {c.connector_name for c in proj.connections}
                    if conn_name not in existing_conn_names:
                        conn = FlowConnection(
                            connector_name=conn_name,
                            connector_type="Connection Reference",
                            connection_name=cr.details.get("connection_name", "") if cr.details else "",
                        )
                        proj.connections.append(conn)

            # Custom Connectors
            if solution.custom_connectors:
                for cc in solution.custom_connectors:
                    cc_name = cc.display_name or cc.name
                    existing_conn_names = {c.connector_name for c in proj.connections}
                    if cc_name not in existing_conn_names:
                        conn = FlowConnection(
                            connector_name=cc_name,
                            connector_type="Custom",
                            connection_name=cc.description or "",
                        )
                        proj.connections.append(conn)

    def _generate_solution_markdown(self):
        """Generiert Markdown-Dokumentation fuer die gesamte Solution."""
        if self._current_solution is None:
            # Wenn keine Solution geladen, anbieten eine zu importieren
            reply = QMessageBox.question(
                self, "Solution-Dokumentation",
                "Keine Solution geladen. Moechten Sie eine Solution-ZIP-Datei importieren?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._import_solution()
            if self._current_solution is None:
                return

        try:
            out = generate_solution_docs(self._current_solution, Path("docs/solution"))
            self.toast.show_message(f"Solution-Doku generiert → {out}")
        except Exception as e:
            self.toast.show_message(f"Fehler: {e}", "error")
