"""Vert entry point with splash screen and Windows icon integration."""

import ctypes
import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.splash import SplashScreen, load_jakarta_font
from ui.theme import ThemeMode, get_stylesheet
from PySide6.QtGui import QFont

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

    # Load and register Plus Jakarta Sans globally as default app font
    font_family = load_jakarta_font()
    app.setFont(QFont(font_family, 10))

    # Set application icon (Vert.ico)
    ico_path = ROOT_DIR / "Vert.ico"
    if ico_path.exists():
        app_icon = QIcon(str(ico_path))
        app.setWindowIcon(app_icon)

    app.setStyleSheet(get_stylesheet(ThemeMode.DARK))

    # Show Hadora Works Splash Screen with smooth animation
    splash = SplashScreen()
    splash.show()

    # Create main window in background
    window = MainWindow()
    if ico_path.exists():
        window.setWindowIcon(QIcon(str(ico_path)))

    # Smooth transition: once splash animation completes, launch main window
    splash.ready_to_launch.connect(window.show)
    splash.start_animation(duration_ms=1200)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
