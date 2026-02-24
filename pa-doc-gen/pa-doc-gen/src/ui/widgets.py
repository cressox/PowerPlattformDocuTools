"""
ui/widgets.py – Wiederverwendbare Widgets fuer die GUI.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal, QTimer, QMimeData, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QIcon,
    QDragEnterEvent, QDropEvent, QKeyEvent, QPixmap, QImage, QPainter,
    QClipboard,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
    QFormLayout, QScrollArea, QFrame, QSplitter, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QGraphicsOpacityEffect,
    QApplication, QSizePolicy, QGridLayout, QGroupBox, QCheckBox,
)

from ui.theme import (
    BG_BASE, BG_CARD, BG_INPUT, BG_SIDEBAR, ACCENT, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, ERROR,
    SIDEBAR_SELECTED, SIDEBAR_HOVER,
)

import re

SCREENSHOT_DIR = Path("data/screenshots")


# ===========================================================================
# Sidebar
# ===========================================================================

class SidebarItem(QPushButton):
    """Ein einzelner Sidebar-Eintrag."""
    def __init__(self, text: str, icon_char: str = "", parent=None):
        super().__init__(parent)
        label = f"  {icon_char}   {text}" if icon_char else f"  {text}"
        self.setText(label)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                text-align: left;
                padding-left: 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {SIDEBAR_HOVER};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {SIDEBAR_SELECTED};
                color: {ACCENT};
                border-left: 3px solid {ACCENT};
                font-weight: bold;
            }}
        """)


