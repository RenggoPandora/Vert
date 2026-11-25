"""Archive compression adapter for ZIP archives."""

from pathlib import Path
from typing import Callable, Optional
import zipfile

from core.compression.base import (
    CompressionAdapter,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
    format_bytes_human,
)


class ArchiveCompressionAdapter(CompressionAdapter):
    """Adapter for recompressing ZIP archives at maximum deflate compression."""

    def can_handle(self, src_path: Path) -> bool:
        return src_path.suffix.lower() == ".zip"

    def compress(
        self,
        request: CompressionRequest,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> CompressionResult:
        src = Path(request.src_path).resolve()
        dst = request.dst_path or compute_safe_output_path(src, request.output_dir)
        orig_size = src.stat().st_size

        if progress_callback:
            progress_callback(10.0, "Reading archive entries...")

        with zipfile.ZipFile(src, "r") as src_zf:
            entries = src_zf.infolist()
            total = len(entries)

            with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dst_zf:
                for idx, entry in enumerate(entries, start=1):
                    if is_cancelled and is_cancelled():
                        dst_zf.close()
                        if dst.exists():
                            dst.unlink()
                        raise InterruptedError("Archive compression cancelled by user.")

                    data = src_zf.read(entry.filename)
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    dst_zf.writestr(entry, data)

                    if progress_callback and total > 0:
                        pct = 10.0 + (idx / total) * 85.0
                        progress_callback(pct, f"Compressing entry {idx}/{total}: {entry.filename}")

        final_size = dst.stat().st_size
        savings_bytes = orig_size - final_size
        savings_ratio = max(0.0, savings_bytes / orig_size) if orig_size > 0 else 0.0

        target_bytes = request.target_size_bytes
        target_achieved = True
        unachievable_reason = None
        if target_bytes and final_size > target_bytes:
            target_achieved = False
            unachievable_reason = (
                f"Target size ({format_bytes_human(target_bytes)}) unachievable for pre-compressed archive content. "
                f"Best achieved: {format_bytes_human(final_size)}."
            )

        if progress_callback:
            progress_callback(100.0, "Archive compression complete.")

        msg = (
            f"Compressed archive: {format_bytes_human(orig_size)} -> {format_bytes_human(final_size)} "
            f"({savings_ratio * 100:.1f}% reduction)."
        )

        return CompressionResult(
            success=True,
            src_path=src,
            dst_path=dst,
            original_size_bytes=orig_size,
            compressed_size_bytes=final_size,
            savings_bytes=savings_bytes,
            savings_ratio=savings_ratio,
            target_achieved=target_achieved,
            target_unachievable_reason=unachievable_reason,
            iterations=1,
            message=msg,
        )
