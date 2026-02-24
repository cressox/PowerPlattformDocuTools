"""
ui/theme.py – Dark-Mode Farbpalette und globales QSS fuer die GUI.
"""

# ---------------------------------------------------------------------------
# Farbpalette (identisch zum PBI-Tool)
# ---------------------------------------------------------------------------

BG_BASE = "#0F1117"
BG_CARD = "#161822"
BG_INPUT = "#1C1F2E"
BG_HOVER = "#252838"
BG_SIDEBAR = "#0D0E14"

TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#8B8FA3"
TEXT_MUTED = "#5A5E72"

ACCENT = "#5B8DEF"
ACCENT_HOVER = "#7BA4F7"
ACCENT_PRESSED = "#4A73CC"

SUCCESS = "#4CAF50"
WARNING = "#E0A526"
ERROR = "#EF5B5B"
INFO = "#5B8DEF"

BORDER = "#2A2D3A"
BORDER_FOCUS = "#5B8DEF"

SCROLLBAR_BG = "#161822"
SCROLLBAR_HANDLE = "#2A2D3A"

SIDEBAR_SELECTED = "#1E2233"
SIDEBAR_HOVER = "#191C28"

# ---------------------------------------------------------------------------
# Globales Stylesheet
# ---------------------------------------------------------------------------

GLOBAL_QSS = f"""
/* ---------- Basis ---------- */
QWidget {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BG_BASE};
}}

/* ---------- Labels ---------- */
QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
    padding: 2px;
}}
QLabel[class="section-title"] {{
    font-size: 16px;
    font-weight: bold;
    color: {ACCENT};
    padding: 6px 0;
}}
QLabel[class="muted"] {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

/* ---------- Inputs ---------- */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 8px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
    color: {TEXT_PRIMARY};
    min-height: 22px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 7px 16px;
    font-weight: bold;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
}}
QPushButton:disabled {{
    background-color: {BG_HOVER};
    color: {TEXT_MUTED};
}}
QPushButton[class="secondary"] {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
}}
QPushButton[class="secondary"]:hover {{
    background-color: {BG_HOVER};
}}
QPushButton[class="danger"] {{
    background-color: {ERROR};
}}
QPushButton[class="danger"]:hover {{
    background-color: #FF7070;
}}

/* ---------- Tabs ---------- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_CARD};
    border-radius: 4px;
}}
QTabBar::tab {{
    background-color: {BG_BASE};
    color: {TEXT_SECONDARY};
    padding: 8px 16px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}

/* ---------- Scroll ---------- */
QScrollBar:vertical {{
    background: {SCROLLBAR_BG};
    width: 10px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {SCROLLBAR_HANDLE};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {SCROLLBAR_BG};
    height: 10px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {SCROLLBAR_HANDLE};
    border-radius: 5px;
    min-width: 30px;
}}

/* ---------- Tree / Table ---------- */
QTreeWidget, QTableWidget, QListWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    alternate-background-color: {BG_INPUT};
    gridline-color: {BORDER};
}}
QTreeWidget::item, QTableWidget::item, QListWidget::item {{
    padding: 4px;
}}
QTreeWidget::item:selected, QTableWidget::item:selected, QListWidget::item:selected {{
    background-color: {ACCENT};
    color: white;
}}
QTreeWidget::item:hover, QListWidget::item:hover {{
    background-color: {BG_HOVER};
}}
QHeaderView::section {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    padding: 5px;
    font-weight: bold;
}}

/* ---------- Splitter ---------- */
QSplitter::handle {{
    background-color: {BORDER};
}}
QSplitter::handle:horizontal {{
    width: 2px;
}}
QSplitter::handle:vertical {{
    height: 2px;
}}

/* ---------- GroupBox ---------- */
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: {TEXT_SECONDARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    padding: 0 6px;
    color: {ACCENT};
}}

/* ---------- ToolTip ---------- */
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 4px;
}}

/* ---------- Menu ---------- */
QMenuBar {{
    background-color: {BG_SIDEBAR};
    border-bottom: 1px solid {BORDER};
}}
QMenuBar::item:selected {{
    background-color: {BG_HOVER};
}}
QMenu {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
}}
QMenu::item:selected {{
    background-color: {ACCENT};
    color: white;
}}

/* ---------- StatusBar ---------- */
QStatusBar {{
    background-color: {BG_SIDEBAR};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
}}

/* ---------- ProgressBar ---------- */
QProgressBar {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 18px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 3px;
}}

/* ---------- Dialog ---------- */
QDialog {{
    background-color: {BG_BASE};
}}
"""


def apply_theme(app):
    """Wendet das Dark-Mode-Stylesheet auf die gesamte Anwendung an."""
    app.setStyleSheet(GLOBAL_QSS)
