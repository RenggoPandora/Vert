"""Main application window for Vert with iLovePDF-style Tools Hub and dedicated workflows."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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
from ui.hub_view import HubView
from ui.images_to_pdf_view import ImagesToPdfView
from ui.pdf_tools_view import PdfToolsView
from ui.queue_view import QueueView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vert — 100% Offline Desktop File Converter & PDF Suite")
        self.resize(1000, 700)
        self.setMinimumSize(880, 560)

        self._init_ui()
        self._update_engine_status()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 14, 16, 14)
        root_layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_row = QHBoxLayout()

        app_title = QLabel("VERT")
        app_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #10B981; letter-spacing: 1px;")

        badge = QLabel(" 100% OFFLINE ")
        badge.setStyleSheet(
            "background-color: #064E3B; color: #6EE7B7; border: 1px solid #059669; "
            "border-radius: 4px; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )

        title_row.addWidget(app_title)
        title_row.addWidget(badge)
        title_row.addStretch()

        subtitle = QLabel("Local File Converter & PDF Suite • Zero-Cloud • No File Caps")
        subtitle.setStyleSheet("color: #64748B; font-size: 12px;")

        title_box.addLayout(title_row)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Navigation buttons
        self.back_btn = QPushButton("← All Tools")
        self.back_btn.setStyleSheet(
            "background-color: #1E293B; color: #10B981; border: 1px solid #059669; font-weight: bold; padding: 6px 14px;"
        )
        self.back_btn.setVisible(False)
        self.back_btn.clicked.connect(self.show_hub)
        header_layout.addWidget(self.back_btn)

        root_layout.addLayout(header_layout)

        # Stacked views
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

        root_layout.addWidget(self.stack)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def show_hub(self):
        self.stack.setCurrentIndex(0)
        self.back_btn.setVisible(False)

    def _on_tool_selected(self, tool_id: str):
        self.back_btn.setVisible(True)

        if tool_id == "merge_pdf":
            self.pdf_tools_view.tabs.setCurrentIndex(0)
            self.stack.setCurrentWidget(self.pdf_tools_view)
        elif tool_id == "split_pdf":
            self.pdf_tools_view.tabs.setCurrentIndex(1)
            self.stack.setCurrentWidget(self.pdf_tools_view)
        elif tool_id == "images_to_pdf":
            self.stack.setCurrentWidget(self.images_to_pdf_view)
        else:
            # Universal batch, office to pdf, pdf to office, image converter, media, data
            self.stack.setCurrentWidget(self.queue_view)

    def _update_engine_status(self):
        lo_found = find_libreoffice_binary() is not None
        ffmpeg_found = find_ffmpeg_binary() is not None

        lo_text = "Office: Ready" if lo_found else "Office: System Fallback / Standby"
        ffmpeg_text = "Media (FFmpeg): Ready" if ffmpeg_found else "Media (FFmpeg): Optional / Standby"

        self.status_bar.showMessage(f"Engine Status: {lo_text} | {ffmpeg_text} | Network: Disabled (100% Local)")
