"""1:1 Batch conversion queue interface with drag-and-drop support."""

import os
import subprocess
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QThreadPool, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.naming import get_safe_output_path
from core.router import get_file_category, get_target_formats
from core.worker import ConversionJob, ConversionTask


def format_size(bytes_val: int) -> str:
    """Format file size in human readable units."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"


class DropZone(QFrame):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Drag & Drop Files Here")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.sub_label = QLabel("Supports Word, Excel, PowerPoint, PDF, Images, Video, Audio, and Data")
        self.sub_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.sub_label.setAlignment(Qt.AlignCenter)

        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setFixedWidth(140)
        self.browse_btn.clicked.connect(self._on_browse)

        layout.addWidget(self.title_label)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)

    def _on_browse(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Convert",
            "",
            "All Files (*.*)",
        )
        if files:
            self.files_dropped.emit([Path(f) for f in files])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setObjectName("dropZoneActive")
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setObjectName("dropZone")
        self.style().polish(self)

    def dropEvent(self, event):
        self.setObjectName("dropZone")
        self.style().polish(self)
        paths = []
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            if local_path and os.path.isfile(local_path):
                paths.append(Path(local_path))
        if paths:
            self.files_dropped.emit(paths)


class QueueView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.items: dict[str, dict] = {}  # job_id -> metadata
        self.active_tasks: dict[str, ConversionTask] = {}  # retain task instances to prevent GC
        self.custom_output_dir: Optional[Path] = None
        self.total_jobs_in_batch = 0
        self.completed_jobs_count = 0

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Drop Zone
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_files)
        main_layout.addWidget(self.drop_zone)

        # Queue Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Source File", "Size", "Convert To", "Status", "Actions"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)

        # Output options bar
        output_bar = QHBoxLayout()
        self.output_label = QLabel("Output Folder: Same as source file")
        self.output_label.setStyleSheet("color: #94A3B8;")

        self.choose_out_btn = QPushButton("Select Output Folder")
        self.choose_out_btn.clicked.connect(self._on_choose_output_dir)

        self.reset_out_btn = QPushButton("Reset to Source")
        self.reset_out_btn.clicked.connect(self._on_reset_output_dir)
        self.reset_out_btn.setVisible(False)

        output_bar.addWidget(self.output_label)
        output_bar.addWidget(self.choose_out_btn)
        output_bar.addWidget(self.reset_out_btn)
        output_bar.addStretch()
        main_layout.addLayout(output_bar)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)

        # Bottom Action Bar
        actions_bar = QHBoxLayout()
        self.clear_finished_btn = QPushButton("Clear Finished")
        self.clear_finished_btn.clicked.connect(self._clear_finished)

        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self._clear_all)

        self.convert_all_btn = QPushButton("Convert All")
        self.convert_all_btn.setObjectName("primaryButton")
        self.convert_all_btn.clicked.connect(self.start_conversion)

        actions_bar.addWidget(self.clear_finished_btn)
        actions_bar.addWidget(self.clear_all_btn)
        actions_bar.addStretch()
        actions_bar.addWidget(self.convert_all_btn)
        main_layout.addLayout(actions_bar)

    def _on_choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.custom_output_dir = Path(folder)
            self.output_label.setText(f"Output Folder: {self.custom_output_dir}")
            self.reset_out_btn.setVisible(True)

    def _on_reset_output_dir(self):
        self.custom_output_dir = None
        self.output_label.setText("Output Folder: Same as source file")
        self.reset_out_btn.setVisible(False)

    def add_files(self, paths: list[Path]):
        for path in paths:
            if not path.is_file():
                continue
            targets = get_target_formats(path)
            if not targets:
                QMessageBox.warning(
                    self,
                    "Unsupported File",
                    f"'{path.name}' format is not supported for 1:1 conversion.",
                )
                continue

            job_id = f"job_{len(self.items) + 1}_{path.name}"
            row = self.table.rowCount()
            self.table.insertRow(row)

            # File name item
            name_item = QTableWidgetItem(path.name)
            name_item.setToolTip(str(path))
            self.table.setItem(row, 0, name_item)

            # Size item
            try:
                size_str = format_size(path.stat().st_size)
            except Exception:
                size_str = "0 B"
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, size_item)

            # Target format combobox
            combo = QComboBox()
            for opt in targets:
                combo.addItem(opt.label, opt.extension)
            self.table.setCellWidget(row, 2, combo)

            # Status badge
            status_item = QTableWidgetItem("Queued")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, status_item)

            # Action widget (Remove button initially)
            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("dangerButton")
            remove_btn.clicked.connect(lambda _, jid=job_id: self._remove_job(jid))
            self.table.setCellWidget(row, 4, remove_btn)

            self.items[job_id] = {
                "row": row,
                "src_path": path,
                "combo": combo,
                "status": "Queued",
                "output_path": None,
            }

    def _remove_job(self, job_id: str):
        if job_id not in self.items:
            return
        row = self.items[job_id]["row"]
        self.table.removeRow(row)
        del self.items[job_id]
        # Re-index rows
        for idx in range(self.table.rowCount()):
            for jid, data in self.items.items():
                if data["row"] > row:
                    data["row"] -= 1

    def _clear_all(self):
        self.table.setRowCount(0)
        self.items.clear()
        self.progress_bar.setVisible(False)

    def _clear_finished(self):
        to_delete = [jid for jid, data in self.items.items() if data["status"] in ("Done", "Failed")]
        for jid in to_delete:
            self._remove_job(jid)

    def start_conversion(self):
        queued_jobs = [
            (jid, data) for jid, data in self.items.items() if data["status"] == "Queued"
        ]
        if not queued_jobs:
            QMessageBox.information(self, "Nothing to Convert", "No queued files to convert.")
            return

        self.total_jobs_in_batch = len(queued_jobs)
        self.completed_jobs_count = 0
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.convert_all_btn.setEnabled(False)

        for jid, data in queued_jobs:
            src = data["src_path"]
            target_ext = data["combo"].currentData()
            dest_dir = self.custom_output_dir if self.custom_output_dir else src.parent
            dst = get_safe_output_path(dest_dir, src.name, target_ext)

            job = ConversionJob(job_id=jid, src_path=src, dst_path=dst)
            task = ConversionTask(job)

            # Store reference to prevent GC while executing
            self.active_tasks[jid] = task

            task.signals.started.connect(self._on_job_started)
            task.signals.finished.connect(self._on_job_finished)
            task.signals.failed.connect(self._on_job_failed)

            self.thread_pool.start(task)

    def _on_job_started(self, job_id: str):
        if job_id in self.items:
            row = self.items[job_id]["row"]
            self.items[job_id]["status"] = "Converting"
            item = self.table.item(row, 3)
            if item:
                item.setText("Converting...")
                item.setForeground(Qt.cyan)

    def _on_job_finished(self, job_id: str, out_path: str):
        self.completed_jobs_count += 1
        pct = int((self.completed_jobs_count / max(1, self.total_jobs_in_batch)) * 100)
        self.progress_bar.setValue(pct)

        # Release task reference safely
        self.active_tasks.pop(job_id, None)

        if job_id in self.items:
            row = self.items[job_id]["row"]
            self.items[job_id]["status"] = "Done"
            self.items[job_id]["output_path"] = out_path

            status_item = self.table.item(row, 3)
            if status_item:
                status_item.setText("Done")
                status_item.setForeground(Qt.green)

            # Replace action with "Open" button
            open_btn = QPushButton("Open")
            open_btn.setStyleSheet("color: #10B981; font-weight: bold;")
            open_btn.clicked.connect(lambda _, p=out_path: self._open_path(p))
            self.table.setCellWidget(row, 4, open_btn)

        if self.completed_jobs_count >= self.total_jobs_in_batch:
            self.convert_all_btn.setEnabled(True)
            self._notify_batch_completion()

    def _on_job_failed(self, job_id: str, error_msg: str):
        self.completed_jobs_count += 1
        pct = int((self.completed_jobs_count / max(1, self.total_jobs_in_batch)) * 100)
        self.progress_bar.setValue(pct)

        # Release task reference safely
        self.active_tasks.pop(job_id, None)

        if job_id in self.items:
            row = self.items[job_id]["row"]
            self.items[job_id]["status"] = "Failed"

            status_item = self.table.item(row, 3)
            if status_item:
                status_item.setText("Failed")
                status_item.setForeground(Qt.red)
                status_item.setToolTip(error_msg)

        if self.completed_jobs_count >= self.total_jobs_in_batch:
            self.convert_all_btn.setEnabled(True)
            self._notify_batch_completion()

    def _notify_batch_completion(self):
        done_count = sum(1 for d in self.items.values() if d["status"] == "Done")
        failed_count = sum(1 for d in self.items.values() if d["status"] == "Failed")
        if done_count > 0 and failed_count == 0:
            QMessageBox.information(
                self,
                "Conversion Complete",
                f"Successfully converted {done_count} file(s)!",
            )
        elif failed_count > 0:
            QMessageBox.warning(
                self,
                "Conversion Finished with Issues",
                f"Finished: {done_count} converted, {failed_count} failed.\nHover over 'Failed' status to view error details.",
            )

    def _open_path(self, path_str: str):
        path = Path(path_str)
        if path.exists():
            # Open file with default Windows handler
            os.startfile(str(path))
        elif path.parent.exists():
            os.startfile(str(path.parent))
