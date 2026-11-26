"""Unit tests for Audio-to-Text foundation (models, preprocessor, exporters, engine)."""

import json
from pathlib import Path
import tempfile
import pytest

from core.transcription.audio_preprocessor import (
    SUPPORTED_AUDIO_EXTENSIONS,
    preprocess_audio_for_whisper,
    validate_audio_file,
)
from core.transcription.engine import (
    parse_timestamp_to_ms,
    parse_whisper_output_text,
)
from core.transcription.exporters import (
    TranscriptSegment,
    TranscriptionResult,
    export_to_json,
    export_to_srt,
    export_to_txt,
    export_to_vtt,
    ms_to_timestamp,
)
from core.transcription.models import (
    MODEL_CATALOG,
    get_model_path,
    is_model_installed,
)


def test_model_catalog_entries():
    assert "tiny" in MODEL_CATALOG
    assert "base" in MODEL_CATALOG
    assert "small" in MODEL_CATALOG
    assert "medium" in MODEL_CATALOG
    assert MODEL_CATALOG["base"].filename == "ggml-base.bin"
    assert MODEL_CATALOG["base"].size_mb > 100


def test_audio_validator_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        validate_audio_file("non_existent_audio_file.mp3")


def test_audio_validator_rejects_unsupported_ext(tmp_path):
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not audio")
    with pytest.raises(ValueError, match="Unsupported audio format"):
        validate_audio_file(bad_file)


def test_audio_validator_rejects_empty_file(tmp_path):
    empty_file = tmp_path / "empty.wav"
    empty_file.touch()
    with pytest.raises(ValueError, match="empty"):
        validate_audio_file(empty_file)


def test_audio_validator_accepts_valid_file(tmp_path):
    sample = tmp_path / "valid.mp3"
    sample.write_bytes(b"dummy mp3 content header")
    validated = validate_audio_file(sample)
    assert validated == sample


def test_ms_to_timestamp_formatting():
    # 1 hour, 2 minutes, 3 seconds, 450 ms = 3723450 ms
    ms = (1 * 3600 + 2 * 60 + 3) * 1000 + 450
    srt_ts = ms_to_timestamp(ms, srt_format=True)
    vtt_ts = ms_to_timestamp(ms, srt_format=False)
    assert srt_ts == "01:02:03,450"
    assert vtt_ts == "01:02:03.450"


def test_whisper_output_parsing():
    raw_whisper_output = """
whisper_init_from_file_with_params_no_state: loading model from 'ggml-base.bin'
[00:00:00.000 --> 00:00:03.500]   Halo, ini adalah aplikasi Vert.
[00:00:03.500 --> 00:00:07.120]   Konversi file 100 persen offline dan aman.
whisper_print_timings:     load time =   142.12 ms
"""
    segments = parse_whisper_output_text(raw_whisper_output)
    assert len(segments) == 2
    assert segments[0].start_ms == 0
    assert segments[0].end_ms == 3500
    assert segments[0].text == "Halo, ini adalah aplikasi Vert."
    assert segments[1].start_ms == 3500
    assert segments[1].end_ms == 7120
    assert segments[1].text == "Konversi file 100 persen offline dan aman."


def test_exporters(tmp_path):
    segments = [
        TranscriptSegment(0, 3000, "First segment text."),
        TranscriptSegment(3000, 6500, "Second segment text."),
    ]
    result = TranscriptionResult(
        language="id",
        model="base",
        duration_sec=6.5,
        full_text="First segment text. Second segment text.",
        segments=segments,
    )

    # 1. TXT Export
    txt_file = tmp_path / "output.txt"
    export_to_txt(result, txt_file)
    assert txt_file.exists()
    assert txt_file.read_text(encoding="utf-8") == "First segment text. Second segment text."

    # 2. SRT Export
    srt_file = tmp_path / "output.srt"
    export_to_srt(result, srt_file)
    srt_content = srt_file.read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:03,000" in srt_content
    assert "First segment text." in srt_content
    assert "00:00:03,000 --> 00:00:06,500" in srt_content

    # 3. VTT Export
    vtt_file = tmp_path / "output.vtt"
    export_to_vtt(result, vtt_file)
    vtt_content = vtt_file.read_text(encoding="utf-8")
    assert vtt_content.startswith("WEBVTT")
    assert "00:00:00.000 --> 00:00:03.000" in vtt_content

    # 4. JSON Export
    json_file = tmp_path / "output.json"
    export_to_json(result, json_file)
    json_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert json_data["language"] == "id"
    assert json_data["model"] == "base"
    assert len(json_data["segments"]) == 2
    assert json_data["segments"][0]["start_ms"] == 0


def test_find_whisper_binary_finds_bundled_engine():
    from core.transcription.engine import find_whisper_binary
    wb = find_whisper_binary()
    assert wb is not None
    assert wb.exists()
    assert wb.name in ("whisper-cli.exe", "main.exe")


def test_engine_download_task_cancel():
    from core.transcription.worker import EngineDownloadTask
    task = EngineDownloadTask()
    assert not task._is_cancelled
    task.cancel()
    assert task._is_cancelled
