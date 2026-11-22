from pathlib import Path
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import openpyxl
from docx import Document
from pypdf import PdfReader
from core.pdf_tools import (
    merge_pdfs,
    pdf_to_docx,
    pdf_to_images,
    pdf_to_xlsx,
    split_pdf,
)


def _create_sample_pdf(path: Path, pages: int = 2) -> Path:
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 50), f"Sample Page {i + 1}\nTable Header | Column", fontsize=16)
    doc.save(str(path))
    doc.close()
    return path


def test_merge_pdfs(tmp_path):
    pdf1 = _create_sample_pdf(tmp_path / "doc1.pdf", pages=1)
    pdf2 = _create_sample_pdf(tmp_path / "doc2.pdf", pages=2)

    merged = tmp_path / "merged.pdf"
    out = merge_pdfs([pdf1, pdf2], merged)

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3


def test_split_pdf_all(tmp_path):
    pdf = _create_sample_pdf(tmp_path / "multipage.pdf", pages=3)
    out_dir = tmp_path / "split_out"

    files = split_pdf(pdf, out_dir)
    assert len(files) == 3
    for f in files:
        assert f.exists()
        reader = PdfReader(str(f))
        assert len(reader.pages) == 1


def test_split_pdf_ranges(tmp_path):
    pdf = _create_sample_pdf(tmp_path / "doc.pdf", pages=4)
    out_dir = tmp_path / "ranges_out"

    files = split_pdf(pdf, out_dir, page_ranges="1-2, 4")
    assert len(files) == 2
    r1 = PdfReader(str(files[0]))
    assert len(r1.pages) == 2
    r2 = PdfReader(str(files[1]))
    assert len(r2.pages) == 1


def test_pdf_to_images(tmp_path):
    pdf = _create_sample_pdf(tmp_path / "sample.pdf", pages=2)
    img_dir = tmp_path / "images"

    images = pdf_to_images(pdf, img_dir, image_ext=".png")
    assert len(images) == 2
    for img in images:
        assert img.exists()
        assert img.suffix == ".png"
        assert img.stat().st_size > 0


def test_pdf_to_xlsx(tmp_path):
    pdf = _create_sample_pdf(tmp_path / "data.pdf", pages=1)
    out_xlsx = tmp_path / "extracted.xlsx"

    out = pdf_to_xlsx(pdf, out_xlsx)
    assert out.exists()
    wb = openpyxl.load_workbook(out)
    assert len(wb.sheetnames) >= 1
    wb.close()


def test_pdf_to_docx(tmp_path):
    pdf = _create_sample_pdf(tmp_path / "sample_doc.pdf", pages=1)
    out_docx = tmp_path / "converted.docx"

    out = pdf_to_docx(pdf, out_docx)
    assert out.exists()
    doc = Document(str(out))
    assert len(doc.paragraphs) > 0


def test_images_to_pdf(tmp_path):
    from PIL import Image
    from core.pdf_tools import images_to_pdf

    img1 = tmp_path / "pic1.jpg"
    img2 = tmp_path / "pic2.png"

    Image.new("RGB", (100, 150), (255, 0, 0)).save(img1, "JPEG")
    Image.new("RGB", (200, 100), (0, 0, 255)).save(img2, "PNG")

    out_pdf = tmp_path / "combined.pdf"
    res = images_to_pdf([img1, img2], out_pdf)

    assert res.exists()
    assert res.stat().st_size > 0
    reader = PdfReader(str(res))
    assert len(reader.pages) == 2


def test_extract_pages_to_pdf(tmp_path):
    from core.pdf_tools import extract_pages_to_pdf

    src_pdf = _create_sample_pdf(tmp_path / "original.pdf", pages=5)
    dst_pdf = tmp_path / "extracted_subset.pdf"

    res = extract_pages_to_pdf(src_pdf, [1, 3, 5], dst_pdf)
    assert res.exists()

    reader = PdfReader(str(res))
    assert len(reader.pages) == 3


