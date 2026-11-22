"""Non-blocking background conversion runner with PySide6 signals."""

import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from core.data_converter import convert_data
from core.image_converter import convert_image
from core.media_converter import convert_media
from core.office_converter import convert_office_to_pdf
from core.pdf_tools import pdf_to_docx, pdf_to_images, pdf_to_xlsx
from core.router import FileCategory, get_file_category, normalize_extension


@dataclass
class ConversionJob:
    job_id: str
    src_path: Path
    dst_path: Path
    category: Optional[FileCategory] = None

    def __post_init__(self):
        self.src_path = Path(self.src_path)
        self.dst_path = Path(self.dst_path)
        if self.category is None:
            self.category = get_file_category(self.src_path)


def format_error_message(exc: Exception) -> str:
    """Translate system exceptions into clear user-facing messages."""
    msg = str(exc)
    if "Permission denied" in msg or "used by another process" in msg:
        return "File is open in another program or locked by Windows."
    if "password" in msg.lower():
        return "Password-protected PDFs are not supported."
    if "ffmpeg.exe not found" in msg:
        return "Media engine (ffmpeg.exe) is missing. Run download script."
    if "LibreOffice was found" in msg or "Microsoft Office" in msg:
        return "Office engine not found. Install MS Office or download LibreOffice Portable."
    if "zero pages" in msg.lower() or "empty" in msg.lower():
        return "Input file contains no readable content or pages."
    return msg or "Conversion failed unexpectedly."


def dispatch_conversion(job: ConversionJob) -> Path:
    """Execute the conversion matching source and target extensions."""
    src = job.src_path
    dst = job.dst_path
    src_ext = normalize_extension(src)
    dst_ext = normalize_extension(dst)

    # 1. Image -> Image or Image -> PDF
    if src_ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".ico", ".tiff", ".tif"]:
        return convert_image(src, dst)

    # 2. PDF -> Office or Images
    if src_ext == ".pdf":
        if dst_ext == ".docx":
            return pdf_to_docx(src, dst)
        elif dst_ext == ".xlsx":
            return pdf_to_xlsx(src, dst)
        elif dst_ext in [".png", ".jpg"]:
            out_dir = dst.parent
            imgs = pdf_to_images(src, out_dir, image_ext=dst_ext)
            return imgs[0] if imgs else dst
        else:
            raise ValueError(f"Unsupported PDF target: {dst_ext}")

    # 3. Office -> PDF
    if src_ext in [".docx", ".pptx"] or (src_ext == ".xlsx" and dst_ext == ".pdf"):
        return convert_office_to_pdf(src, dst)

    # 4. Data -> Data (CSV / XLSX / JSON)
    if src_ext in [".csv", ".json"] or (src_ext == ".xlsx" and dst_ext in [".csv", ".json"]):
        return convert_data(src, dst)

    # 5. Media -> Media
    if src_ext in [".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".flac"]:
        return convert_media(src, dst)

    raise ValueError(f"No conversion pipeline found for {src.name} to {dst.name}")


class JobSignals(QObject):
    started = Signal(str)
    finished = Signal(str, str)  # job_id, output_path
    failed = Signal(str, str)    # job_id, error_message
    progress = Signal(str, int)  # job_id, percentage


class ConversionTask(QRunnable):
    """Runnable task executed within QThreadPool."""

    def __init__(self, job: ConversionJob):
        super().__init__()
        self.job = job
        self.signals = JobSignals()
        self.setAutoDelete(False)  # Retain task memory until caller releases it

    def run(self):
        self.signals.started.emit(self.job.job_id)
        try:
            out_path = dispatch_conversion(self.job)
            self.signals.finished.emit(self.job.job_id, str(out_path))
        except Exception as exc:
            user_msg = format_error_message(exc)
            self.signals.failed.emit(self.job.job_id, user_msg)
