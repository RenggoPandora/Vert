"""Media (video and audio) compression adapter utilizing FFmpeg."""

import os
from pathlib import Path
import re
import subprocess
from typing import Callable, Optional

from core.compression.base import (
    CompressionAdapter,
    CompressionRequest,
    CompressionResult,
    compute_safe_output_path,
    format_bytes_human,
)
from core.media_converter import find_ffmpeg_binary

MEDIA_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".wav", ".flac", ".m4a"}


class MediaCompressionAdapter(CompressionAdapter):
    """Adapter for compressing video and audio files using FFmpeg."""

    def can_handle(self, src_path: Path) -> bool:
        return src_path.suffix.lower() in MEDIA_EXTENSIONS

    def compress(
        self,
        request: CompressionRequest,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> CompressionResult:
        src = Path(request.src_path).resolve()
        dst = request.dst_path or compute_safe_output_path(src, request.output_dir)
        orig_size = src.stat().st_size

        ffmpeg_bin = find_ffmpeg_binary()
        if not ffmpeg_bin:
            raise RuntimeError("ffmpeg.exe not found in engines/ or system PATH.")

        target_bytes = request.target_size_bytes
        if target_bytes is None and request.target_percent is not None:
            target_bytes = max(1024 * 100, int(orig_size * (1.0 - (request.target_percent / 100.0))))

        if progress_callback:
            progress_callback(10.0, "Probing media duration and streams...")

        # Probe duration
        duration_sec = self._probe_duration(ffmpeg_bin, src)

        cmd = [
            str(ffmpeg_bin),
            "-y",
            "-i",
            str(src),
        ]

        ext = dst.suffix.lower()
        is_video = ext in {".mp4", ".mkv", ".mov", ".avi", ".webm"}

        target_achieved = True
        unachievable_reason = None

        if is_video:
            # Video codec and compression settings
            cmd.extend(["-c:v", "libx264", "-preset", "medium"])

            if target_bytes and duration_sec and duration_sec > 1:
                # Target-size calculation: bitrate = (target_bytes * 8) / duration
                total_bitrate_kbps = int((target_bytes * 8) / (duration_sec * 1000))
                audio_kbps = 64 if total_bitrate_kbps < 300 else 96
                video_kbps = max(50, total_bitrate_kbps - audio_kbps)

                cmd.extend([
                    "-b:v", f"{video_kbps}k",
                    "-maxrate", f"{int(video_kbps * 1.4)}k",
                    "-bufsize", f"{int(video_kbps * 2)}k",
                    "-c:a", "aac",
                    "-b:a", f"{audio_kbps}k",
                ])
                if video_kbps < 150:
                    # Automatically downscale resolution to keep visual quality acceptable
                    cmd.extend(["-vf", "scale=-2:480"])
            else:
                # CRF-based compression
                crf = 28 if request.preset == "balanced" else (34 if request.preset == "maximum" else 24)
                if request.quality:
                    # Invert 1-100 quality into CRF 50..18
                    crf = max(18, min(50, int(50 - (request.quality * 0.32))))
                cmd.extend(["-crf", str(crf), "-c:a", "aac", "-b:a", "96k"])

                if request.resolution_scale < 1.0:
                    cmd.extend(["-vf", f"scale=trunc(iw*{request.resolution_scale}/2)*2:trunc(ih*{request.resolution_scale}/2)*2"])
        else:
            # Audio file compression
            if ext == ".mp3":
                bitrate = "96k" if request.preset == "maximum" else ("128k" if request.preset == "balanced" else "192k")
                cmd.extend(["-vn", "-c:a", "libmp3lame", "-b:a", bitrate])
            elif ext == ".m4a" or ext == ".aac":
                cmd.extend(["-vn", "-c:a", "aac", "-b:a", "96k"])
            else:
                cmd.extend(["-vn", "-c:a", "aac", "-b:a", "128k"])

        cmd.append(str(dst))

        if progress_callback:
            progress_callback(30.0, "Encoding and compressing media stream...")

        creation_flags = 0x08000000 if os.name == "nt" else 0
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creation_flags,
        )

        while True:
            if is_cancelled and is_cancelled():
                proc.kill()
                proc.wait()
                if dst.exists():
                    dst.unlink()
                raise InterruptedError("Media compression cancelled by user.")

            ret = proc.poll()
            if ret is not None:
                break

        if proc.returncode != 0 or not dst.exists() or dst.stat().st_size == 0:
            err = proc.stderr.read() if proc.stderr else ""
            if dst.exists():
                dst.unlink()
            raise RuntimeError(f"FFmpeg compression failed: {err}")

        final_size = dst.stat().st_size
        savings_bytes = orig_size - final_size
        savings_ratio = max(0.0, savings_bytes / orig_size) if orig_size > 0 else 0.0

        if target_bytes and final_size > target_bytes:
            target_achieved = False
            unachievable_reason = (
                f"Output {format_bytes_human(final_size)} exceeded target {format_bytes_human(target_bytes)} "
                f"due to stream container and audio track minimum bitrate overhead."
            )

        if progress_callback:
            progress_callback(100.0, "Media compression complete.")

        msg = (
            f"Compressed media: {format_bytes_human(orig_size)} -> {format_bytes_human(final_size)} "
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

    def _probe_duration(self, ffmpeg_bin: Path, src: Path) -> Optional[float]:
        try:
            creation_flags = 0x08000000 if os.name == "nt" else 0
            res = subprocess.run(
                [str(ffmpeg_bin), "-i", str(src)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags,
            )
            match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", res.stderr)
            if match:
                h, m, s = match.groups()
                return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception:
            pass
        return None
