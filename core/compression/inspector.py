"""Metadata and format inspection for compressible files."""

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import Optional

from PIL import Image
import fitz  # PyMuPDF
import zipfile

from core.compression.base import CompressionCategory, format_bytes_human
from core.media_converter import find_ffmpeg_binary


@dataclass
class FileMetadata:
    path: Path
    extension: str
    category: CompressionCategory
    size_bytes: int
    size_human: str
    width: Optional[int] = None
    height: Optional[int] = None
    page_count: Optional[int] = None
    duration_sec: Optional[float] = None
    details_summary: str = ""


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
PDF_EXTS = {".pdf"}
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
ARCHIVE_EXTS = {".zip", ".7z", ".tar", ".gz"}


def categorize_file(path: Path | str) -> CompressionCategory:
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTS:
        return CompressionCategory.IMAGE
    elif ext in PDF_EXTS:
        return CompressionCategory.PDF
    elif ext in VIDEO_EXTS:
        return CompressionCategory.VIDEO
    elif ext in ARCHIVE_EXTS:
        return CompressionCategory.ARCHIVE
    return CompressionCategory.UNSUPPORTED


def inspect_file(file_path: Path | str) -> FileMetadata:
    """Inspect file properties, format, and dimension/page/duration metadata."""
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    size_bytes = path.stat().st_size
    size_human = format_bytes_human(size_bytes)
    ext = path.suffix.lower()
    cat = categorize_file(path)

    width = None
    height = None
    page_count = None
    duration_sec = None
    summary_parts = [f"Size: {size_human}"]

    if cat == CompressionCategory.IMAGE:
        try:
            with Image.open(path) as img:
                width, height = img.size
                summary_parts.append(f"Dimensions: {width}x{height}px")
                summary_parts.append(f"Mode: {img.mode}")
        except Exception:
            pass

    elif cat == CompressionCategory.PDF:
        try:
            doc = fitz.open(str(path))
            page_count = len(doc)
            doc.close()
            summary_parts.append(f"Pages: {page_count}")
        except Exception:
            pass

    elif cat == CompressionCategory.VIDEO:
        ffmpeg_bin = find_ffmpeg_binary()
        if ffmpeg_bin:
            try:
                creation_flags = 0x08000000 if os.name == "nt" else 0
                cmd = [str(ffmpeg_bin), "-i", str(path)]
                res = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=creation_flags,
                )
                output = res.stderr
                # Parse Duration: 00:01:23.45
                import re
                dur_match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", output)
                if dur_match:
                    h, m, s = dur_match.groups()
                    duration_sec = int(h) * 3600 + int(m) * 60 + float(s)
                    summary_parts.append(f"Duration: {duration_sec:.1f}s")
                # Parse Video resolution: Stream #0:0: Video: ..., 1920x1080
                res_match = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", output)
                if res_match:
                    width = int(res_match.group(1))
                    height = int(res_match.group(2))
                    summary_parts.append(f"Resolution: {width}x{height}px")
            except Exception:
                pass

    elif cat == CompressionCategory.ARCHIVE and ext == ".zip":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                file_count = len(zf.namelist())
                summary_parts.append(f"Entries: {file_count} files")
        except Exception:
            pass

    return FileMetadata(
        path=path,
        extension=ext,
        category=cat,
        size_bytes=size_bytes,
        size_human=size_human,
        width=width,
        height=height,
        page_count=page_count,
        duration_sec=duration_sec,
        details_summary=" • ".join(summary_parts),
    )
