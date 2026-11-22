"""Main application window for Vert."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.media_converter import find_ffmpeg_binary
from core.office_converter import find_libreoffice_binary
from ui.pdf_tools_view import PdfToolsView
from ui.queue_view import QueueView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vert — 100% Offline Desktop File Converter")
        self.resize(920, 640)
        self.setMinimumSize(800, 520)

        self._init_ui()
        self._update_engine_status()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        # Header bar
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_row = QHBoxLayout()

        app_title = QLabel("VERT")
        app_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #10B981; letter-spacing: 1px;")

        badge = QLabel(" 100% OFFLINE ")
        badge.setStyleSheet(
            "background-color: #064E3B; color: #6EE7B7; border: 1px solid #059669; "
            "border-radius: 4px; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )

        title_row.addWidget(app_title)
        title_row.addWidget(badge)
        title_row.addStretch()

        subtitle = QLabel("Universal offline converter for Office documents, PDFs, images, media, and data")
        subtitle.setStyleSheet("color: #64748B; font-size: 12px;")

        title_box.addLayout(title_row)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        root_layout.addLayout(header_layout)

        # Tab Widget (Convert Queue vs. PDF Toolbox)
        self.tabs = QTabWidget()
        self.queue_view = QueueView()
        self.pdf_tools_view = PdfToolsView()

        self.tabs.addTab(self.queue_view, "File Converter")
        self.tabs.addTab(self.pdf_tools_view, "PDF Toolbox")

        root_layout.addWidget(self.tabs)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _update_engine_status(self):
        lo_found = find_libreoffice_binary() is not None
        ffmpeg_found = find_ffmpeg_binary() is not None

        lo_text = "Office: Ready" if lo_found else "Office: System Fallback / Standby"
        ffmpeg_text = "Media (FFmpeg): Ready" if ffmpeg_found else "Media (FFmpeg): Optional / Standby"

        self.status_bar.showMessage(f"Engine Status: {lo_text} | {ffmpeg_text} | Network: Disabled (100% Local)")
