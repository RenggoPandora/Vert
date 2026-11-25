"""Multi-format exporters for audio transcription results."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import List


@dataclass
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str

    @property
    def start_str_srt(self) -> str:
        return ms_to_timestamp(self.start_ms, srt_format=True)

    @property
    def end_str_srt(self) -> str:
        return ms_to_timestamp(self.end_ms, srt_format=True)

    @property
    def start_str_vtt(self) -> str:
        return ms_to_timestamp(self.start_ms, srt_format=False)

    @property
    def end_str_vtt(self) -> str:
        return ms_to_timestamp(self.end_ms, srt_format=False)


@dataclass
class TranscriptionResult:
    language: str
    model: str
    duration_sec: float
    full_text: str
    segments: List[TranscriptSegment]


def ms_to_timestamp(ms: int, srt_format: bool = True) -> str:
    """Format milliseconds into HH:MM:SS,mmm or HH:MM:SS.mmm."""
    ms = max(0, int(ms))
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    millis = ms % 1000
    separator = "," if srt_format else "."
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}"


def export_to_txt(result: TranscriptionResult, dest_path: Path | str) -> Path:
    """Export plain transcript text."""
    path = Path(dest_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = result.full_text.strip()
    if not text and result.segments:
        text = " ".join(s.text.strip() for s in result.segments if s.text.strip())
    path.write_text(text, encoding="utf-8")
    return path


def export_to_srt(result: TranscriptionResult, dest_path: Path | str) -> Path:
    """Export SubRip (SRT) format."""
    path = Path(dest_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    segments = result.segments
    if not segments and result.full_text:
        # Fallback single block
        segments = [TranscriptSegment(0, int(result.duration_sec * 1000) or 5000, result.full_text)]

    for idx, seg in enumerate(segments, start=1):
        lines.append(str(idx))
        lines.append(f"{seg.start_str_srt} --> {seg.end_str_srt}")
        lines.append(seg.text.strip())
        lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path


def export_to_vtt(result: TranscriptionResult, dest_path: Path | str) -> Path:
    """Export WebVTT (VTT) format."""
    path = Path(dest_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["WEBVTT", ""]

    segments = result.segments
    if not segments and result.full_text:
        segments = [TranscriptSegment(0, int(result.duration_sec * 1000) or 5000, result.full_text)]

    for idx, seg in enumerate(segments, start=1):
        lines.append(f"{seg.start_str_vtt} --> {seg.end_str_vtt}")
        lines.append(seg.text.strip())
        lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path


def export_to_json(result: TranscriptionResult, dest_path: Path | str) -> Path:
    """Export structured JSON format."""
    path = Path(dest_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "language": result.language,
        "model": result.model,
        "duration_sec": result.duration_sec,
        "full_text": result.full_text,
        "segments": [asdict(seg) for seg in result.segments],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
