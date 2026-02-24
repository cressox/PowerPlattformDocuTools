"""
Reusable widgets for the PBI DocGen dark-mode GUI.

- CodeEditor:      syntax-highlighted text area for DAX / M / SQL, full Ctrl+V
- ScreenshotPanel: drag-drop / paste / browse for images, shows thumbnails
- Sidebar:         left navigation rail
- FormPage:        scrollable base for all editor pages
- ListEditorPage:  table + form combo for list sections
- Toast:           ephemeral feedback label in toolbar
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QScrollArea, QFrame, QFileDialog, QGroupBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QSizePolicy, QApplication,
)
from PySide6.QtCore import Qt, Signal, QMimeData, QTimer, QSize
from PySide6.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QColor,
    QImage, QPixmap, QDragEnterEvent, QDropEvent, QKeyEvent,
)
import re

from .theme import *

SCREENSHOTS_DIR = Path("data") / "screenshots"


# ══════════════════════════════════════════════════════════════════
# CODE EDITOR  with syntax highlighting + Ctrl+V support
# ══════════════════════════════════════════════════════════════════

class _DAXHighlighter(QSyntaxHighlighter):
    """Simple DAX / M / SQL keyword highlighter."""

    KEYWORDS = (
        "CALCULATE|FILTER|ALL|ALLEXCEPT|VALUES|DISTINCT|SUMMARIZE|ADDCOLUMNS|"
        "SELECTCOLUMNS|TOPN|RANKX|COUNTROWS|SUMX|AVERAGEX|MAXX|MINX|"
        "IF|SWITCH|DIVIDE|BLANK|ISBLANK|FORMAT|RELATED|RELATEDTABLE|"
        "DATEADD|DATESYTD|DATESQTD|DATESMTD|SAMEPERIODLASTYEAR|"
        "PARALLELPERIOD|TOTALYTD|TOTALQTD|TOTALMTD|"
        "SUM|AVERAGE|MIN|MAX|COUNT|COUNTA|DISTINCTCOUNT|"
        "VAR|RETURN|TRUE|FALSE|IN|NOT|AND|OR|"
        "let|in|each|if|then|else|true|false|null|"
        "Table\\.SelectRows|Table\\.AddColumn|Table\\.TransformColumnTypes|"
        "Table\\.FromList|List\\.Dates|Date\\.Year|Date\\.Month|Date\\.WeekOfYear|"
        "Source|Sql\\.Database|SapHana\\.Database|Excel\\.Workbook|"
        "SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AS|"
        "GROUP BY|ORDER BY|HAVING|UNION|INSERT|UPDATE|DELETE|CREATE"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # Keywords
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor(CODE_KEYWORD))
        kw_fmt.setFontWeight(QFont.Bold)
        for word in self.KEYWORDS.split("|"):
            pattern = rf"\b{re.escape(word)}\b"
            self._rules.append((re.compile(pattern, re.IGNORECASE), kw_fmt))

        # Strings
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor(CODE_STRING))
        self._rules.append((re.compile(r'"[^"]*"'), str_fmt))
        self._rules.append((re.compile(r"'[^']*'"), str_fmt))

        # Numbers
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#F78C6C"))
        self._rules.append((re.compile(r"\b\d+\.?\d*\b"), num_fmt))

        # Comments (// and /* */)
        cmt_fmt = QTextCharFormat()
        cmt_fmt.setForeground(QColor(CODE_COMMENT))
        cmt_fmt.setFontItalic(True)
        self._rules.append((re.compile(r"//[^\n]*"), cmt_fmt))
        self._rules.append((re.compile(r"/\*.*?\*/", re.DOTALL), cmt_fmt))

        # Functions (word followed by open paren)
        fn_fmt = QTextCharFormat()
        fn_fmt.setForeground(QColor("#82AAFF"))
        self._rules.append((re.compile(r"\b[A-Za-z_]\w*(?=\s*\()"), fn_fmt))

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class CodeEditor(QTextEdit):
    """
    Dark code editor with:
    - DAX/M syntax highlighting
    - Monospace font
    - Full Ctrl+V paste support
    - Line-number-ish left padding
    - Tab = 4 spaces
    """

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        font = QFont("Cascadia Code, Consolas, Courier New", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {CODE_BG};
                color: {CODE_FG};
                border: 1px solid {BORDER};
                border-radius: {RADIUS_SM};
                padding: 10px;
                selection-background-color: {BG_SELECTED};
            }}
            QTextEdit:focus {{
                border-color: {BORDER_FOCUS};
            }}
        """)
        self.setPlaceholderText(placeholder)
        self.setTabStopDistance(32)  # 4 chars
        self.setAcceptRichText(False)
        self._highlighter = _DAXHighlighter(self.document())

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return
        super().keyPressEvent(e)


