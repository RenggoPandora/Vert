"""Format routing and detection for Vert file conversions."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileCategory(str, Enum):
    OFFICE = "Office Document"
    PDF = "PDF Document"
    IMAGE = "Image"
    MEDIA = "Audio & Video"
    DATA = "Structured Data"
    UNSUPPORTED = "Unsupported"


# Mapping from normalized extension to category
EXTENSION_CATEGORY_MAP: dict[str, FileCategory] = {
    # Office
    ".docx": FileCategory.OFFICE,
    ".xlsx": FileCategory.DATA,  # Can also be routed as data or office depending on target
    ".pptx": FileCategory.OFFICE,
    # PDF
    ".pdf": FileCategory.PDF,
    # Images
    ".png": FileCategory.IMAGE,
    ".jpg": FileCategory.IMAGE,
    ".jpeg": FileCategory.IMAGE,
    ".webp": FileCategory.IMAGE,
    ".bmp": FileCategory.IMAGE,
    ".ico": FileCategory.IMAGE,
    ".tiff": FileCategory.IMAGE,
    ".tif": FileCategory.IMAGE,
    # Media
    ".mp4": FileCategory.MEDIA,
    ".mkv": FileCategory.MEDIA,
    ".avi": FileCategory.MEDIA,
    ".mov": FileCategory.MEDIA,
    ".mp3": FileCategory.MEDIA,
    ".wav": FileCategory.MEDIA,
    ".flac": FileCategory.MEDIA,
    # Data
    ".csv": FileCategory.DATA,
    ".json": FileCategory.DATA,
}


@dataclass(frozen=True)
class TargetFormatOption:
    extension: str
    label: str
    description: str


# Valid targets per category / extension
TARGET_FORMATS_MAP: dict[str, list[TargetFormatOption]] = {
    # Office documents
    ".docx": [
        TargetFormatOption(".pdf", "PDF", "Portable Document Format"),
    ],
    ".pptx": [
        TargetFormatOption(".pdf", "PDF", "Portable Document Format"),
    ],
    # PDF
    ".pdf": [
        TargetFormatOption(".docx", "Word (.docx)", "Editable Word document"),
        TargetFormatOption(".xlsx", "Excel (.xlsx)", "Extracted tabular data"),
        TargetFormatOption(".png", "PNG Images (.png)", "Rendered page images"),
        TargetFormatOption(".jpg", "JPG Images (.jpg)", "Rendered page images"),
    ],
    # Image formats
    ".png": [
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".webp", "WebP (.webp)", "Modern web image format"),
        TargetFormatOption(".ico", "Icon (.ico)", "Windows icon format"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Single-page document"),
        TargetFormatOption(".bmp", "Bitmap (.bmp)", "Uncompressed image"),
    ],
    ".jpg": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".webp", "WebP (.webp)", "Modern web image format"),
        TargetFormatOption(".ico", "Icon (.ico)", "Windows icon format"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Single-page document"),
    ],
    ".jpeg": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".webp", "WebP (.webp)", "Modern web image format"),
        TargetFormatOption(".ico", "Icon (.ico)", "Windows icon format"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Single-page document"),
    ],
    ".webp": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".ico", "Icon (.ico)", "Windows icon format"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Single-page document"),
    ],
    ".bmp": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".webp", "WebP (.webp)", "Modern web image format"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Single-page document"),
    ],
    ".ico": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".webp", "WebP (.webp)", "Modern web image format"),
    ],
    ".tiff": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Multi-page or single-page document"),
    ],
    ".tif": [
        TargetFormatOption(".png", "PNG (.png)", "Lossless image"),
        TargetFormatOption(".jpg", "JPEG (.jpg)", "Standard compressed image"),
        TargetFormatOption(".pdf", "PDF (.pdf)", "Multi-page or single-page document"),
    ],
    # Data & Spreadsheet
    ".xlsx": [
        TargetFormatOption(".pdf", "PDF (.pdf)", "Document export via Office/LibreOffice"),
        TargetFormatOption(".csv", "CSV (.csv)", "Comma-separated values"),
        TargetFormatOption(".json", "JSON (.json)", "Structured JSON records"),
    ],
    ".csv": [
        TargetFormatOption(".xlsx", "Excel (.xlsx)", "Workbook spreadsheet"),
        TargetFormatOption(".json", "JSON (.json)", "Structured JSON records"),
    ],
    ".json": [
        TargetFormatOption(".csv", "CSV (.csv)", "Comma-separated values (flat array)"),
        TargetFormatOption(".xlsx", "Excel (.xlsx)", "Workbook spreadsheet (flat array)"),
    ],
    # Media formats
    ".mp4": [
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Extracted audio"),
        TargetFormatOption(".wav", "WAV Audio (.wav)", "Uncompressed audio"),
        TargetFormatOption(".gif", "Animated GIF (.gif)", "Short looping animation"),
        TargetFormatOption(".mkv", "MKV Video (.mkv)", "Matroska container"),
    ],
    ".mkv": [
        TargetFormatOption(".mp4", "MP4 Video (.mp4)", "Standard MP4 container"),
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Extracted audio"),
        TargetFormatOption(".wav", "WAV Audio (.wav)", "Uncompressed audio"),
    ],
    ".avi": [
        TargetFormatOption(".mp4", "MP4 Video (.mp4)", "Standard MP4 container"),
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Extracted audio"),
    ],
    ".mov": [
        TargetFormatOption(".mp4", "MP4 Video (.mp4)", "Standard MP4 container"),
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Extracted audio"),
        TargetFormatOption(".gif", "Animated GIF (.gif)", "Short looping animation"),
    ],
    ".mp3": [
        TargetFormatOption(".wav", "WAV Audio (.wav)", "Uncompressed audio"),
        TargetFormatOption(".flac", "FLAC Audio (.flac)", "Lossless audio"),
    ],
    ".wav": [
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Compressed audio"),
        TargetFormatOption(".flac", "FLAC Audio (.flac)", "Lossless audio"),
    ],
    ".flac": [
        TargetFormatOption(".mp3", "MP3 Audio (.mp3)", "Compressed audio"),
        TargetFormatOption(".wav", "WAV Audio (.wav)", "Uncompressed audio"),
    ],
}


def normalize_extension(filepath_or_ext: str | Path) -> str:
    """Extract lowercased extension with leading dot."""
    if isinstance(filepath_or_ext, Path):
        ext = filepath_or_ext.suffix.lower()
        if ext:
            return ext
        s = filepath_or_ext.name.strip().lower()
    else:
        s = str(filepath_or_ext).strip().lower()

    if not s:
        return ""
    if s.startswith(".") and s.count(".") == 1 and "/" not in s and "\\" not in s:
        return s
    suffix = Path(s).suffix.lower()
    if suffix:
        return suffix
    return f".{s}"


def get_file_category(filepath_or_ext: str | Path) -> FileCategory:
    """Determine category from file path or extension."""
    ext = normalize_extension(filepath_or_ext)
    return EXTENSION_CATEGORY_MAP.get(ext, FileCategory.UNSUPPORTED)


def get_target_formats(filepath_or_ext: str | Path) -> list[TargetFormatOption]:
    """Retrieve allowed target format options for given file or extension."""
    ext = normalize_extension(filepath_or_ext)
    return TARGET_FORMATS_MAP.get(ext, [])


def is_conversion_supported(src_ext: str | Path, dst_ext: str | Path) -> bool:
    """Validate whether input can convert to target."""
    src = normalize_extension(src_ext)
    dst = normalize_extension(dst_ext)
    targets = [opt.extension for opt in get_target_formats(src)]
    return dst in targets
