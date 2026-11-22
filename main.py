"""Vert entry point."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import ThemeMode, get_stylesheet

ROOT_DIR = Path(__file__).resolve().parent


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vert")
    app.setOrganizationName("Vert")

    app.setStyleSheet(get_stylesheet(ThemeMode.DARK))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
