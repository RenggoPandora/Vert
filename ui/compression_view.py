"""Advanced File Compression View for Vert with Target-Size Optimization and output directory picker."""

import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.compression.base import (
    CompressionCategory,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
    format_bytes_human,
)
from core.compression.inspector import FileMetadata, inspect_file
from core.compression.optimizer import compress_file, find_adapter
from core.compression.worker import CompressionTask
from ui.icons import get_icon, get_pixmap


class CompressionDropZone(QFrame):
    files_selected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("audioDropZone")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_pixmap("file_compression", color="#059669", size=32))
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("Click to select or drop files here to compress")
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel("Supports Images (JPG, PNG, WebP), PDFs, Videos (MP4), and ZIP Archives")
        self.hint_label.setStyleSheet("color: #64748B; font-size: 11px;")
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files to Compress",
                "",
                "Compressible Files (*.jpg *.jpeg *.png *.webp *.pdf *.mp4 *.mkv *.zip);;All Files (*.*)",
            )
            if files:
                self.files_selected.emit([Path(f) for f in files])

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.is_file() and find_adapter(p):
                paths.append(p)
        if paths:
            self.files_selected.emit(paths)
            event.acceptProposedAction()


class CompressionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_meta: Optional[FileMetadata] = None
        self.custom_output_dir: Optional[Path] = None
        self.current_task: Optional[CompressionTask] = None
        self.last_result: Optional[CompressionResult] = None

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 8, 12, 12)
        root_layout.setSpacing(10)

        # Header Title Bar
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap("file_compression", color="#059669", size=24))
        title_lbl = QLabel("Advanced File Compression")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        badge = QLabel(" Target-Size Optimizer • 100% Offline ")
        badge.setStyleSheet(
            "color: #059669; border: 1.5px solid #059669; border-radius: 4px; "
            "font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addWidget(badge)
        header.addStretch()
        root_layout.addLayout(header)

        # Scroll Area for clean layout across small resolutions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Drop Zone
        self.drop_zone = CompressionDropZone()
        self.drop_zone.files_selected.connect(self._on_files_selected)
        content_layout.addWidget(self.drop_zone)

        # File Metadata Card
        self.meta_frame = QFrame()
        self.meta_frame.setObjectName("toolCard")
        meta_layout = QVBoxLayout(self.meta_frame)
        meta_layout.setContentsMargins(12, 10, 12, 10)

        self.file_name_lbl = QLabel("No file selected.")
        self.file_name_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.file_details_lbl = QLabel("Drag or select a file above to view metadata and compression options.")
        self.file_details_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        meta_layout.addWidget(self.file_name_lbl)
        meta_layout.addWidget(self.file_details_lbl)
        content_layout.addWidget(self.meta_frame)

        # Compression Settings Card
        self.settings_frame = QFrame()
        self.settings_frame.setObjectName("toolCard")
        settings_layout = QVBoxLayout(self.settings_frame)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(12)

        st_title = QLabel("Compression Strategy & Target Size")
        st_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        settings_layout.addWidget(st_title)

        # Target Size Options
        mode_box = QHBoxLayout()
        mode_box.setSpacing(16)

        self.radio_preset_25 = QRadioButton("Reduce by 25%")
        self.radio_preset_50 = QRadioButton("Reduce by 50% (Recommended)")
        self.radio_preset_50.setChecked(True)
        self.radio_preset_75 = QRadioButton("Reduce by 75% (Maximum)")
        self.radio_custom = QRadioButton("Custom Target:")

        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.radio_preset_25)
        self.btn_group.addButton(self.radio_preset_50)
        self.btn_group.addButton(self.radio_preset_75)
        self.btn_group.addButton(self.radio_custom)

        mode_box.addWidget(self.radio_preset_25)
        mode_box.addWidget(self.radio_preset_50)
        mode_box.addWidget(self.radio_preset_75)
        mode_box.addWidget(self.radio_custom)

        # Custom size inputs
        self.custom_size_spin = QSpinBox()
        self.custom_size_spin.setRange(1, 100000)
        self.custom_size_spin.setValue(500)
        self.custom_size_spin.setEnabled(False)
        self.custom_unit_combo = QComboBox()
        self.custom_unit_combo.addItems(["KB", "MB"])
        self.custom_unit_combo.setEnabled(False)

        self.radio_custom.toggled.connect(self._on_custom_toggled)

        mode_box.addWidget(self.custom_size_spin)
        mode_box.addWidget(self.custom_unit_combo)
        mode_box.addStretch()
        settings_layout.addLayout(mode_box)

        # Format-specific tuning row
        tuning_row = QHBoxLayout()
        tuning_row.setSpacing(14)

        # Resolution scale slider
        res_box = QVBoxLayout()
        self.res_lbl = QLabel("Resolution Scale: 100% (Original)")
        self.res_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.res_slider = QSlider(Qt.Horizontal)
        self.res_slider.setRange(25, 100)
        self.res_slider.setValue(100)
        self.res_slider.valueChanged.connect(self._on_res_slider_changed)
        res_box.addWidget(self.res_lbl)
        res_box.addWidget(self.res_slider)
        tuning_row.addLayout(res_box)

        # Preset profile
        profile_box = QVBoxLayout()
        profile_lbl = QLabel("Quality Profile:")
        profile_lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced (Optimal visual quality & size)", "balanced")
        self.preset_combo.addItem("Maximum Compression (Smallest file size)", "maximum")
        self.preset_combo.addItem("Fast / High Fidelity (Minimal compression)", "fast")
        profile_box.addWidget(profile_lbl)
        profile_box.addWidget(self.preset_combo)
        tuning_row.addLayout(profile_box)

        settings_layout.addLayout(tuning_row)

        # OUTPUT FOLDER SELECTOR (Explicit user freedom)
        out_box = QVBoxLayout()
        out_title = QLabel("Destination / Output Folder:")
        out_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2563EB;")
        out_box.addWidget(out_title)

        out_row = QHBoxLayout()
        self.out_path_edit = QLineEdit("Default: Same folder as source file")
        self.out_path_edit.setReadOnly(True)
        self.out_path_edit.setStyleSheet("color: #64748B; background: rgba(0,0,0,0.1); padding: 6px;")

        self.choose_dir_btn = QPushButton("Select Output Folder...")
        self.choose_dir_btn.setIcon(get_icon("download", color="#2563EB", size=14))
        self.choose_dir_btn.clicked.connect(self._choose_output_folder)

        self.reset_dir_btn = QPushButton("Reset to Source")
        self.reset_dir_btn.clicked.connect(self._reset_output_folder)
        self.reset_dir_btn.setVisible(False)

        out_row.addWidget(self.out_path_edit, stretch=1)
        out_row.addWidget(self.choose_dir_btn)
        out_row.addWidget(self.reset_dir_btn)
        out_box.addLayout(out_row)
        settings_layout.addLayout(out_box)

        content_layout.addWidget(self.settings_frame)

        # Execution and Action Bar
        action_bar = QHBoxLayout()
        self.compress_btn = QPushButton(" Compress File")
        self.compress_btn.setIcon(get_icon("file_compression", color="#FFFFFF", size=16))
        self.compress_btn.setStyleSheet(
            "QPushButton { background-color: #059669; color: #FFFFFF; font-weight: bold; "
            "padding: 8px 20px; border-radius: 6px; font-size: 13px; } QPushButton:hover { background-color: #047857; }"
        )
        self.compress_btn.setEnabled(False)
        self.compress_btn.clicked.connect(self._start_compression)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_compression)

        action_bar.addWidget(self.compress_btn)
        action_bar.addWidget(self.cancel_btn)
        action_bar.addStretch()
        content_layout.addLayout(action_bar)

        # Progress Bar & Live Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        content_layout.addWidget(self.progress_bar)

        self.status_msg_lbl = QLabel("")
        self.status_msg_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        content_layout.addWidget(self.status_msg_lbl)

        # Results & Comparison Card
        self.results_frame = QFrame()
        self.results_frame.setObjectName("toolCard")
        self.results_frame.setVisible(False)
        res_layout = QVBoxLayout(self.results_frame)
        res_layout.setContentsMargins(12, 12, 12, 12)
        res_layout.setSpacing(8)

        res_title = QLabel("Compression Results & Verification")
        res_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        res_layout.addWidget(res_title)

        self.res_summary_lbl = QLabel("")
        self.res_summary_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #059669;")
        res_layout.addWidget(self.res_summary_lbl)

        self.res_explanation_lbl = QLabel("")
        self.res_explanation_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        self.res_explanation_lbl.setWordWrap(True)
        res_layout.addWidget(self.res_explanation_lbl)

        # Buttons to open file or folder
        res_btn_row = QHBoxLayout()
        self.open_file_btn = QPushButton("Open Compressed File")
        self.open_file_btn.clicked.connect(self._open_output_file)

        self.open_folder_btn = QPushButton("Open Destination Folder")
        self.open_folder_btn.clicked.connect(self._open_output_folder)

        res_btn_row.addWidget(self.open_file_btn)
        res_btn_row.addWidget(self.open_folder_btn)
        res_btn_row.addStretch()
        res_layout.addLayout(res_btn_row)

        content_layout.addWidget(self.results_frame)

        scroll.setWidget(container)
        root_layout.addWidget(scroll, stretch=1)

    def _on_custom_toggled(self, checked: bool):
        self.custom_size_spin.setEnabled(checked)
        self.custom_unit_combo.setEnabled(checked)

    def _on_res_slider_changed(self, val: int):
        self.res_lbl.setText(f"Resolution Scale: {val}%" if val < 100 else "Resolution Scale: 100% (Original)")

    def _choose_output_folder(self):
        start_dir = str(self.custom_output_dir or (self.current_meta.path.parent if self.current_meta else Path.home()))
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder for Compressed Files",
            start_dir,
        )
        if selected:
            self.custom_output_dir = Path(selected)
            self.out_path_edit.setText(str(self.custom_output_dir))
            self.out_path_edit.setStyleSheet("color: #059669; font-weight: bold; padding: 6px;")
            self.reset_dir_btn.setVisible(True)

    def _reset_output_folder(self):
        self.custom_output_dir = None
        self.out_path_edit.setText("Default: Same folder as source file")
        self.out_path_edit.setStyleSheet("color: #64748B; background: rgba(0,0,0,0.1); padding: 6px;")
        self.reset_dir_btn.setVisible(False)

    def _on_files_selected(self, files: List[Path]):
        if not files:
            return
        target = files[0]
        try:
            self.current_meta = inspect_file(target)
            self.file_name_lbl.setText(f"Selected: {self.current_meta.path.name}")
            self.file_details_lbl.setText(self.current_meta.details_summary)
            self.compress_btn.setEnabled(True)
            self.results_frame.setVisible(False)
            self.status_msg_lbl.setText("Ready to compress.")
        except Exception as e:
            QMessageBox.warning(self, "Inspection Error", str(e))

    def _start_compression(self):
        if not self.current_meta:
            return

        # Calculate target size request
        target_bytes = None
        target_pct = None
        if self.radio_preset_25.isChecked():
            target_pct = 25
        elif self.radio_preset_50.isChecked():
            target_pct = 50
        elif self.radio_preset_75.isChecked():
            target_pct = 75
        elif self.radio_custom.isChecked():
            mult = 1024 if self.custom_unit_combo.currentText() == "KB" else 1024 * 1024
            target_bytes = self.custom_size_spin.value() * mult

        scale = self.res_slider.value() / 100.0
        preset = self.preset_combo.currentData()

        # Prompt user if they want to choose explicit Save As destination file
        dst_path = None
        if not self.custom_output_dir:
            # Offer user option to pick direct file location if desired
            pass

        request = CompressionRequest(
            src_path=self.current_meta.path,
            dst_path=dst_path,
            output_dir=self.custom_output_dir,
            target_size_bytes=target_bytes,
            target_percent=target_pct,
            resolution_scale=scale,
            preset=preset,
        )

        self.compress_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.status_msg_lbl.setText("Starting compression...")
        self.results_frame.setVisible(False)

        self.current_task = CompressionTask(request)
        self.current_task.signals.progress.connect(self._on_compress_progress)
        self.current_task.signals.finished.connect(self._on_compress_finished)
        self.current_task.signals.error.connect(self._on_compress_error)
        self.current_task.signals.cancelled.connect(self._on_compress_cancelled)

        QThreadPool.globalInstance().start(self.current_task)

    def _cancel_compression(self):
        if self.current_task:
            self.current_task.cancel()
            self.status_msg_lbl.setText("Cancelling...")
            self.cancel_btn.setEnabled(False)

    def _on_compress_progress(self, percent: float, msg: str):
        self.progress_bar.setValue(int(percent))
        self.status_msg_lbl.setText(msg)

    def _on_compress_finished(self, result: CompressionResult):
        self.last_result = result
        self.compress_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)

        self.results_frame.setVisible(True)
        self.res_summary_lbl.setText(result.message)

        if result.target_achieved is False and result.target_unachievable_reason:
            self.res_explanation_lbl.setText(f"Target notice: {result.target_unachievable_reason}")
            self.res_explanation_lbl.setStyleSheet("color: #D97706; font-size: 11px;")
        else:
            self.res_explanation_lbl.setText("Original file preserved intact. Compressed output verified.")
            self.res_explanation_lbl.setStyleSheet("color: #059669; font-size: 11px;")

        self.status_msg_lbl.setText(f"Done! Output saved to: {result.dst_path.name}")

    def _on_compress_error(self, err_msg: str):
        self.compress_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_msg_lbl.setText(f"Failed: {err_msg}")
        QMessageBox.critical(self, "Compression Error", f"Compression failed:\n\n{err_msg}")

    def _on_compress_cancelled(self):
        self.compress_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_msg_lbl.setText("Compression cancelled.")

    def _open_output_file(self):
        if self.last_result and self.last_result.dst_path.exists():
            os.startfile(str(self.last_result.dst_path))

    def _open_output_folder(self):
        if self.last_result and self.last_result.dst_path.exists():
            os.startfile(str(self.last_result.dst_path.parent))