class Sidebar(QWidget):
    """Sidebar-Navigation."""
    page_changed = Signal(int)

    PAGES = [
        ("📊", "Dashboard"),        ("🗂️", "Solution"),        ("📋", "Metadaten"),
        ("🎨", "CI / Branding"),
        ("⚡", "Trigger"),
        ("�", "Flussdiagramm"),
        ("�🔧", "Aktionen"),
        ("🔌", "Konnektoren"),
        ("📦", "Variablen"),
        ("🛡️", "Fehlerbehandlung"),
        ("🔗", "Datenmappings"),
        ("📈", "SLA & Performance"),
        ("🏛️", "Governance"),
        ("🔀", "Abhaengigkeiten"),
        ("📝", "Aenderungen"),
        ("👁️", "Vorschau"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {BG_SIDEBAR}; border-right: 1px solid {BORDER};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(2)

        # Header
        title = QLabel("PA Doc Gen")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 18px; font-weight: bold; padding: 8px 12px;")
        layout.addWidget(title)
        subtitle = QLabel("Flow-Dokumentation")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 0 12px 12px;")
        layout.addWidget(subtitle)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        self.buttons: list[SidebarItem] = []
        for icon, text in self.PAGES:
            btn = SidebarItem(text, icon)
            btn.clicked.connect(self._on_click)
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # Version
        ver = QLabel("v1.0.0")
        ver.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; padding: 4px 12px;")
        layout.addWidget(ver)

        # Select first by default
        if self.buttons:
            self.buttons[0].setChecked(True)

    def _on_click(self):
        sender = self.sender()
        for i, btn in enumerate(self.buttons):
            if btn is sender:
                btn.setChecked(True)
                self.page_changed.emit(i)
            else:
                btn.setChecked(False)

    def select_page(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)


# ===========================================================================
# Toast-Benachrichtigung
# ===========================================================================

class Toast(QLabel):
    """Temporaere Benachrichtigung (Toast)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            background-color: {SUCCESS};
            color: white;
            border-radius: 6px;
            padding: 6px 20px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.hide()

    def show_message(self, text: str, msg_type: str = "success", duration: int = 2500):
        colors_map = {"success": SUCCESS, "warning": WARNING, "error": ERROR, "info": ACCENT}
        bg = colors_map.get(msg_type, SUCCESS)
        self.setStyleSheet(f"""
            background-color: {bg};
            color: white;
            border-radius: 6px;
            padding: 6px 20px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.setText(text)
        self.adjustSize()
        # Position zentriert oben im Parent
        if self.parent():
            pw = self.parent().width()
            self.move((pw - self.width()) // 2, 10)
        self.show()
        QTimer.singleShot(duration, self.hide)


# ===========================================================================
# Code-Editor mit Syntax-Highlighting
# ===========================================================================

class JsonHighlighter(QSyntaxHighlighter):
    """Syntax-Highlighting fuer JSON und PA-Expressions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        # Strings
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#CE9178"))
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', fmt))

        # Numbers
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#B5CEA8"))
        self.rules.append((r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b', fmt))

        # Keywords
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#569CD6"))
        self.rules.append((r'\b(true|false|null)\b', fmt))

        # Keys
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#9CDCFE"))
        self.rules.append((r'"[^"]+"\s*:', fmt))

        # PA Expressions @{...}
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#DCDCAA"))
        fmt.setFontWeight(QFont.Bold)
        self.rules.append((r'@\{[^}]+\}', fmt))

        # Braces
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#D4D4D4"))
        self.rules.append((r'[\{\}\[\]]', fmt))

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class CodeEditor(QPlainTextEdit):
    """Code-Editor mit Syntax-Highlighting, Zeilennummern und Strg+V."""

    def __init__(self, parent=None, language: str = "json"):
        super().__init__(parent)
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(28)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {BG_INPUT};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
        """)

        if language in ("json", "expression"):
            self._highlighter = JsonHighlighter(self.document())

    def keyPressEvent(self, event: QKeyEvent):
        # Strg+V: mehrzeiliger Paste
        super().keyPressEvent(event)


# ===========================================================================
# Screenshot-Panel
# ===========================================================================

class ScreenshotPanel(QWidget):
    """Screenshot-Widget mit Drag & Drop, Strg+V und Dateibrowser."""
    screenshot_added = Signal(str)  # Emits filename

    def __init__(self, section: str = "", parent=None):
        super().__init__(parent)
        self.section = section
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.drop_area = QLabel("Screenshot hier ablegen, einfuegen (Strg+V) oder Datei waehlen")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setMinimumHeight(80)
        self.drop_area.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {BORDER};
                border-radius: 6px;
                color: {TEXT_MUTED};
                background-color: {BG_CARD};
                padding: 16px;
            }}
        """)
        layout.addWidget(self.drop_area)

        btn_row = QHBoxLayout()
        self.btn_browse = QPushButton("Datei waehlen …")
        self.btn_browse.setProperty("class", "secondary")
        self.btn_browse.clicked.connect(self._browse)
        btn_row.addWidget(self.btn_browse)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.hide()
        layout.addWidget(self.preview_label)

    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeyEvent.Paste) or (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V):
            self._paste_from_clipboard()
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        if mime.hasImage():
            img = QImage(mime.imageData())
            self._save_image(img)
        elif mime.hasUrls():
            for url in mime.urls():
                path = url.toLocalFile()
                if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    self._copy_file(path)

    def _paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        img = clipboard.image()
        if not img.isNull():
            self._save_image(img)
        elif clipboard.mimeData().hasUrls():
            for url in clipboard.mimeData().urls():
                path = url.toLocalFile()
                if path:
                    self._copy_file(path)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Screenshot waehlen", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif);;Alle Dateien (*)"
        )
        if path:
            self._copy_file(path)

    def _save_image(self, img: QImage):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        import time
        fname = f"screenshot_{self.section}_{int(time.time())}.png"
        fpath = SCREENSHOT_DIR / fname
        img.save(str(fpath))
        self._show_preview(fpath)
        self.screenshot_added.emit(fname)

    def _copy_file(self, src: str):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        fname = Path(src).name
        dst = SCREENSHOT_DIR / fname
        if str(Path(src).resolve()) != str(dst.resolve()):
            shutil.copy2(src, dst)
        self._show_preview(dst)
        self.screenshot_added.emit(fname)

    def _show_preview(self, path: Path):
        pix = QPixmap(str(path))
        if not pix.isNull():
            scaled = pix.scaledToWidth(min(300, pix.width()), Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)
            self.preview_label.show()


# ===========================================================================
# FormPage – Basis fuer Formularseiten
# ===========================================================================

class FormPage(QScrollArea):
    """Scrollbare Seite mit Titel und Formular."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(12)

        # Titel
        lbl = QLabel(title)
        lbl.setProperty("class", "section-title")
        self._layout.addWidget(lbl)

        self.setWidget(container)

    def add_widget(self, w: QWidget):
        self._layout.addWidget(w)

    def add_form_row(self, label: str, widget: QWidget) -> QWidget:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(180)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY};")
        row.addWidget(lbl)
        row.addWidget(widget)
        wrapper = QWidget()
        wrapper.setLayout(row)
        self._layout.addWidget(wrapper)
        return widget

    def add_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        self._layout.addWidget(sep)

    def add_stretch(self):
        self._layout.addStretch()

    def add_group(self, title: str) -> QVBoxLayout:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        self._layout.addWidget(group)
        return layout


# ===========================================================================
# Card Widget
# ===========================================================================

class Card(QFrame):
    """Karten-Widget mit Titel und Inhalt."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            Card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet(f"color: {ACCENT}; font-size: 14px; font-weight: bold;")
            self._layout.addWidget(lbl)

    def add_widget(self, w: QWidget):
        self._layout.addWidget(w)

    def layout(self):
        return self._layout


# ===========================================================================
# StatCard fuer Dashboard
# ===========================================================================

class StatCard(QFrame):
    """Statistik-Karte fuer das Dashboard."""

    def __init__(self, label: str, value: str = "0", color: str = ACCENT, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 90)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold;")
        layout.addWidget(self.value_label)

        desc = QLabel(label)
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(desc)

    def set_value(self, val):
        self.value_label.setText(str(val))
