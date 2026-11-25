"""Background worker for asynchronous compression tasks."""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, QRunnable, Signal

from core.compression.base import CompressionRequest, CompressionResult
from core.compression.optimizer import compress_file


class CompressionWorkerSignals(QObject):
    started = Signal(str)           # job_id or file name
    progress = Signal(float, str)   # percent, status message
    finished = Signal(object)       # CompressionResult
    error = Signal(str)             # error message
    cancelled = Signal()


class CompressionTask(QRunnable):
    """QRunnable task for running compression in background thread."""

    def __init__(self, request: CompressionRequest, job_id: str = ""):
        super().__init__()
        self.request = request
        self.job_id = job_id
        self.signals = CompressionWorkerSignals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self.signals.started.emit(self.job_id or self.request.src_path.name)
        try:
            result = compress_file(
                request=self.request,
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
