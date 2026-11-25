"""Image compression adapter for JPEG, WebP, PNG, and common raster formats."""

import io
import os
from pathlib import Path
from typing import Callable, Optional
from PIL import Image

from core.compression.base import (
    CompressionAdapter,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
    format_bytes_human,
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


class ImageCompressionAdapter(CompressionAdapter):
    """Adapter handling raster image compression with iterative target-size optimization."""

    def can_handle(self, src_path: Path) -> bool:
        return src_path.suffix.lower() in IMAGE_EXTENSIONS

    def compress(
        self,
        request: CompressionRequest,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> CompressionResult:
        src = Path(request.src_path).resolve()
        dst = request.dst_path or compute_safe_output_path(src, request.output_dir)
        orig_size = src.stat().st_size

        # Determine target size in bytes if provided
        target_bytes = request.target_size_bytes
        if target_bytes is None and request.target_percent is not None:
            # e.g., target_percent=50 means target 50% of original size
            target_bytes = max(1024, int(orig_size * (1.0 - (request.target_percent / 100.0))))

        ext = dst.suffix.lower()
        if ext in {".jpg", ".jpeg"}:
            fmt = "JPEG"
        elif ext == ".webp":
            fmt = "WEBP"
        elif ext == ".png":
            fmt = "PNG"
        else:
            fmt = "JPEG"

        with Image.open(src) as img:
            # Preserve orientation & convert modes if needed for JPEG
            if fmt == "JPEG" and img.mode in ("RGBA", "P"):
                img_work = img.convert("RGB")
            else:
                img_work = img.copy()

            # Apply resolution scaling if requested
            if request.resolution_scale < 1.0:
                new_w = max(1, int(img_work.width * request.resolution_scale))
                new_h = max(1, int(img_work.height * request.resolution_scale))
                img_work = img_work.resize((new_w, new_h), Image.Resampling.LANCZOS)

            iterations = 0
            best_candidate_bytes = None
            best_candidate_data: Optional[bytes] = None

            # If no specific target size, run single-pass with requested or default quality
            if target_bytes is None:
                iterations = 1
                q = request.quality or (75 if request.preset == "balanced" else (50 if request.preset == "maximum" else 85))
                buf = io.BytesIO()
                self._save_image(img_work, buf, fmt, q)
                candidate_data = buf.getvalue()
                best_candidate_data = candidate_data
                best_candidate_bytes = len(candidate_data)
                target_achieved = True
                unachievable_reason = None
            else:
                # Bounded binary search on quality (max 5 iterations)
                low_q = 10
                high_q = 90
                max_iter = 5
                target_achieved = False
                unachievable_reason = None

                while iterations < max_iter and low_q <= high_q:
                    if is_cancelled and is_cancelled():
                        raise InterruptedError("Compression cancelled by user.")

                    iterations += 1
                    mid_q = (low_q + high_q) // 2
                    if progress_callback:
                        progress_callback(
                            (iterations / max_iter) * 80,
                            f"Testing compression iteration {iterations}/{max_iter} (Quality {mid_q})...",
                        )

                    buf = io.BytesIO()
                    self._save_image(img_work, buf, fmt, mid_q)
                    candidate = buf.getvalue()
                    candidate_len = len(candidate)

                    if best_candidate_bytes is None or abs(candidate_len - target_bytes) < abs(best_candidate_bytes - target_bytes):
                        best_candidate_bytes = candidate_len
                        best_candidate_data = candidate

                    if candidate_len <= target_bytes:
                        target_achieved = True
                        # Can we achieve better quality while still <= target?
                        low_q = mid_q + 1
                    else:
                        high_q = mid_q - 1

                if not target_achieved:
                    unachievable_reason = (
                        f"Target size ({format_bytes_human(target_bytes)}) too small without further dimension scaling. "
                        f"Best achieved: {format_bytes_human(best_candidate_bytes)}."
                    )

            if best_candidate_data is None:
                raise RuntimeError("Failed to compress image data.")

            # Save best candidate to destination file
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(best_candidate_data)

            final_size = dst.stat().st_size
            savings_bytes = orig_size - final_size
            savings_ratio = max(0.0, savings_bytes / orig_size) if orig_size > 0 else 0.0

            if progress_callback:
                progress_callback(100.0, "Image compression complete.")

            msg = (
                f"Compressed {format_bytes_human(orig_size)} -> {format_bytes_human(final_size)} "
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
                iterations=iterations,
                message=msg,
            )

    def _save_image(self, img: Image.Image, buf: io.BytesIO, fmt: str, quality: int):
        if fmt == "JPEG":
            img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        elif fmt == "WEBP":
            img.save(buf, format="WEBP", quality=quality, method=6)
        elif fmt == "PNG":
            # For PNG with aggressive compression / target search, quantize if low quality
            if quality < 50:
                p_img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=min(256, max(32, quality * 4)))
                p_img.save(buf, format="PNG", optimize=True)
            else:
                img.save(buf, format="PNG", optimize=True)
        else:
            img.save(buf, format=fmt, quality=quality)
