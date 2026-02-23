"""
Preview page – renders the generated documentation as styled HTML
inside a QTextBrowser, dark-mode themed.
"""

from __future__ import annotations
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextBrowser, QTabWidget, QComboBox, QSplitter, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .theme import *
from ..models import Project
from ..generator import (
    gen_index, gen_overview, gen_kpis, gen_data_sources, gen_queries,
    gen_data_model, gen_measures, gen_pages_visuals,
    gen_refresh_gateway_rls, gen_assumptions_limitations, gen_change_log,
)


# Simple Markdown-to-HTML converter (no dependency needed)
def _md_to_html(md: str) -> str:
    """Convert basic Markdown to HTML for preview (headings, tables, code, bold, italic, lists, hr)."""
    import html as html_mod
    lines = md.split("\n")
    out = []
    in_code = False
    in_table = False
    code_lang = ""

    for line in lines:
        # Code fences
        if line.strip().startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                code_lang = line.strip()[3:].strip()
                out.append(f'<pre style="background:{CODE_BG}; color:{CODE_FG}; '
                           f'padding:12px; border-radius:6px; border:1px solid {BORDER}; '
                           f'font-family:Consolas,monospace; font-size:12px; overflow-x:auto;">'
                           f'<code>')
                in_code = True
            continue

        if in_code:
            out.append(html_mod.escape(line))
            continue

        stripped = line.strip()

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            if in_table:
                out.append("</table>")
                in_table = False
            out.append(f'<hr style="border:none; border-top:1px solid {BORDER}; margin:12px 0;">')
            continue

        # Table rows
        if "|" in stripped and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Skip separator rows
            if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                continue
            if not in_table:
                out.append(f'<table style="width:100%; border-collapse:collapse; '
                           f'margin:8px 0; font-size:12px;">')
                # First row = header
                out.append("<tr>")
                for c in cells:
                    out.append(f'<th style="background:{TBL_HEADER}; color:{TEXT_SECONDARY}; '
                               f'padding:8px; border:1px solid {BORDER}; text-align:left; '
                               f'font-weight:600;">{_inline_md(c)}</th>')
                out.append("</tr>")
                in_table = True
                continue
            out.append("<tr>")
            for c in cells:
                out.append(f'<td style="padding:6px 8px; border:1px solid {BORDER}; '
                           f'color:{TEXT_PRIMARY};">{_inline_md(c)}</td>')
            out.append("</tr>")
            continue

        if in_table and not ("|" in stripped):
            out.append("</table>")
            in_table = False

        # Headings
        if stripped.startswith("# "):
            out.append(f'<h1 style="color:{ACCENT}; font-size:20px; margin:18px 0 8px 0; '
                       f'border-bottom:1px solid {BORDER}; padding-bottom:6px;">'
                       f'{_inline_md(stripped[2:])}</h1>')
            continue
        if stripped.startswith("## "):
            out.append(f'<h2 style="color:{TEXT_PRIMARY}; font-size:16px; margin:14px 0 6px 0;">'
                       f'{_inline_md(stripped[3:])}</h2>')
            continue
        if stripped.startswith("### "):
            out.append(f'<h3 style="color:{TEXT_SECONDARY}; font-size:14px; margin:10px 0 4px 0;">'
                       f'{_inline_md(stripped[4:])}</h3>')
            continue

        # Blockquote
        if stripped.startswith("> "):
            out.append(f'<blockquote style="border-left:3px solid {ACCENT}; margin:8px 0; '
                       f'padding:4px 12px; color:{TEXT_SECONDARY}; font-style:italic;">'
                       f'{_inline_md(stripped[2:])}</blockquote>')
            continue

        # List items
        if stripped.startswith("- ") or stripped.startswith("* "):
            out.append(f'<div style="padding-left:16px; margin:2px 0;">• {_inline_md(stripped[2:])}</div>')
            continue

        # Numbered list
        import re
        num_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if num_match:
            out.append(f'<div style="padding-left:16px; margin:2px 0;">'
                       f'{num_match.group(1)}. {_inline_md(num_match.group(2))}</div>')
            continue

        # Empty lines
        if not stripped:
            out.append("<br>")
            continue

        # Paragraph
        out.append(f'<p style="margin:4px 0; line-height:1.6;">{_inline_md(stripped)}</p>')

    if in_table:
        out.append("</table>")
    if in_code:
        out.append("</code></pre>")

    return "\n".join(out)


