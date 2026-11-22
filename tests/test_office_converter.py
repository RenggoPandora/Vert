from pathlib import Path
import pytest
from core.office_converter import find_libreoffice_binary, convert_office_to_pdf


def test_find_libreoffice_binary_returns_path_or_none():
    res = find_libreoffice_binary()
    assert res is None or isinstance(res, Path)


def test_convert_office_missing_engine_raises_clear_error(tmp_path, monkeypatch):
    # Simulate neither MS Office nor LibreOffice available
    monkeypatch.setattr("core.office_converter.find_libreoffice_binary", lambda: None)
    monkeypatch.setattr("core.office_converter.convert_docx_via_msword", lambda s, d: (_ for _ in ()).throw(RuntimeError("No MS Word")))

    docx_file = tmp_path / "dummy.docx"
    docx_file.write_text("dummy", encoding="utf-8")
    out_pdf = tmp_path / "out.pdf"

    with pytest.raises(RuntimeError, match="Neither Microsoft Office nor LibreOffice"):
        convert_office_to_pdf(docx_file, out_pdf)
