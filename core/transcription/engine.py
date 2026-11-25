"""Local whisper.cpp speech recognition engine execution."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Callable, List, Optional, Tuple

from core.transcription.audio_preprocessor import preprocess_audio_for_whisper
from core.transcription.exporters import TranscriptSegment, TranscriptionResult
from core.transcription.models import get_model_path, is_model_installed

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENGINES_DIR = ROOT_DIR / "engines"

# Whisper.cpp regex pattern: [00:00:00.000 --> 00:00:04.500]   text
TIMESTAMP_LINE_REGEX = re.compile(
    r"\[(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\]\s*(.*)"
)


def find_whisper_binary() -> Optional[Path]:
    """Find whisper.cpp CLI executable in engines/ or system PATH."""
    candidates = [
        ENGINES_DIR / "whisper-cli.exe",
        ENGINES_DIR / "whisper.exe",
        ENGINES_DIR / "main.exe",
        ENGINES_DIR / "whisper-cli",
        ENGINES_DIR / "whisper",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    for name in ("whisper-cli", "whisper", "main"):
        sys_bin = shutil.which(name)
        if sys_bin:
            return Path(sys_bin)

    return None


def parse_timestamp_to_ms(hours: str, mins: str, secs: str, millis: str) -> int:
    """Convert timestamp components into total milliseconds."""
    return (
        int(hours) * 3600000
        + int(mins) * 60000
        + int(secs) * 1000
        + int(millis)
    )


def parse_whisper_output_text(output_text: str) -> List[TranscriptSegment]:
    """Parse whisper.cpp stdout lines into TranscriptSegments."""
    segments: List[TranscriptSegment] = []
    lines = output_text.splitlines()

    for line in lines:
        line_clean = line.strip()
        match = TIMESTAMP_LINE_REGEX.match(line_clean)
        if match:
            h1, m1, s1, ms1, h2, m2, s2, ms2, seg_text = match.groups()
            start_ms = parse_timestamp_to_ms(h1, m1, s1, ms1)
            end_ms = parse_timestamp_to_ms(h2, m2, s2, ms2)
            clean_text = seg_text.strip()
            if clean_text:
                segments.append(TranscriptSegment(start_ms=start_ms, end_ms=end_ms, text=clean_text))

    return segments


def run_transcription(
    audio_path: Path | str,
    model_name: str = "base",
    language: str = "auto",
    threads: int = 4,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
) -> TranscriptionResult:
    """Execute speech recognition on an audio file using whisper.cpp."""
    whisper_bin = find_whisper_binary()
    if not whisper_bin:
        raise RuntimeError(
            "whisper.cpp engine executable not found in engines/ or system PATH.\n"
            "Please place whisper-cli.exe in engines/ or run scripts/download_engines.py --whisper."
        )

    model_path = get_model_path(model_name)
    if not model_path:
        raise FileNotFoundError(
            f"Whisper model '{model_name}' is not installed.\n"
            f"Please download the '{model_name}' model first via the Model Manager."
        )

    if progress_callback:
        progress_callback(10.0, "Preprocessing audio to 16kHz WAV...")

    if is_cancelled and is_cancelled():
        raise InterruptedError("Transcription cancelled by user.")

    # Convert audio to 16kHz mono WAV
    temp_wav = preprocess_audio_for_whisper(audio_path)

    try:
        if is_cancelled and is_cancelled():
            raise InterruptedError("Transcription cancelled by user.")

        if progress_callback:
            progress_callback(30.0, f"Running local transcription with '{model_name}' model...")

        cmd = [
            str(whisper_bin),
            "-m",
            str(model_path),
            "-f",
            str(temp_wav),
            "-t",
            str(max(1, threads)),
            "-pp",  # print progress
        ]

        if language and language.lower() != "auto":
            cmd.extend(["-l", language.lower()])
        else:
            cmd.extend(["-l", "auto"])

        creation_flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation_flags,
        )

        stdout_lines: list[str] = []
        while True:
            if is_cancelled and is_cancelled():
                proc.kill()
                proc.wait()
                raise InterruptedError("Transcription cancelled by user.")

            ret = proc.poll()
            if ret is not None:
                remaining_stdout, _ = proc.communicate()
                if remaining_stdout:
                    stdout_lines.append(remaining_stdout)
                break

            line = proc.stdout.readline() if proc.stdout else ""
            if line:
                stdout_lines.append(line)
                if progress_callback:
                    # Provide visual progress pulse
                    progress_callback(60.0, "Transcribing speech segments...")

        if proc.returncode != 0:
            stderr_out = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(f"whisper.cpp returned exit code {proc.returncode}: {stderr_out}")

        full_raw_output = "".join(stdout_lines)
        segments = parse_whisper_output_text(full_raw_output)

        if not segments:
            # Check if whisper simply printed unbracketed text
            clean_lines = [l.strip() for l in stdout_lines if l.strip() and not l.startswith("whisper_")]
            fallback_text = " ".join(clean_lines)
            if fallback_text:
                segments = [TranscriptSegment(start_ms=0, end_ms=5000, text=fallback_text)]

        full_text = " ".join(s.text for s in segments)
        duration_sec = (segments[-1].end_ms / 1000.0) if segments else 0.0

        if progress_callback:
            progress_callback(100.0, "Transcription finished successfully.")

        return TranscriptionResult(
            language=language,
            model=model_name,
            duration_sec=duration_sec,
            full_text=full_text,
            segments=segments,
        )

    finally:
        # Guarantee temp WAV cleanup
        if temp_wav.exists():
            try:
                temp_wav.unlink()
            except OSError:
                pass
