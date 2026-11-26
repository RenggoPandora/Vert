"""Background worker for asynchronous speech recognition tasks."""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, QRunnable, Signal

import io
import shutil
import urllib.request
import zipfile

from core.transcription.engine import run_transcription
from core.transcription.exporters import TranscriptionResult
from core.transcription.models import download_model


class EngineDownloadSignals(QObject):
    started = Signal()
    progress = Signal(float, str)  # percent, message
    finished = Signal(object)      # binary path
    error = Signal(str)
    cancelled = Signal()


class EngineDownloadTask(QRunnable):
    """QRunnable task for downloading whisper.cpp runtime engine in background."""

    WHISPER_ENGINE_URL = "https://github.com/ggml-org/whisper.cpp/releases/download/b5907/whisper-bin-x64.zip"

    def __init__(self):
        super().__init__()
        self.signals = EngineDownloadSignals()
        self.setAutoDelete(False)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self.signals.started.emit()
        target_dir = Path.home() / ".vert" / "engines"
        target_dir.mkdir(parents=True, exist_ok=True)
        temp_zip = target_dir / "whisper_temp.zip"

        req = urllib.request.Request(
            self.WHISPER_ENGINE_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Vert/1.1.2"},
        )

        try:
            self.signals.progress.emit(10.0, "Downloading whisper.cpp engine (~8.7 MB)...")
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_bytes = int(resp.headers.get("content-length") or (9 * 1024 * 1024))
                downloaded = 0
                block_size = 1024 * 128

                with open(temp_zip, "wb") as f:
                    while True:
                        if self._is_cancelled:
                            f.close()
                            if temp_zip.exists():
                                temp_zip.unlink()
                            self.signals.cancelled.emit()
                            return
                        chunk = resp.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        pct = min(80.0, 10.0 + (downloaded / total_bytes) * 70.0)
                        self.signals.progress.emit(pct, f"Downloading engine: {downloaded / (1024*1024):.1f} / {total_bytes / (1024*1024):.1f} MB...")

            self.signals.progress.emit(85.0, "Extracting whisper.cpp runtime and libraries...")
            target_exe = target_dir / "whisper-cli.exe"
            with zipfile.ZipFile(temp_zip, "r") as zf:
                for member in zf.namelist():
                    if member.startswith("Release/"):
                        fname = Path(member).name
                        if fname.endswith(".dll") or fname in ("whisper-cli.exe", "main.exe"):
                            dest = target_dir / fname
                            with zf.open(member) as src, open(dest, "wb") as dst:
                                shutil.copyfileobj(src, dst)

            if temp_zip.exists():
                temp_zip.unlink(missing_ok=True)

            if target_exe.exists():
                self.signals.progress.emit(100.0, "Engine ready.")
                self.signals.finished.emit(target_exe)
            else:
                self.signals.error.emit("Failed to extract whisper-cli.exe from engine archive.")
        except Exception as exc:
            if temp_zip.exists():
                temp_zip.unlink(missing_ok=True)
            self.signals.error.emit(str(exc))


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
