"""Audio-to-Text Speech Recognition View for Vert."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.transcription.audio_preprocessor import (
    SUPPORTED_AUDIO_EXTENSIONS,
    validate_audio_file,
)
from core.transcription.engine import find_whisper_binary
from core.transcription.exporters import (
    TranscriptionResult,
    export_to_json,
    export_to_srt,
    export_to_txt,
    export_to_vtt,
)
from core.transcription.models import (
    MODEL_CATALOG,
    delete_model,
    download_model,
    get_model_path,
    is_model_installed,
)
from core.transcription.worker import TranscriptionTask
from ui.icons import get_icon, get_pixmap

LANGUAGES = [
    ("auto", "Auto-Detect Spoken Language"),
    ("id", "Indonesian (Bahasa Indonesia)"),
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("ja", "Japanese"),
    ("zh", "Chinese"),
    ("ar", "Arabic"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
]


class AudioDropZone(QFrame):
    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("audioDropZone")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_pixmap("audio_transcription", color="#2563EB", size=32))
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("Click to select or drop audio file here")
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.hint_label = QLabel("Supported: MP3, WAV, M4A, FLAC, OGG, AAC (100% Local & Offline)")
        self.hint_label.setStyleSheet("color: #64748B; font-size: 11px;")
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            formats = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_AUDIO_EXTENSIONS))
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Audio File for Transcription",
                "",
                f"Audio Files ({formats});;All Files (*.*)",
            )
            if file_path:
                self.file_selected.emit(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                ext = Path(url.toLocalFile()).suffix.lower()
                if ext in SUPPORTED_AUDIO_EXTENSIONS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            ext = Path(file_path).suffix.lower()
            if ext in SUPPORTED_AUDIO_EXTENSIONS:
                self.file_selected.emit(file_path)
                event.acceptProposedAction()
                return


class AudioTranscriptionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_audio_path: Optional[Path] = None
        self.last_result: Optional[TranscriptionResult] = None
        self.current_task: Optional[TranscriptionTask] = None

        self._init_ui()
        self._refresh_model_status()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 8, 12, 12)
        root_layout.setSpacing(10)

        # Header title
        header_box = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap("audio_transcription", color="#7C3AED", size=24))
        title_lbl = QLabel("Audio-to-Text Transcription")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        badge = QLabel(" whisper.cpp • 100% Offline ")
        badge.setStyleSheet(
            "color: #7C3AED; border: 1.5px solid #7C3AED; border-radius: 4px; "
            "font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )
        header_box.addWidget(icon_lbl)
        header_box.addWidget(title_lbl)
        header_box.addWidget(badge)
        header_box.addStretch()
        root_layout.addLayout(header_box)

        # Top Section: File Picker & Configuration Controls
        controls_frame = QFrame()
        controls_frame.setObjectName("toolCard")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        controls_layout.setSpacing(10)

        # Drop zone
        self.drop_zone = AudioDropZone()
        self.drop_zone.file_selected.connect(self._on_file_selected)
        controls_layout.addWidget(self.drop_zone)

        # Selected file status row
        self.file_info_lbl = QLabel("No audio file selected.")
        self.file_info_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        controls_layout.addWidget(self.file_info_lbl)

        # Configuration Row: Model, Language, and Action
        config_row = QHBoxLayout()
        config_row.setSpacing(12)

        # Model selector
        model_box = QVBoxLayout()
        model_label = QLabel("Speech Model:")
        model_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.model_combo = QComboBox()
        for key, info in MODEL_CATALOG.items():
            self.model_combo.addItem(info.display_name, key)
        self.model_combo.setCurrentIndex(1)  # Default: Base
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_box.addWidget(model_label)
        model_box.addWidget(self.model_combo)
        config_row.addLayout(model_box)

        # Model status and download/delete button
        model_action_box = QVBoxLayout()
        self.model_status_lbl = QLabel("Status: Checking...")
        self.model_status_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        self.model_action_btn = QPushButton("Download Model")
        self.model_action_btn.clicked.connect(self._on_model_action_clicked)
        model_action_box.addWidget(self.model_status_lbl)
        model_action_box.addWidget(self.model_action_btn)
        config_row.addLayout(model_action_box)

        # Language selector
        lang_box = QVBoxLayout()
        lang_label = QLabel("Spoken Language:")
        lang_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.lang_combo = QComboBox()
        for code, label in LANGUAGES:
            self.lang_combo.addItem(label, code)
        lang_box.addWidget(lang_label)
        lang_box.addWidget(self.lang_combo)
        config_row.addLayout(lang_box)

        config_row.addStretch()

        # Start / Cancel Buttons
        btn_box = QVBoxLayout()
        btn_box.addStretch()
        action_btns = QHBoxLayout()
        self.start_btn = QPushButton(" Start Transcription")
        self.start_btn.setIcon(get_icon("audio_transcription", color="#FFFFFF", size=16))
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #7C3AED; color: #FFFFFF; font-weight: bold; "
            "padding: 8px 18px; border-radius: 6px; } QPushButton:hover { background-color: #6D28D9; }"
        )
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_transcription)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_transcription)

        action_btns.addWidget(self.start_btn)
        action_btns.addWidget(self.cancel_btn)
        btn_box.addLayout(action_btns)
        config_row.addLayout(btn_box)

        controls_layout.addLayout(config_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        controls_layout.addWidget(self.progress_bar)

        self.status_msg_lbl = QLabel("")
        self.status_msg_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        controls_layout.addWidget(self.status_msg_lbl)

        root_layout.addWidget(controls_frame)

        # Transcript Editor & Output Section
        editor_frame = QFrame()
        editor_frame.setObjectName("toolCard")
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(12, 12, 12, 12)
        editor_layout.setSpacing(8)

        # Editor toolbar
        toolbar = QHBoxLayout()
        editor_title = QLabel("Transcript Editor & Export")
        editor_title.setStyleSheet("font-size: 13px; font-weight: bold;")
        toolbar.addWidget(editor_title)
        toolbar.addStretch()

        self.copy_btn = QPushButton(" Copy Text")
        self.copy_btn.setIcon(get_icon("copy", color="#2563EB", size=14))
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        toolbar.addWidget(self.copy_btn)

        self.export_txt_btn = QPushButton("Export TXT")
        self.export_txt_btn.setEnabled(False)
        self.export_txt_btn.clicked.connect(lambda: self._export("txt"))
        toolbar.addWidget(self.export_txt_btn)

        self.export_srt_btn = QPushButton("Export SRT")
        self.export_srt_btn.setEnabled(False)
        self.export_srt_btn.clicked.connect(lambda: self._export("srt"))
        toolbar.addWidget(self.export_srt_btn)

        self.export_vtt_btn = QPushButton("Export VTT")
        self.export_vtt_btn.setEnabled(False)
        self.export_vtt_btn.clicked.connect(lambda: self._export("vtt"))
        toolbar.addWidget(self.export_vtt_btn)

        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.setEnabled(False)
        self.export_json_btn.clicked.connect(lambda: self._export("json"))
        toolbar.addWidget(self.export_json_btn)

        editor_layout.addLayout(toolbar)

        # Transcript text editor
        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlaceholderText("Transcribed text will appear here. You can freely edit before exporting.")
        self.text_editor.setStyleSheet("font-size: 13px; line-height: 1.5; font-family: monospace;")
        editor_layout.addWidget(self.text_editor, stretch=1)

        root_layout.addWidget(editor_frame, stretch=1)

    def _on_file_selected(self, file_path: str):
        path = Path(file_path).resolve()
        try:
            validate_audio_file(path)
            self.current_audio_path = path
            size_mb = path.stat().st_size / (1024 * 1024)
            self.file_info_lbl.setText(
                f"Selected: {path.name} ({size_mb:.2f} MB, {path.suffix.upper()})"
            )
            self.file_info_lbl.setStyleSheet("color: #059669; font-size: 12px; font-weight: bold;")
            self._update_start_button_state()
        except Exception as e:
            QMessageBox.warning(self, "Invalid Audio File", str(e))

    def _on_model_changed(self):
        self._refresh_model_status()
        self._update_start_button_state()

    def _refresh_model_status(self):
        model_name = self.model_combo.currentData()
        if not model_name:
            return
        installed = is_model_installed(model_name)
        info = MODEL_CATALOG[model_name]

        if installed:
            self.model_status_lbl.setText(f"Status: Installed ({info.size_mb} MB)")
            self.model_status_lbl.setStyleSheet("color: #059669; font-size: 11px; font-weight: bold;")
            self.model_action_btn.setText("Delete Model")
            self.model_action_btn.setIcon(get_icon("trash", color="#DC2626", size=14))
        else:
            self.model_status_lbl.setText(f"Status: Not Installed (~{info.size_mb} MB)")
            self.model_status_lbl.setStyleSheet("color: #D97706; font-size: 11px;")
            self.model_action_btn.setText("Download")
            self.model_action_btn.setIcon(get_icon("download", color="#2563EB", size=14))

    def _on_model_action_clicked(self):
        model_name = self.model_combo.currentData()
        if not model_name:
            return

        installed = is_model_installed(model_name)
        if installed:
            reply = QMessageBox.question(
                self,
                "Delete Speech Model",
                f"Are you sure you want to delete the '{model_name}' model to free up disk space?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                delete_model(model_name)
                self._refresh_model_status()
                self._update_start_button_state()
        else:
            info = MODEL_CATALOG[model_name]
            reply = QMessageBox.question(
                self,
                "Download Speech Model",
                f"Download '{info.display_name}' ({info.size_mb} MB) for offline transcription?\n\n"
                f"Once downloaded, all transcriptions run 100% locally and offline without internet.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._download_model_async(model_name)

    def _download_model_async(self, model_name: str):
        self.model_action_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_msg_lbl.setText(f"Connecting to download '{model_name}' model...")

        class DownloadRunner(QObject):
            progress = Signal(float, str)
            finished = Signal()
            error = Signal(str)

            def __init__(self, name: str):
                super().__init__()
                self.name = name

            def run(self):
                try:
                    download_model(
                        self.name,
                        progress_callback=lambda p, m: self.progress.emit(p, m),
                    )
                    self.finished.emit()
                except Exception as exc:
                    self.error.emit(str(exc))

        runner = DownloadRunner(model_name)
        runner.progress.connect(self._on_download_progress)
        runner.finished.connect(self._on_download_finished)
        runner.error.connect(self._on_download_error)

        from PySide6.QtCore import QRunnable
        class RunnableWrapper(QRunnable):
            def run(self):
                runner.run()

        QThreadPool.globalInstance().start(RunnableWrapper())

    def _on_download_progress(self, percent: float, msg: str):
        self.progress_bar.setValue(int(percent))
        self.status_msg_lbl.setText(msg)

    def _on_download_finished(self):
        self.progress_bar.setVisible(False)
        self.model_action_btn.setEnabled(True)
        self.status_msg_lbl.setText("Model downloaded successfully!")
        self._refresh_model_status()
        self._update_start_button_state()
        QMessageBox.information(self, "Download Complete", "Speech model downloaded and ready for offline use.")

    def _on_download_error(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.model_action_btn.setEnabled(True)
        self.status_msg_lbl.setText(f"Download failed: {err_msg}")
        self._refresh_model_status()
        QMessageBox.warning(self, "Download Failed", f"Failed to download model:\n{err_msg}")

    def _update_start_button_state(self):
        has_file = self.current_audio_path is not None and self.current_audio_path.exists()
        model_name = self.model_combo.currentData()
        model_ok = is_model_installed(model_name) if model_name else False
        self.start_btn.setEnabled(has_file and model_ok)

    def _start_transcription(self):
        if not self.current_audio_path:
            return

        whisper_bin = find_whisper_binary()
        if not whisper_bin:
            QMessageBox.warning(
                self,
                "whisper.cpp Engine Required",
                "whisper.cpp executable was not found in engines/ or system PATH.\n\n"
                "Please place whisper-cli.exe in the engines/ directory or run:\n"
                "python scripts/download_engines.py --whisper",
            )
            return

        model_name = self.model_combo.currentData()
        lang_code = self.lang_combo.currentData()

        self.start_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.status_msg_lbl.setText("Starting transcription worker...")
        self.text_editor.clear()

        self.current_task = TranscriptionTask(
            audio_path=self.current_audio_path,
            model_name=model_name,
            language=lang_code,
        )
        self.current_task.signals.progress.connect(self._on_transcribe_progress)
        self.current_task.signals.finished.connect(self._on_transcribe_finished)
        self.current_task.signals.error.connect(self._on_transcribe_error)
        self.current_task.signals.cancelled.connect(self._on_transcribe_cancelled)

        QThreadPool.globalInstance().start(self.current_task)

    def _cancel_transcription(self):
        if self.current_task:
            self.current_task.cancel()
            self.status_msg_lbl.setText("Cancelling transcription...")
            self.cancel_btn.setEnabled(False)

    def _on_transcribe_progress(self, percent: float, msg: str):
        self.progress_bar.setValue(int(percent))
        self.status_msg_lbl.setText(msg)

    def _on_transcribe_finished(self, result: TranscriptionResult):
        self.last_result = result
        self.start_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_msg_lbl.setText(
            f"Transcription complete ({result.duration_sec:.1f}s audio processed)."
        )

        self.text_editor.setPlainText(result.full_text)
        self.copy_btn.setEnabled(True)
        self.export_txt_btn.setEnabled(True)
        self.export_srt_btn.setEnabled(True)
        self.export_vtt_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)

    def _on_transcribe_error(self, err_msg: str):
        self.start_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_msg_lbl.setText(f"Error: {err_msg}")
        QMessageBox.critical(self, "Transcription Error", f"Failed to transcribe audio:\n\n{err_msg}")

    def _on_transcribe_cancelled(self):
        self.start_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_msg_lbl.setText("Transcription was cancelled.")

    def _copy_to_clipboard(self):
        text = self.text_editor.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_msg_lbl.setText("Transcript copied to clipboard!")

    def _export(self, format_type: str):
        if not self.last_result:
            return

        # Update result full_text from user edits
        self.last_result.full_text = self.text_editor.toPlainText()

        default_name = f"{self.current_audio_path.stem}.{format_type}" if self.current_audio_path else f"transcript.{format_type}"
        file_filters = {
            "txt": "Text File (*.txt)",
            "srt": "SubRip Subtitles (*.srt)",
            "vtt": "WebVTT Subtitles (*.vtt)",
            "json": "JSON File (*.json)",
        }
        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Transcript as {format_type.upper()}",
            default_name,
            file_filters.get(format_type, "All Files (*.*)"),
        )
        if not dest_path:
            return

        try:
            if format_type == "txt":
                export_to_txt(self.last_result, dest_path)
            elif format_type == "srt":
                export_to_srt(self.last_result, dest_path)
            elif format_type == "vtt":
                export_to_vtt(self.last_result, dest_path)
            elif format_type == "json":
                export_to_json(self.last_result, dest_path)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Transcript exported successfully to:\n{dest_path}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export transcript:\n{e}")
