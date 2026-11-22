"""Main application window for Vert with responsive views and dual-theme switcher."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from core.media_converter import find_ffmpeg_binary
from core.office_converter import find_libreoffice_binary
from core.updater import UpdateCheckTask
from core.version import GITHUB_REPO, __version__
from ui.hub_view import HubView
from ui.icons import get_icon, get_pixmap
from ui.images_to_pdf_view import ImagesToPdfView
from ui.pdf_tools_view import PdfToolsView
from ui.queue_view import QueueView
from ui.theme import ThemeMode, get_stylesheet
import webbrowser
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vert — 100% Offline Desktop File Converter & PDF Suite")
        self.resize(1000, 700)
        self.setMinimumSize(780, 520)

        self.current_theme = ThemeMode.DARK

        self._init_ui()
        self._apply_theme()
        self._update_engine_status()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 12, 16, 12)
        root_layout.setSpacing(10)

        # Header Bar
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_row = QHBoxLayout()

        app_title = QLabel("VERT")
        app_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #2563EB; letter-spacing: 1.5px;")

        badge = QLabel(" 100% OFFLINE ")
        badge.setStyleSheet(
            "background-color: transparent; color: #2563EB; border: 1.5px solid #2563EB; "
            "border-radius: 4px; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )

        title_row.addWidget(app_title)
        title_row.addWidget(badge)
        title_row.addStretch()

        subtitle = QLabel("Local File Converter & PDF Suite • Zero-Cloud • Free & Fast")
        subtitle.setStyleSheet("color: #64748B; font-size: 12px;")

        title_box.addLayout(title_row)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Navigation: Back button
        self.back_btn = QPushButton(" All Tools")
        self.back_btn.setIcon(get_icon("arrow_left", color="#2563EB", size=16))
        self.back_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 6px 14px; border-radius: 6px; } "
            "QPushButton:hover { color: #2563EB; }"
        )
        self.back_btn.setVisible(False)
        self.back_btn.clicked.connect(self.show_hub)
        header_layout.addWidget(self.back_btn)

        # Update Checker Button
        self.update_btn = QPushButton("Check for Updates")
        self.update_btn.setToolTip("Check GitHub for the latest release")
        self.update_btn.clicked.connect(self.check_for_updates)
        header_layout.addWidget(self.update_btn)

        # Theme Switcher Button
        self.theme_btn = QPushButton()
        self.theme_btn.setToolTip("Toggle Light / Dark Mode")
        self.theme_btn.setFixedSize(38, 38)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        root_layout.addLayout(header_layout)

        # Stacked Views
        self.stack = QStackedWidget()

        # View 0: Tools Hub
        self.hub_view = HubView()
        self.hub_view.tool_selected.connect(self._on_tool_selected)
        self.stack.addWidget(self.hub_view)

        # View 1: Universal 1:1 Batch Converter
        self.queue_view = QueueView()
        self.stack.addWidget(self.queue_view)

        # View 2: PDF Toolbox (Merge & Split)
        self.pdf_tools_view = PdfToolsView()
        self.stack.addWidget(self.pdf_tools_view)

        # View 3: Images to PDF
        self.images_to_pdf_view = ImagesToPdfView()
        self.stack.addWidget(self.images_to_pdf_view)

        root_layout.addWidget(self.stack, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def toggle_theme(self):
        self.current_theme = (
            ThemeMode.LIGHT if self.current_theme == ThemeMode.DARK else ThemeMode.DARK
        )
        self._apply_theme()

    def _apply_theme(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(self.current_theme))

        # Update Theme Toggle Icon
        if self.current_theme == ThemeMode.DARK:
            self.theme_btn.setIcon(get_icon("theme_sun", color="#F59E0B", size=20))
            self.theme_btn.setToolTip("Switch to Light Theme")
        else:
            self.theme_btn.setIcon(get_icon("theme_moon", color="#2563EB", size=20))
            self.theme_btn.setToolTip("Switch to Dark Theme")

    def show_hub(self):
        self.stack.setCurrentIndex(0)
        self.back_btn.setVisible(False)

    def _on_tool_selected(self, tool_id: str):
        self.back_btn.setVisible(True)

        if tool_id == "merge_pdf":
            self.pdf_tools_view.tabs.setCurrentIndex(1)
            self.stack.setCurrentWidget(self.pdf_tools_view)
        elif tool_id == "split_pdf":
            self.pdf_tools_view.tabs.setCurrentIndex(0)
            self.stack.setCurrentWidget(self.pdf_tools_view)
        elif tool_id == "images_to_pdf":
            self.stack.setCurrentWidget(self.images_to_pdf_view)
        else:
            self.stack.setCurrentWidget(self.queue_view)

    def check_for_updates(self):
        self.update_btn.setEnabled(False)
        self.update_btn.setText("Checking...")

        task = UpdateCheckTask()
        task.signals.checked.connect(self._on_update_checked)
        task.signals.failed.connect(self._on_update_failed)
        QThreadPool.globalInstance().start(task)

    def _on_update_checked(self, has_update: bool, tag: str, url: str, body: str):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("Check for Updates")

        if has_update:
            notes = f"\n\nRelease Notes:\n{body[:300]}..." if body else ""
            reply = QMessageBox.information(
                self,
                "Update Available!",
                f"A new version of Vert ({tag}) is available!\n"
                f"Your current version: v{__version__}{notes}\n\n"
                f"Would you like to open the download page?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                webbrowser.open(url)
        else:
            QMessageBox.information(
                self,
                "Up to Date",
                f"You are running the latest version of Vert (v{__version__})!",
            )

    def _on_update_failed(self, err_msg: str):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("Check for Updates")
        QMessageBox.warning(
            self,
            "Update Check Failed",
            f"Could not connect to GitHub to check for updates.\n"
            f"Please ensure internet access is available and try again.\n\nDetails: {err_msg}",
        )

    def _update_engine_status(self):
        lo_found = find_libreoffice_binary() is not None
        ffmpeg_found = find_ffmpeg_binary() is not None

        lo_text = "Office: Ready" if lo_found else "Office: System Fallback / Standby"
        ffmpeg_text = "Media (FFmpeg): Ready" if ffmpeg_found else "Media (FFmpeg): Standby"

        self.status_bar.showMessage(
            f"Engine Status: {lo_text} | {ffmpeg_text} | Network: Disabled (100% Local)"
        )
