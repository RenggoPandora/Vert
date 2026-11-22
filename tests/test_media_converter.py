from pathlib import Path
import pytest
from core.media_converter import find_ffmpeg_binary, convert_media


def test_find_ffmpeg_returns_path_or_none():
    res = find_ffmpeg_binary()
    assert res is None or isinstance(res, Path)


def test_convert_media_missing_ffmpeg_raises_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr("core.media_converter.find_ffmpeg_binary", lambda: None)

    src = tmp_path / "test.mp4"
    src.write_text("dummy", encoding="utf-8")
    dst = tmp_path / "test.mp3"

    with pytest.raises(RuntimeError, match="ffmpeg.exe not found"):
        convert_media(src, dst)
