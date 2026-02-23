"""
Dark-mode colour palette, constants, and the global QSS stylesheet.
All UI modules import from here to ensure visual consistency.
"""

# ── Colour Tokens ────────────────────────────────────────────────
BG_BASE      = "#0F1117"     # deepest background
BG_SURFACE   = "#161922"     # cards / panels
BG_ELEVATED  = "#1C1F2E"     # sidebar, tooltips
BG_INPUT     = "#1E2130"     # text fields
BG_HOVER     = "#252A3A"     # hover states
BG_SELECTED  = "#2A3352"     # selected rows

BORDER       = "#2D3348"     # subtle borders
BORDER_FOCUS = "#5B8DEF"     # focused input

TEXT_PRIMARY  = "#E2E8F0"    # main text
TEXT_SECONDARY= "#8892A8"    # labels, hints
TEXT_MUTED    = "#525C72"    # disabled text
TEXT_INVERSE  = "#0F1117"    # text on accent bg
TEXT_BEIGE    = "#EADFC8"    # high-contrast warm text for controls

ACCENT       = "#5B8DEF"    # primary accent (buttons, links)
ACCENT_HOVER = "#7BA4F7"
ACCENT_DARK  = "#3D6AD6"
SUCCESS      = "#34D399"
SUCCESS_BG   = "#132B21"
WARNING      = "#FBBF24"
WARNING_BG   = "#2B2514"
DANGER       = "#F87171"
DANGER_BG    = "#2B1515"

# Power BI brand-ish
PBI_YELLOW   = "#F2C811"
PBI_DARK     = "#1B3A5C"

# Table header
TBL_HEADER   = "#1A2035"
TBL_ROW_ALT  = "#13151E"

# Code editor
CODE_BG      = "#12141C"
CODE_FG      = "#A8D4A0"     # green-ish code text
CODE_KEYWORD = "#C792EA"     # purple keywords
CODE_STRING  = "#C3E88D"
CODE_COMMENT = "#546E7A"

# ── Font ─────────────────────────────────────────────────────────
FONT_FAMILY  = "Segoe UI"
FONT_MONO    = "Cascadia Code, Consolas, Courier New, monospace"
FONT_SIZE    = 13

# ── Sidebar ──────────────────────────────────────────────────────
SIDEBAR_W    = 220

# ── Sizes ────────────────────────────────────────────────────────
RADIUS       = "6px"
RADIUS_SM    = "4px"
RADIUS_LG    = "8px"

# ── Global QSS ──────────────────────────────────────────────────

GLOBAL_QSS = f"""
/* ── Base ──────────────────────────────────────────── */
QMainWindow, QDialog {{
    background: {BG_BASE};
    color: {TEXT_PRIMARY};
}}
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: "{FONT_FAMILY}";
    font-size: {FONT_SIZE}px;
}}

/* ── Scroll areas ─────────────────────────────────── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {BG_SURFACE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_SURFACE};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
}}

/* ── Labels ───────────────────────────────────────── */
QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
}}

/* ── Inputs ───────────────────────────────────────── */
QLineEdit, QSpinBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 7px 10px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {BORDER_FOCUS};
}}
QLineEdit:disabled {{
    color: {TEXT_MUTED};
    background: {BG_BASE};
}}

QTextEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 6px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QTextEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 7px 10px;
    color: {TEXT_PRIMARY};
}}
QComboBox:hover {{
    border-color: {TEXT_MUTED};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
    selection-background-color: {BG_SELECTED};
}}

QCheckBox {{
    spacing: 8px;
    color: {TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid {BORDER};
    background: {BG_INPUT};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Buttons ──────────────────────────────────────── */
QPushButton {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    padding: 8px 16px;
    color: {TEXT_BEIGE};
    font-weight: 500;
}}
QPushButton:hover {{
    background: {BG_HOVER};
    border-color: {TEXT_MUTED};
}}
QPushButton:pressed {{
    background: {BG_SELECTED};
}}
QPushButton:disabled {{
    background: {BG_BASE};
    color: {TEXT_MUTED};
    border-color: {BG_BASE};
}}

QPushButton#primary {{
    background: {ACCENT};
    color: {TEXT_BEIGE};
    border-color: {ACCENT};
    font-weight: 600;
}}
QPushButton#primary:hover {{
    background: {ACCENT_HOVER};
}}
QPushButton#primary:pressed {{
    background: {ACCENT_DARK};
}}

QPushButton#accent {{
    background: {PBI_YELLOW};
    color: {PBI_DARK};
    border-color: {PBI_YELLOW};
    font-weight: 600;
}}
QPushButton#accent:hover {{
    background: #E5B800;
}}

QPushButton#success {{
    background: {SUCCESS};
    color: {TEXT_BEIGE};
    border-color: {SUCCESS};
    font-weight: 600;
}}
QPushButton#success:hover {{
    background: #2FBC89;
}}

QPushButton#danger {{
    background: transparent;
    color: {DANGER};
    border-color: {DANGER};
}}
QPushButton#danger:hover {{
    background: {DANGER_BG};
}}

/* ── Group boxes ──────────────────────────────────── */
QGroupBox {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_LG};
    margin-top: 14px;
    padding: 20px 14px 14px 14px;
    font-weight: 600;
    font-size: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {ACCENT};
}}

/* ── Tabs ─────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    background: {BG_SURFACE};
    top: -1px;
}}
QTabBar::tab {{
    background: {BG_BASE};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: {RADIUS_SM} {RADIUS_SM} 0 0;
    padding: 8px 20px;
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {BG_SURFACE};
    color: {ACCENT};
    font-weight: 600;
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}

/* ── Tables ───────────────────────────────────────── */
QTableWidget {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    gridline-color: {BORDER};
    font-size: 12px;
    selection-background-color: {BG_SELECTED};
}}
QTableWidget::item {{
    padding: 5px;
    border-bottom: 1px solid {BG_BASE};
}}
QTableWidget::item:selected {{
    background: {BG_SELECTED};
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background: {TBL_HEADER};
    color: {TEXT_SECONDARY};
    padding: 7px 8px;
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
    font-size: 12px;
}}

/* ── Splitter ─────────────────────────────────────── */
QSplitter::handle {{
    background: {BORDER};
}}

/* ── Status bar ───────────────────────────────────── */
QStatusBar {{
    background: {BG_ELEVATED};
    color: {TEXT_SECONDARY};
    font-size: 12px;
    border-top: 1px solid {BORDER};
}}

/* ── Tooltip ──────────────────────────────────────── */
QToolTip {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 6px 10px;
    border-radius: {RADIUS_SM};
    font-size: 12px;
}}

/* ── Message boxes ────────────────────────────────── */
QMessageBox {{
    background: {BG_SURFACE};
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}

/* ── Progress dialog ──────────────────────────────── */
QProgressDialog {{
    background: {BG_SURFACE};
}}
QProgressBar {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM};
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 12px;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: {RADIUS_SM};
}}

/* ── Menu ─────────────────────────────────────────── */
QMenu {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: {RADIUS_SM};
}}
QMenu::item:selected {{
    background: {BG_SELECTED};
}}
"""
