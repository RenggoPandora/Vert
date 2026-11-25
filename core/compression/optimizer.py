"""Compression coordinator and Target-Size Optimizer for Vert."""

from pathlib import Path
from typing import Callable, List, Optional

from core.compression.adapters.archive_adapter import ArchiveCompressionAdapter
from core.compression.adapters.image_adapter import ImageCompressionAdapter
from core.compression.adapters.media_adapter import MediaCompressionAdapter
from core.compression.adapters.pdf_adapter import PdfCompressionAdapter
from core.compression.base import (
    CompressionAdapter,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
)

ADAPTERS: List[CompressionAdapter] = [
    ImageCompressionAdapter(),
    PdfCompressionAdapter(),
    MediaCompressionAdapter(),
    ArchiveCompressionAdapter(),
]


def find_adapter(src_path: Path | str) -> Optional[CompressionAdapter]:
    """Find appropriate compression adapter for given file path."""
    path = Path(src_path).resolve()
    for adapter in ADAPTERS:
        if adapter.can_handle(path):
            return adapter
    return None


def compress_file(
    request: CompressionRequest,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
) -> CompressionResult:
    """Execute optimized file compression according to request specifications."""
    src = Path(request.src_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")
    if not src.is_file():
        raise ValueError(f"Path is not a file: {src}")
    if src.stat().st_size == 0:
        raise ValueError(f"File is empty (0 bytes): {src.name}")

    adapter = find_adapter(src)
    if not adapter:
        raise ValueError(f"No compression adapter available for '{src.suffix}' format.")

    # Execute compression
    result = adapter.compress(
        request=request,
        progress_callback=progress_callback,
        is_cancelled=is_cancelled,
    )

    return result
