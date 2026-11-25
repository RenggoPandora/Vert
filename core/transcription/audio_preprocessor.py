"""Audio validation and preprocessing for speech recognition."""

import os
from pathlib import Path
import subprocess
import tempfile
from typing import Optional

from core.media_converter import find_ffmpeg_binary

SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma"}


def validate_audio_file(file_path: Path | str) -> Path:
    """Validate that audio file exists and has a supported extension."""
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Audio file is empty (0 bytes): {path.name}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
        )

    return path


def preprocess_audio_for_whisper(
    src_path: Path | str,
    output_wav_path: Optional[Path | str] = None,
    timeout: int = 300,
) -> Path:
    """Convert audio to 16kHz 16-bit mono PCM WAV for whisper.cpp."""
    src = validate_audio_file(src_path)
    ffmpeg_bin = find_ffmpeg_binary()
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg.exe not found. Required for audio preprocessing.")

    if output_wav_path is None:
        fd, tmp = tempfile.mkstemp(prefix="vert_whisper_", suffix=".wav")
        os.close(fd)
        out_wav = Path(tmp).resolve()
    else:
        out_wav = Path(output_wav_path).resolve()
        out_wav.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(ffmpeg_bin),
        "-y",
        "-i",
        str(src),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(out_wav),
    ]

    creation_flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        creationflags=creation_flags,
    )

    if proc.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size == 0:
        if out_wav.exists():
            out_wav.unlink()
        err_msg = proc.stderr.strip() if proc.stderr else f"FFmpeg returned code {proc.returncode}"
        raise RuntimeError(f"Audio preprocessing failed: {err_msg}")

    return out_wav
