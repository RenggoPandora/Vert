"""Vert entry point."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

ROOT_DIR = Path(__file__).resolve().parent


def load_stylesheet() -> str:
    qss_path = ROOT_DIR / "ui" / "styles.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vert")
    app.setOrganizationName("Vert")

    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
