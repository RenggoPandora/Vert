"""Unit tests for Advanced File Compression foundation and adapters."""

from pathlib import Path
import pytest
from PIL import Image
import pymupdf as fitz
import zipfile

from core.compression.base import (
    CompressionCategory,
    CompressionRequest,
    compute_safe_output_path,
    format_bytes_human,
)
from core.compression.inspector import inspect_file
from core.compression.optimizer import compress_file, find_adapter


def test_format_bytes_human():
    assert format_bytes_human(500) == "500 B"
    assert "KB" in format_bytes_human(2048)
    assert "MB" in format_bytes_human(2 * 1024 * 1024)


def test_safe_output_path_preserves_source(tmp_path):
    src = tmp_path / "sample.jpg"
    src.write_bytes(b"data")

    out1 = compute_safe_output_path(src)
    assert out1 != src
    assert out1.name == "sample_compressed.jpg"

    # If candidate exists, generates incremented name
    out1.write_bytes(b"data")
    out2 = compute_safe_output_path(src)
    assert out2.name == "sample_compressed_1.jpg"


def test_image_inspection_and_compression(tmp_path):
    # Create test JPEG
    img_path = tmp_path / "large_photo.jpg"
    img = Image.new("RGB", (800, 600), color=(200, 100, 50))
    img.save(img_path, format="JPEG", quality=95)
    orig_size = img_path.stat().st_size

    # 1. Inspector
    meta = inspect_file(img_path)
    assert meta.category == CompressionCategory.IMAGE
    assert meta.width == 800
    assert meta.height == 600
    assert meta.size_bytes == orig_size

    # 2. Target size compression (-50%)
    req = CompressionRequest(
        src_path=img_path,
        target_percent=50,
        preset="balanced",
    )
    res = compress_file(req)
    assert res.success is True
    assert res.dst_path.exists()
    assert res.dst_path != img_path
    assert res.compressed_size_bytes < orig_size
    assert res.savings_ratio > 0.1


def test_pdf_inspection_and_compression(tmp_path):
    # Create test PDF
    pdf_path = tmp_path / "document.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello Vert Offline Compression!", fontsize=24)
    doc.save(str(pdf_path))
    doc.close()

    # 1. Inspector
    meta = inspect_file(pdf_path)
    assert meta.category == CompressionCategory.PDF
    assert meta.page_count == 1

    # 2. Compression
    req = CompressionRequest(
        src_path=pdf_path,
        preset="balanced",
    )
    res = compress_file(req)
    assert res.success is True
    assert res.dst_path.exists()
    assert res.dst_path != pdf_path


def test_archive_inspection_and_compression(tmp_path):
    # Create test ZIP with uncompressed text files
    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("test1.txt", "Some repeated text " * 100)
        zf.writestr("test2.txt", "Another repeated string " * 100)
    orig_size = zip_path.stat().st_size

    meta = inspect_file(zip_path)
    assert meta.category == CompressionCategory.ARCHIVE

    req = CompressionRequest(src_path=zip_path)
    res = compress_file(req)
    assert res.success is True
    assert res.compressed_size_bytes < orig_size
    assert res.savings_ratio > 0.4
