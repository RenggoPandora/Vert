from pathlib import Path
from core.naming import get_safe_output_path
from core.router import (
    FileCategory,
    get_file_category,
    get_target_formats,
    is_conversion_supported,
    normalize_extension,
)


def test_normalize_extension():
    assert normalize_extension("test.PNG") == ".png"
    assert normalize_extension(".DOCX") == ".docx"
    assert normalize_extension(Path("folder/sub/data.XLSX")) == ".xlsx"
    assert normalize_extension("mp4") == ".mp4"


def test_get_file_category():
    assert get_file_category("doc.docx") == FileCategory.OFFICE
    assert get_file_category("book.pdf") == FileCategory.PDF
    assert get_file_category("image.webp") == FileCategory.IMAGE
    assert get_file_category("video.mp4") == FileCategory.MEDIA
    assert get_file_category("table.csv") == FileCategory.DATA
    assert get_file_category("unknown.xyz") == FileCategory.UNSUPPORTED


def test_target_formats():
    targets = [opt.extension for opt in get_target_formats("photo.png")]
    assert ".jpg" in targets
    assert ".webp" in targets
    assert ".ico" in targets
    assert ".pdf" in targets

    pdf_targets = [opt.extension for opt in get_target_formats("doc.pdf")]
    assert ".docx" in pdf_targets
    assert ".xlsx" in pdf_targets

    docx_targets = [opt.extension for opt in get_target_formats("notes.docx")]
    assert ".pdf" in docx_targets

    assert get_target_formats("unsupported.zip") == []


def test_is_conversion_supported():
    assert is_conversion_supported(".png", ".jpg")
    assert is_conversion_supported("photo.png", "target.webp")
    assert is_conversion_supported("document.docx", "document.pdf")
    assert is_conversion_supported("data.csv", "data.json")
    assert not is_conversion_supported("song.mp3", "doc.pdf")


def test_get_safe_output_path(tmp_path):
    # Base case: file does not exist
    out1 = get_safe_output_path(tmp_path, "sample.txt", ".pdf")
    assert out1.name == "sample.pdf"
    out1.touch()

    # Second case: sample.pdf exists -> sample (1).pdf
    out2 = get_safe_output_path(tmp_path, "sample.txt", ".pdf")
    assert out2.name == "sample (1).pdf"
    out2.touch()

    # Third case: sample (1).pdf exists -> sample (2).pdf
    out3 = get_safe_output_path(tmp_path, "sample.txt", ".pdf")
    assert out3.name == "sample (2).pdf"