# ══════════════════════════════════════════════════════════════════
# SCREENSHOT PANEL  – browse / paste / drop images
# ══════════════════════════════════════════════════════════════════

class ScreenshotPanel(QWidget):
    """
    A panel for attaching screenshots.
    - Browse button to pick files
    - Ctrl+V to paste from clipboard
    - Drag & drop image files
    - Shows thumbnails with captions
    - Stores copies in data/screenshots/
    """
    screenshots_changed = Signal()

    def __init__(self, section_id: str = "general", parent=None):
        super().__init__(parent)
        self.section_id = section_id
        self._images: list[dict] = []  # [{filename, caption, pixmap}]

        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header row
        hdr = QHBoxLayout()
        lbl = QLabel("📷 Screenshots")
        lbl.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {ACCENT};")
        hdr.addWidget(lbl)
        hdr.addStretch()

        self.btn_browse = QPushButton("📂 Bild wählen …")
        self.btn_browse.setFixedHeight(30)
        self.btn_browse.clicked.connect(self._browse)
        hdr.addWidget(self.btn_browse)

        self.btn_paste = QPushButton("📋 Aus Zwischenablage")
        self.btn_paste.setFixedHeight(30)
        self.btn_paste.setToolTip("Strg+V funktioniert auch!")
        self.btn_paste.clicked.connect(self._paste_clipboard)
        hdr.addWidget(self.btn_paste)
        layout.addLayout(hdr)

        # Hint label
        self.hint = QLabel("Bilder hierher ziehen oder Strg+V zum Einfügen")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet(f"""
            color: {TEXT_MUTED};
            border: 2px dashed {BORDER};
            border-radius: {RADIUS_LG};
            padding: 16px;
            font-size: 12px;
        """)
        self.hint.setMinimumHeight(60)
        layout.addWidget(self.hint)

        # Thumbnail area
        self.thumb_area = QWidget()
        self.thumb_layout = QHBoxLayout(self.thumb_area)
        self.thumb_layout.setContentsMargins(0, 0, 0, 0)
        self.thumb_layout.setSpacing(8)
        self.thumb_layout.addStretch()
        layout.addWidget(self.thumb_area)

    def keyPressEvent(self, e: QKeyEvent):
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_V:
            self._paste_clipboard()
            return
        super().keyPressEvent(e)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls() or e.mimeData().hasImage():
            e.acceptProposedAction()
            self.hint.setStyleSheet(f"""
                color: {ACCENT};
                border: 2px dashed {ACCENT};
                border-radius: {RADIUS_LG};
                padding: 16px;
                font-size: 12px;
                background: {BG_SELECTED};
            """)

    def dragLeaveEvent(self, e):
        self.hint.setStyleSheet(f"""
            color: {TEXT_MUTED};
            border: 2px dashed {BORDER};
            border-radius: {RADIUS_LG};
            padding: 16px;
            font-size: 12px;
        """)

    def dropEvent(self, e: QDropEvent):
        self.hint.setStyleSheet(f"""
            color: {TEXT_MUTED};
            border: 2px dashed {BORDER};
            border-radius: {RADIUS_LG};
            padding: 16px;
            font-size: 12px;
        """)
        if e.mimeData().hasImage():
            img = QImage(e.mimeData().imageData())
            self._add_image_from_qimage(img)
        elif e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                path = url.toLocalFile()
                if path and path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
                    self._add_image_from_file(Path(path))

    def _browse(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Screenshots auswählen", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Alle Dateien (*)"
        )
        for p in paths:
            self._add_image_from_file(Path(p))

    def _paste_clipboard(self):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            img = QImage(mime.imageData())
            if not img.isNull():
                self._add_image_from_qimage(img)
                return
        if mime.hasUrls():
            for url in mime.urls():
                p = url.toLocalFile()
                if p and p.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
                    self._add_image_from_file(Path(p))
                    return
        QMessageBox.information(self, "Zwischenablage", "Kein Bild in der Zwischenablage gefunden.")

    def _save_to_screenshots_dir(self, source_path: Optional[Path] = None,
                                   qimage: Optional[QImage] = None) -> str:
        """Copy or save image to data/screenshots/. Returns relative filename."""
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        uid = uuid.uuid4().hex[:8]
        if source_path:
            ext = source_path.suffix or ".png"
            dest_name = f"{self.section_id}_{uid}{ext}"
            dest = SCREENSHOTS_DIR / dest_name
            shutil.copy2(source_path, dest)
        elif qimage:
            dest_name = f"{self.section_id}_{uid}.png"
            dest = SCREENSHOTS_DIR / dest_name
            qimage.save(str(dest))
        else:
            return ""
        return dest_name

    def _add_image_from_file(self, path: Path):
        filename = self._save_to_screenshots_dir(source_path=path)
        pixmap = QPixmap(str(path)).scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._add_thumb(filename, pixmap)

    def _add_image_from_qimage(self, img: QImage):
        filename = self._save_to_screenshots_dir(qimage=img)
        pixmap = QPixmap.fromImage(img).scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._add_thumb(filename, pixmap)

    def _add_thumb(self, filename: str, pixmap: QPixmap):
        self._images.append({"filename": filename, "caption": "", "pixmap": pixmap})

        card = QWidget()
        card.setFixedSize(130, 120)
        card.setStyleSheet(f"""
            QWidget {{
                background: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: {RADIUS_SM};
            }}
        """)
        clayout = QVBoxLayout(card)
        clayout.setContentsMargins(4, 4, 4, 4)
        clayout.setSpacing(2)

        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        clayout.addWidget(img_label)

        name_label = QLabel(filename[:18] + "…" if len(filename) > 18 else filename)
        name_label.setStyleSheet(f"font-size: 10px; color: {TEXT_SECONDARY}; background: transparent;")
        name_label.setAlignment(Qt.AlignCenter)
        clayout.addWidget(name_label)

        # Remove button
        idx = len(self._images) - 1
        btn_rm = QPushButton("✕")
        btn_rm.setFixedSize(20, 20)
        btn_rm.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER_BG};
                color: {DANGER};
                border: none;
                border-radius: 10px;
                font-size: 11px;
                padding: 0;
            }}
            QPushButton:hover {{ background: {DANGER}; color: white; }}
        """)
        btn_rm.clicked.connect(lambda checked, i=idx, w=card: self._remove_thumb(i, w))
        # Overlay the remove button
        btn_rm.setParent(card)
        btn_rm.move(106, 2)
        btn_rm.raise_()

        # Insert before the stretch
        self.thumb_layout.insertWidget(self.thumb_layout.count() - 1, card)
        self.hint.hide()
        self.screenshots_changed.emit()

    def _remove_thumb(self, idx: int, widget: QWidget):
        if idx < len(self._images):
            # Remove file
            fn = self._images[idx]["filename"]
            fpath = SCREENSHOTS_DIR / fn
            if fpath.exists():
                fpath.unlink()
            self._images[idx] = None  # mark removed
        widget.setParent(None)
        widget.deleteLater()
        if all(x is None for x in self._images):
            self.hint.show()
        self.screenshots_changed.emit()

    def get_filenames(self) -> list[str]:
        return [img["filename"] for img in self._images if img is not None]

    def load_filenames(self, filenames: list[str]):
        """Load existing screenshot references."""
        for fn in filenames:
            fpath = SCREENSHOTS_DIR / fn
            if fpath.exists():
                pixmap = QPixmap(str(fpath)).scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._add_thumb(fn, pixmap)


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════

class Sidebar(QWidget):
    nav_clicked = Signal(int)

    ITEMS = [
        ("🏠", "Dashboard"),
        ("📋", "Metadaten"),
        ("🎨", "CI / Branding"),
        ("🎯", "KPIs"),
        ("🗄️", "Datenquellen"),
        ("⚙️", "Power Query"),
        ("🔗", "Datenmodell"),
        ("📐", "Measures"),
        ("📊", "Berichtsseiten"),
        ("🛡️", "Governance"),
        ("📝", "Änderungen"),
        ("�", "Berechtigungen"),
        ("📁", "Ablagestruktur"),
        ("🏷️", "Namenskonzept"),
        ("🔄", "Änderungshinweise"),
        ("�👁️", "Vorschau"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_W)
        self.setStyleSheet(f"background: {BG_ELEVATED};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("  ⚡ PBI DocGen")
        logo.setStyleSheet(f"""
            color: {PBI_YELLOW};
            font-size: 17px;
            font-weight: 700;
            padding: 18px 14px 14px 14px;
            background: transparent;
        """)
        layout.addWidget(logo)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        layout.addWidget(sep)

        self._buttons: list[QPushButton] = []
        for idx, (icon, label) in enumerate(self.ITEMS):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setStyleSheet(self._btn_style(False))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda checked, i=idx: self._on_click(i))
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()

        ver = QLabel("  v3.0 Dark")
        ver.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 12px; background: transparent;")
        layout.addWidget(ver)

    def _btn_style(self, selected: bool) -> str:
        if selected:
            return f"""
                QPushButton {{
                    text-align: left; border: none; border-radius: 0;
                    color: {TEXT_BEIGE}; padding: 0 14px; font-size: 13px;
                    background: {BG_SELECTED};
                    border-left: 3px solid {ACCENT};
                    font-weight: 600;
                }}
            """
        return f"""
            QPushButton {{
                text-align: left; border: none; border-radius: 0;
                color: {TEXT_BEIGE}; padding: 0 14px; font-size: 13px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: {TEXT_BEIGE};
            }}
        """

    def _on_click(self, idx: int):
        self.nav_clicked.emit(idx)
        self.select(idx)

    def select(self, idx: int):
        for i, btn in enumerate(self._buttons):
            btn.setStyleSheet(self._btn_style(i == idx))


# ══════════════════════════════════════════════════════════════════
# FORM PAGE BASE
# ══════════════════════════════════════════════════════════════════

class FormPage(QScrollArea):
    """Base scrollable page with title/subtitle helpers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(28, 24, 28, 24)
        self._layout.setSpacing(14)
        self.setWidget(self._container)

    def add_title(self, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY};")
        self._layout.addWidget(lbl)

    def add_subtitle(self, text: str):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; margin-bottom: 4px;")
        self._layout.addWidget(lbl)

    def add_separator(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        self._layout.addWidget(sep)


# ══════════════════════════════════════════════════════════════════
# LIST EDITOR PAGE
# ══════════════════════════════════════════════════════════════════

class ListEditorPage(FormPage):
    """
    Reusable page: table at top, form below, add/edit/delete buttons.
    Subclasses override form building and data marshalling.
    """
    changed = Signal()

    def __init__(self, title: str, subtitle: str, columns: list[str], parent=None):
        super().__init__(parent)
        self.add_title(title)
        self.add_subtitle(subtitle)
        self._columns = columns

        # Table
        self.table = QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMaximumHeight(220)
        self.table.verticalHeader().setVisible(False)
        self._layout.addWidget(self.table)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("➕  Hinzufügen")
        self.btn_add.setObjectName("primary")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_edit = QPushButton("✏️  Übernehmen")
        self.btn_edit.setObjectName("success")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_del = QPushButton("🗑️  Löschen")
        self.btn_del.setObjectName("danger")
        self.btn_del.setCursor(Qt.PointingHandCursor)
        self.btn_clear = QPushButton("🧹  Leeren")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_form)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_del)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        self._layout.addLayout(btn_row)

        # Form area
        self.form_group = QGroupBox("Details")
        self.form_layout = QFormLayout(self.form_group)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self._build_form(self.form_layout)
        self._layout.addWidget(self.form_group)
        self._layout.addStretch()
        self._editing_row: int = -1

    def _build_form(self, form: QFormLayout): pass
    def _clear_form(self): pass
    def _validate(self) -> Optional[str]: return None

    def load_items(self, items: list):
        self.table.setRowCount(0)
        for item in items:
            row_data = self._item_to_row(item)
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row_data):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
        self._editing_row = -1
        self._clear_form()

    def _item_to_row(self, item) -> list[str]:
        return []
