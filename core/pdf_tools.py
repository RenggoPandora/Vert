"""PDF conversion, extraction, merge, and split tools."""

import tempfile
from pathlib import Path
from typing import Sequence
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import openpyxl
from pdf2docx import Converter
import pdfplumber
from pypdf import PdfReader, PdfWriter


def pdf_to_docx(src_pdf: Path | str, dst_docx: Path | str) -> Path:
    """Convert PDF to editable DOCX using pdf2docx."""
    src = Path(src_pdf).resolve()
    dst = Path(dst_docx).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    cv = Converter(str(src))
    try:
        cv.convert(str(dst), start=0, end=None)
    finally:
        cv.close()
    return dst


def pdf_to_xlsx(src_pdf: Path | str, dst_xlsx: Path | str) -> Path:
    """Extract tabular data from PDF to an Excel workbook using pdfplumber."""
    src = Path(src_pdf).resolve()
    dst = Path(dst_xlsx).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()
    default_sheet = wb.active
    if default_sheet is not None:
        wb.remove(default_sheet)

    extracted_any_table = False
    with pdfplumber.open(src) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            sheet = wb.create_sheet(title=f"Page_{idx}")
            if not tables:
                # Fallback: extract text lines
                text = page.extract_text()
                if text:
                    for line in text.splitlines():
                        sheet.append([line])
                continue

            extracted_any_table = True
            for table in tables:
                for row in table:
                    clean_row = ["" if cell is None else str(cell) for cell in row]
                    sheet.append(clean_row)
                sheet.append([])  # blank line between multiple tables on same page

    if len(wb.sheetnames) == 0:
        ws = wb.create_sheet(title="No Data")
        ws.append(["No content extracted from PDF."])

    wb.save(dst)
    wb.close()
    return dst


def pdf_to_images(
    src_pdf: Path | str,
    output_dir: Path | str,
    image_ext: str = ".png",
    dpi: int = 150,
) -> list[Path]:
    """Render each page of a PDF as an image."""
    src = Path(src_pdf).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ext = image_ext if image_ext.startswith(".") else f".{image_ext}"
    generated_files: list[Path] = []
    doc = fitz.open(str(src))
    stem = src.stem

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    try:
        total_pages = len(doc)
        for page_idx in range(total_pages):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            page_num_str = f"{page_idx + 1:03d}" if total_pages >= 10 else f"{page_idx + 1}"
            out_file = out_dir / f"{stem}_page_{page_num_str}{ext}"
            pix.save(str(out_file))
            generated_files.append(out_file)
    finally:
        doc.close()

    return generated_files


def merge_pdfs(pdf_paths: Sequence[Path | str], dst_pdf: Path | str) -> Path:
    """Merge ordered sequence of PDF files into a single target PDF."""
    if not pdf_paths:
        raise ValueError("At least one PDF file is required to merge.")

    dst = Path(dst_pdf).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()
    for p in pdf_paths:
        path_obj = Path(p).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"PDF to merge does not exist: {path_obj}")
        reader = PdfReader(str(path_obj))
        for page in reader.pages:
            writer.add_page(page)

    with open(dst, "wb") as f:
        writer.write(f)

    return dst


def split_pdf(
    src_pdf: Path | str,
    dst_dir: Path | str,
    page_ranges: str | None = None,
) -> list[Path]:
    """Split PDF pages into separate PDF files.

    If page_ranges is None or empty, splits every page into page_1.pdf, page_2.pdf, etc.
    If page_ranges specified (e.g. '1-3, 5, 8-10'), extracts specified segments.
    """
    src = Path(src_pdf).resolve()
    out_dir = Path(dst_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(src))
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("Source PDF contains zero pages.")

    created_files: list[Path] = []
    stem = src.stem

    if not page_ranges or not page_ranges.strip():
        # Split every page
        for idx in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[idx])
            page_no = idx + 1
            out_file = out_dir / f"{stem}_page_{page_no:03d}.pdf"
            with open(out_file, "wb") as f:
                writer.write(f)
            created_files.append(out_file)
        return created_files

    # Parse ranges: e.g. "1-3, 5, 8-10"
    parts = [p.strip() for p in page_ranges.split(",") if p.strip()]
    for segment_idx, part in enumerate(parts, start=1):
        writer = PdfWriter()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start_page = max(1, int(start_str))
            end_page = min(total_pages, int(end_str))
            for p_num in range(start_page, end_page + 1):
                writer.add_page(reader.pages[p_num - 1])
            out_file = out_dir / f"{stem}_pages_{start_page}-{end_page}.pdf"
        else:
            p_num = int(part)
            if 1 <= p_num <= total_pages:
                writer.add_page(reader.pages[p_num - 1])
                out_file = out_dir / f"{stem}_page_{p_num}.pdf"
            else:
                continue

        with open(out_file, "wb") as f:
            writer.write(f)
        created_files.append(out_file)

    return created_files


def images_to_pdf(image_paths: Sequence[Path | str], dst_pdf: Path | str) -> Path:
    """Combine multiple images into a single multi-page PDF document."""
    if not image_paths:
        raise ValueError("At least one image is required to build a PDF.")

    dst = Path(dst_pdf).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open()
    try:
        for p in image_paths:
            path_obj = Path(p).resolve()
            if not path_obj.exists():
                raise FileNotFoundError(f"Image not found: {path_obj}")
            img_doc = fitz.open(str(path_obj))
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()
            img_pdf = fitz.open("pdf", pdf_bytes)
            doc.insert_pdf(img_pdf)
            img_pdf.close()

        doc.save(str(dst))
    finally:
        doc.close()

    return dst

