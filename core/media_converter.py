"""Media conversion module utilizing ffmpeg."""

import os
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ENGINES_DIR = ROOT_DIR / "engines"


def find_ffmpeg_binary() -> Path | None:
    """Find ffmpeg.exe in bundled engines or system PATH."""
    bundled = ENGINES_DIR / "ffmpeg.exe"
    if bundled.exists():
        return bundled

    sys_bin = shutil.which("ffmpeg")
    if sys_bin:
        return Path(sys_bin)

    return None


def convert_media(
    src_path: Path | str,
    dst_path: Path | str,
    timeout: int = 600,
) -> Path:
    """Convert audio or video file using ffmpeg."""
    src = Path(src_path).resolve()
    dst = Path(dst_path).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = find_ffmpeg_binary()
    if not ffmpeg_bin:
        raise RuntimeError(
            "ffmpeg.exe not found in engines/ or system PATH. "
            "Please run scripts/download_engines.py --ffmpeg or install ffmpeg."
        )

    dst_ext = dst.suffix.lower()

    cmd = [
        str(ffmpeg_bin),
        "-y",  # Overwrite temp/destination file
        "-i",
        str(src),
    ]

    # Specific format flags
    if dst_ext == ".gif":
        # Generate high quality GIF palette filter
        cmd.extend(["-vf", "fps=10,scale=480:-1:flags=lanczos", "-c:v", "gif"])
    elif dst_ext == ".mp3":
        cmd.extend(["-vn", "-acodec", "libmp3lame", "-q:a", "2"])
    elif dst_ext == ".wav":
        cmd.extend(["-vn", "-acodec", "pcm_s16le"])
    elif dst_ext == ".flac":
        cmd.extend(["-vn", "-acodec", "flac"])
    elif dst_ext == ".mp4":
        cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac"])

    cmd.append(str(dst))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0 or not dst.exists():
        raise RuntimeError(
            f"FFmpeg conversion failed (exit code {result.returncode}). "
            f"Error details: {result.stderr[-500:].strip() if result.stderr else 'Unknown error'}"
        )

    return dst