def _inline_md(text: str) -> str:
    """Process inline markdown: bold, italic, code, links."""
    import re
    import html as html_mod
    # Inline code
    text = re.sub(r'`([^`]+)`',
                  rf'<code style="background:{CODE_BG}; color:{CODE_FG}; '
                  rf'padding:2px 5px; border-radius:3px; font-family:Consolas,monospace; '
                  rf'font-size:12px;">\1</code>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', rf'<em style="color:{TEXT_SECONDARY};">\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  rf'<a style="color:{ACCENT}; text-decoration:none;" href="\2">\1</a>', text)
    return text


# ── Sections for the dropdown ─────────────────────────────────────

PREVIEW_SECTIONS = [
    ("index.md", "Startseite", gen_index),
    ("overview.md", "Übersicht", gen_overview),
    ("kpis.md", "KPIs & Kennzahlen", gen_kpis),
    ("data_sources.md", "Datenquellen", gen_data_sources),
    ("queries.md", "Power Query (M)", gen_queries),
    ("data_model.md", "Datenmodell", gen_data_model),
    ("measures.md", "Measures (DAX)", gen_measures),
    ("pages_visuals.md", "Berichtsseiten", gen_pages_visuals),
    ("refresh.md", "Governance", gen_refresh_gateway_rls),
    ("assumptions.md", "Annahmen", gen_assumptions_limitations),
    ("change_log.md", "Änderungsprotokoll", gen_change_log),
]


class PreviewPage(QWidget):
    """
    Live documentation preview with section selector.
    Renders generated Markdown as styled HTML.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"background: {BG_SURFACE}; border-bottom: 1px solid {BORDER};")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(20, 8, 20, 8)

        title = QLabel("👁️  Dokumentations-Vorschau")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        hdr_lay.addWidget(title)
        hdr_lay.addStretch()

        lbl_section = QLabel("Abschnitt:")
        lbl_section.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        hdr_lay.addWidget(lbl_section)

        self.combo_section = QComboBox()
        self.combo_section.setFixedWidth(220)
        for _, label, _ in PREVIEW_SECTIONS:
            self.combo_section.addItem(label)
        self.combo_section.currentIndexChanged.connect(self._on_section_changed)
        hdr_lay.addWidget(self.combo_section)

        self.btn_all = QPushButton("📄  Alle Abschnitte")
        self.btn_all.clicked.connect(self._show_all)
        hdr_lay.addWidget(self.btn_all)

        layout.addWidget(hdr)

        # Splitter: rendered HTML | raw Markdown
        self.splitter = QSplitter(Qt.Horizontal)

        # HTML preview
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: none;
                padding: 20px;
                font-family: "{FONT_FAMILY}";
                font-size: 13px;
            }}
        """)
        self.splitter.addWidget(self.browser)

        # Raw markdown panel
        self.raw_view = QTextBrowser()
        self.raw_view.setFont(QFont("Cascadia Code, Consolas", 11))
        self.raw_view.setStyleSheet(f"""
            QTextBrowser {{
                background: {CODE_BG};
                color: {CODE_FG};
                border: none;
                padding: 16px;
            }}
        """)
        self.splitter.addWidget(self.raw_view)

        self.splitter.setSizes([600, 400])
        layout.addWidget(self.splitter)

        self._project: Project | None = None
        self._current_section = 0

    def set_project(self, project: Project):
        self._project = project
        self._render_current()

    def _on_section_changed(self, idx: int):
        self._current_section = idx
        self._render_current()

    def _render_current(self):
        if not self._project:
            self.browser.setHtml(f'<p style="color:{TEXT_MUTED};">Kein Projekt geladen.</p>')
            self.raw_view.setPlainText("")
            return
        _, _, gen_fn = PREVIEW_SECTIONS[self._current_section]
        md = gen_fn(self._project)
        self.raw_view.setPlainText(md)
        html = _md_to_html(md)
        full_html = f"""
        <html>
        <body style="background:{BG_SURFACE}; color:{TEXT_PRIMARY};
                     font-family:'{FONT_FAMILY}'; padding:8px; font-size:13px;">
        {html}
        </body>
        </html>
        """
        self.browser.setHtml(full_html)

    def _show_all(self):
        if not self._project:
            return
        all_md = []
        for _, label, gen_fn in PREVIEW_SECTIONS:
            all_md.append(gen_fn(self._project))
            all_md.append("\n\n---\n\n")
        combined = "\n".join(all_md)
        self.raw_view.setPlainText(combined)
        html = _md_to_html(combined)
        full_html = f"""
        <html>
        <body style="background:{BG_SURFACE}; color:{TEXT_PRIMARY};
                     font-family:'{FONT_FAMILY}'; padding:8px; font-size:13px;">
        {html}
        </body>
        </html>
        """
        self.browser.setHtml(full_html)

    def refresh(self):
        self._render_current()
