"""
ui/preview.py – Live-Vorschau: Markdown -> HTML.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSplitter, QTabWidget, QPlainTextEdit, QComboBox,
)

from ui.theme import BG_BASE, BG_CARD, ACCENT, TEXT_PRIMARY, BORDER

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


PREVIEW_CSS = f"""
<style>
    body {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 13px;
        padding: 16px;
        line-height: 1.6;
    }}
    h1 {{ color: {ACCENT}; border-bottom: 1px solid {BORDER}; padding-bottom: 6px; }}
    h2 {{ color: {ACCENT}; margin-top: 20px; }}
    h3 {{ color: #8BA8D9; }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }}
    th, td {{
        border: 1px solid {BORDER};
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background-color: {ACCENT};
        color: white;
    }}
    tr:nth-child(even) {{
        background-color: #1A1D28;
    }}
    code {{
        background-color: #1E2233;
        padding: 2px 5px;
        border-radius: 3px;
        font-family: Consolas, monospace;
        font-size: 12px;
    }}
    pre {{
        background-color: #1E2233;
        padding: 12px;
        border-radius: 4px;
        overflow-x: auto;
    }}
    pre code {{
        background: none;
        padding: 0;
    }}
    a {{ color: {ACCENT}; text-decoration: none; }}
    blockquote {{
        border-left: 3px solid {ACCENT};
        margin: 10px 0;
        padding: 6px 12px;
        color: #8B8FA3;
    }}
    ul, ol {{ padding-left: 24px; }}
    li {{ margin: 3px 0; }}
</style>
"""


class PreviewWidget(QWidget):
    """Live-Vorschau mit Tabs: HTML-Ansicht und Raw-Markdown."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Vorschau")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold;")
        hdr.addWidget(title)

        self.section_combo = QComboBox()
        self.section_combo.addItems([
            "Komplett",
            "Uebersicht",
            "Trigger",
            "Flussdiagramm",
            "Aktionen",
            "Variablen",
            "Datenmappings",
            "Konnektoren",
            "Abhaengigkeiten",
            "Fehlerbehandlung",
            "SLA & Performance",
            "Governance",
            "Aenderungsprotokoll",
        ])
        hdr.addWidget(self.section_combo)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Tab-Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # HTML-Ansicht
        self.html_view = QTextEdit()
        self.html_view.setReadOnly(True)
        self.tabs.addTab(self.html_view, "HTML-Ansicht")

        # Raw Markdown
        self.raw_view = QPlainTextEdit()
        self.raw_view.setReadOnly(True)
        self.raw_view.setFont(__import__("PySide6.QtGui", fromlist=["QFont"]).QFont("Consolas", 11))
        self.tabs.addTab(self.raw_view, "Markdown")

    def set_markdown(self, md_text: str):
        """Setzt den Markdown-Inhalt und rendert HTML."""
        self.raw_view.setPlainText(md_text)
        if HAS_MARKDOWN:
            html = markdown.markdown(
                md_text,
                extensions=["tables", "fenced_code", "toc"],
            )
        else:
            # Fallback: einfache Konvertierung
            html = f"<pre>{md_text}</pre>"
        self.html_view.setHtml(PREVIEW_CSS + html)

    def set_html(self, html: str):
        self.html_view.setHtml(PREVIEW_CSS + html)
