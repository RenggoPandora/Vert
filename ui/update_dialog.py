"""In-App Direct Auto-Update Dialog."""

import sys
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.updater import UpdateDownloadTask, launch_installer_and_exit
from core.version import __version__
from ui.icons import get_icon, get_pixmap


class UpdateDialog(QDialog):
    def __init__(self, new_tag: str, download_url: str, release_body: str, parent=None):
        super().__init__(parent)
        self.new_tag = new_tag
        self.download_url = download_url
        self.release_body = release_body
        self._download_task = None

        self.setWindowTitle("Software Update Available — Vert")
        self.resize(520, 380)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header with vector icon
        header = QHBoxLayout()
        header.setSpacing(14)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap("download", color="#2563EB", size=36))
        header.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_lbl = QLabel("New Version Available!")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        version_lbl = QLabel(f"Version {self.new_tag} is ready to install (Current: v{__version__})")
        version_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(version_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # Release notes text
        notes_title = QLabel("What's New:")
        notes_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(notes_title)

        self.notes_view = QTextEdit()
        self.notes_view.setReadOnly(True)
        self.notes_view.setPlainText(self.release_body or "General stability improvements and performance enhancements.")
        self.notes_view.setStyleSheet("font-size: 11px; line-height: 1.4; background: rgba(0,0,0,0.1); border-radius: 6px; padding: 6px;")
        layout.addWidget(self.notes_view, stretch=1)

        # Progress bar (hidden until download starts)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("Click 'Update Now' to update automatically without downloading manually.")
        self.status_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.status_lbl)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.later_btn = QPushButton("Remind Me Later")
        self.later_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.later_btn)

        self.update_btn = QPushButton(" Update Now")
        self.update_btn.setIcon(get_icon("download", color="#FFFFFF", size=16))
        self.update_btn.setStyleSheet(
            "QPushButton { background-color: #2563EB; color: #FFFFFF; font-weight: bold; "
            "padding: 8px 18px; border-radius: 6px; } QPushButton:hover { background-color: #1D4ED8; }"
        )
        self.update_btn.clicked.connect(self._start_update)
        btn_row.addWidget(self.update_btn)

        layout.addLayout(btn_row)

    def _start_update(self):
        self.update_btn.setEnabled(False)
        self.later_btn.setText("Cancel")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Connecting to download update...")

        self._download_task = UpdateDownloadTask(self.download_url)
        self._download_task.signals.progress.connect(self._on_progress)
        self._download_task.signals.finished.connect(self._on_finished)
        self._download_task.signals.failed.connect(self._on_failed)
        self._download_task.signals.cancelled.connect(self._on_cancelled)

        QThreadPool.globalInstance().start(self._download_task)

    def _on_progress(self, percent: float, msg: str):
        self.progress_bar.setValue(int(percent))
        self.status_lbl.setText(msg)

    def _on_finished(self, installer_path: str):
        self.progress_bar.setValue(100)
        self.status_lbl.setText("Download complete! Applying update and restarting Vert...")
        self.status_lbl.setStyleSheet("color: #059669; font-weight: bold; font-size: 11px;")

        # Launch downloaded installer silently and quit running instance
        try:
            launch_installer_and_exit(installer_path)
            QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to start installer:\n{e}")

    def _on_failed(self, err_msg: str):
        self.update_btn.setEnabled(True)
        self.later_btn.setText("Close")
        self.progress_bar.setVisible(False)
        self.status_lbl.setText(f"Update failed: {err_msg}")
        self.status_lbl.setStyleSheet("color: #DC2626; font-size: 11px;")
        QMessageBox.warning(self, "Download Error", f"Could not download update:\n{err_msg}")

    def _on_cancelled(self):
        self.update_btn.setEnabled(True)
        self.later_btn.setText("Close")
        self.progress_bar.setVisible(False)
        self.status_lbl.setText("Update cancelled.")

    def reject(self):
        if self._download_task:
            self._download_task.cancel()
        super().reject()
