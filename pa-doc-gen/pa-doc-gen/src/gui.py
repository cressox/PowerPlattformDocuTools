#!/usr/bin/env python3
"""
gui.py – Entry Point fuer den Power Automate Documentation Generator.
"""
import sys
import os

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.theme import apply_theme
from ui.mainwindow import MainWindow


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("PA Doc Gen")
    app.setOrganizationName("PADocGen")

    apply_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
