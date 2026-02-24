"""
GUI entry point – launches the PySide6 dark-mode application.

Run:  python -m src.gui
"""
try:
    from src.ui.mainwindow import run
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.ui.mainwindow import run

if __name__ == "__main__":
    run()

def main():
    run()
