"""Vert entry point with splash screen and Windows icon integration."""

import ctypes
import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.splash import SplashScreen
from ui.theme import ThemeMode, get_stylesheet

ROOT_DIR = Path(__file__).resolve().parent


def set_windows_app_id():
    """Ensure Windows taskbar pins and displays the custom Vert.ico icon properly."""
    if os.name == "nt":
        try:
            myappid = "HadoraWorks.Vert.FileConverter.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass


def main():
    set_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName("Vert")
    app.setOrganizationName("Hadora Works")

    # Set application icon (Vert.ico)
    ico_path = ROOT_DIR / "Vert.ico"
    if ico_path.exists():
        app_icon = QIcon(str(ico_path))
        app.setWindowIcon(app_icon)

    app.setStyleSheet(get_stylesheet(ThemeMode.DARK))

    # Show Hadora Works Splash Screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Create main window
    window = MainWindow()
    if ico_path.exists():
        window.setWindowIcon(QIcon(str(ico_path)))

    # Smooth transition from splash to main window
    def on_loaded():
        splash.advance_progress(100)
        app.processEvents()
        splash.close()
        window.show()

    QTimer.singleShot(1400, on_loaded)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
