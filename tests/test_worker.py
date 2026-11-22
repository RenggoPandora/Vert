from pathlib import Path
from PIL import Image
from core.worker import (
    ConversionJob,
    dispatch_conversion,
    format_error_message,
)


def test_format_error_message():
    assert "locked by Windows" in format_error_message(PermissionError("Permission denied: file is used by another process"))
    assert "Password-protected" in format_error_message(ValueError("File is password protected"))
    assert "Media engine" in format_error_message(RuntimeError("ffmpeg.exe not found"))


def test_dispatch_conversion_image(tmp_path):
    src = tmp_path / "img.png"
    Image.new("RGB", (30, 30), (255, 0, 0)).save(src)
    dst = tmp_path / "img.webp"

    job = ConversionJob(job_id="job1", src_path=src, dst_path=dst)
    out = dispatch_conversion(job)

    assert out.exists()
    assert out.suffix == ".webp"


def test_dispatch_conversion_data(tmp_path):
    src = tmp_path / "data.csv"
    src.write_text("a,b\n1,2\n", encoding="utf-8")
    dst = tmp_path / "data.json"

    job = ConversionJob(job_id="job2", src_path=src, dst_path=dst)
    out = dispatch_conversion(job)

    assert out.exists()
    assert out.suffix == ".json"
