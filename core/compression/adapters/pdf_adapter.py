"""PDF document compression adapter using PyMuPDF (fitz) stream deflation and image re-encoding."""

import io
import os
from pathlib import Path
from typing import Callable, Optional
from PIL import Image
import pymupdf as fitz

from core.compression.base import (
    CompressionAdapter,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
    format_bytes_human,
)


class PdfCompressionAdapter(CompressionAdapter):
    """Adapter for compressing PDF documents via stream deflation and image re-compression."""

    def can_handle(self, src_path: Path) -> bool:
        return src_path.suffix.lower() == ".pdf"

    def compress(
        self,
        request: CompressionRequest,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> CompressionResult:
        src = Path(request.src_path).resolve()
        dst = request.dst_path or compute_safe_output_path(src, request.output_dir)
        orig_size = src.stat().st_size

        target_bytes = request.target_size_bytes
        if target_bytes is None and request.target_percent is not None:
            target_bytes = max(1024, int(orig_size * (1.0 - (request.target_percent / 100.0))))

        if progress_callback:
            progress_callback(10.0, "Analyzing PDF structure and streams...")

        iterations = 0
        best_candidate_bytes = None
        best_candidate_path: Optional[Path] = None
        target_achieved = False
        unachievable_reason = None

        # Level 1: Standard stream deflation & garbage collection
        iterations += 1
        temp_dst1 = dst.parent / f"{dst.stem}_temp1.pdf"
        try:
            doc = fitz.open(str(src))
            # PyMuPDF standard optimization save options
            doc.save(
                str(temp_dst1),
                garbage=4,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
                clean=True,
            )
            doc.close()

            cand1_size = temp_dst1.stat().st_size
            best_candidate_bytes = cand1_size
            best_candidate_path = temp_dst1

            if target_bytes is None or cand1_size <= target_bytes:
                target_achieved = True
            else:
                # Level 2: Embedded image downsampling / re-encoding if target not reached
                if is_cancelled and is_cancelled():
                    raise InterruptedError("Compression cancelled by user.")

                iterations += 1
                if progress_callback:
                    progress_callback(50.0, "Re-compressing embedded PDF images...")

                temp_dst2 = dst.parent / f"{dst.stem}_temp2.pdf"
                self._compress_embedded_images(src, temp_dst2, quality=60, scale=0.75)
                cand2_size = temp_dst2.stat().st_size

                if cand2_size < best_candidate_bytes:
                    best_candidate_bytes = cand2_size
                    best_candidate_path = temp_dst2

                if cand2_size <= target_bytes:
                    target_achieved = True
                else:
                    # Level 3: Maximum image re-compression
                    iterations += 1
                    if progress_callback:
                        progress_callback(75.0, "Applying maximum image compression...")
                    temp_dst3 = dst.parent / f"{dst.stem}_temp3.pdf"
                    self._compress_embedded_images(src, temp_dst3, quality=40, scale=0.5)
                    cand3_size = temp_dst3.stat().st_size

                    if cand3_size < best_candidate_bytes:
                        best_candidate_bytes = cand3_size
                        best_candidate_path = temp_dst3

                    if cand3_size <= target_bytes:
                        target_achieved = True
                    else:
                        unachievable_reason = (
                            f"Target size ({format_bytes_human(target_bytes)}) unachievable without "
                            f"stripping text/vector content. Best achieved: {format_bytes_human(best_candidate_bytes)}."
                        )

            # Move best candidate to final dst
            if best_candidate_path and best_candidate_path.exists():
                if dst.exists():
                    dst.unlink()
                best_candidate_path.rename(dst)

            final_size = dst.stat().st_size
            savings_bytes = orig_size - final_size
            savings_ratio = max(0.0, savings_bytes / orig_size) if orig_size > 0 else 0.0

            if progress_callback:
                progress_callback(100.0, "PDF compression complete.")

            msg = (
                f"Compressed PDF: {format_bytes_human(orig_size)} -> {format_bytes_human(final_size)} "
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

        finally:
            # Clean any leftover temp files
            for p in (dst.parent / f"{dst.stem}_temp1.pdf", dst.parent / f"{dst.stem}_temp2.pdf", dst.parent / f"{dst.stem}_temp3.pdf"):
                if p.exists() and p != dst:
                    try:
                        p.unlink()
                    except OSError:
                        pass

    def _compress_embedded_images(self, src_pdf: Path, out_pdf: Path, quality: int = 60, scale: float = 0.75):
        """Downscale and re-encode raster images embedded in PDF."""
        doc = fitz.open(str(src_pdf))
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                base_img = doc.extract_image(xref)
                if not base_img:
                    continue

                img_bytes = base_img["image"]
                img_ext = base_img["ext"]
                try:
                    with Image.open(io.BytesIO(img_bytes)) as pil_img:
                        if scale < 1.0:
                            new_w = max(1, int(pil_img.width * scale))
                            new_h = max(1, int(pil_img.height * scale))
                            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                        buf = io.BytesIO()
                        if pil_img.mode in ("RGBA", "P"):
                            pil_img = pil_img.convert("RGB")
                        pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                        doc.update_stream(xref, buf.getvalue())
                except Exception:
                    continue

        doc.save(
            str(out_pdf),
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True,
        )
        doc.close()
