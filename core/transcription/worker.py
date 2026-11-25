"""Background worker for asynchronous speech recognition tasks."""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, QRunnable, Signal

from core.transcription.engine import run_transcription
from core.transcription.exporters import TranscriptionResult
from core.transcription.models import download_model


class ModelDownloadSignals(QObject):
    started = Signal()
    progress = Signal(float, str)  # percent, message
    finished = Signal(str, object)  # model_name, path
    error = Signal(str)
    cancelled = Signal()


class ModelDownloadTask(QRunnable):
    """QRunnable task for downloading whisper speech model in background."""

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name
        self.signals = ModelDownloadSignals()
        self.setAutoDelete(False)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self.signals.started.emit()
        try:
            path = download_model(
                self.model_name,
                progress_callback=lambda pct, msg: self.signals.progress.emit(pct, msg),
                is_cancelled=lambda: self._is_cancelled,
            )
            if self._is_cancelled:
                self.signals.cancelled.emit()
            else:
                self.signals.finished.emit(self.model_name, path)
        except InterruptedError:
            self.signals.cancelled.emit()
        except Exception as exc:
            self.signals.error.emit(str(exc))


class TranscriptionWorkerSignals(QObject):
    started = Signal()
    progress = Signal(float, str)  # percent, message
    finished = Signal(object)      # TranscriptionResult
    error = Signal(str)            # error message
    cancelled = Signal()


class TranscriptionTask(QRunnable):
    """QRunnable task for running transcription in background thread."""

    def __init__(
        self,
        audio_path: Path | str,
        model_name: str = "base",
        language: str = "auto",
        threads: int = 4,
    ):
        super().__init__()
        self.audio_path = Path(audio_path)
        self.model_name = model_name
        self.language = language
        self.threads = threads
        self.signals = TranscriptionWorkerSignals()
        self._is_cancelled = False

    def cancel(self):
        """Flag task for cancellation."""
        self._is_cancelled = True

    def run(self):
        self.signals.started.emit()
        try:
            result = run_transcription(
                audio_path=self.audio_path,
                model_name=self.model_name,
                language=self.language,
                threads=self.threads,
                progress_callback=lambda pct, msg: self.signals.progress.emit(pct, msg),
                is_cancelled=lambda: self._is_cancelled,
            )
            if self._is_cancelled:
                self.signals.cancelled.emit()
            else:
                self.signals.finished.emit(result)
        except InterruptedError:
            self.signals.cancelled.emit()
        except Exception as exc:
            self.signals.error.emit(str(exc))
