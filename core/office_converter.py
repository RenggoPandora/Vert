"""Office documents (DOCX, XLSX, PPTX) to PDF conversion engine.

Uses MS Office COM automation if available on Windows,
with transparent fallback to bundled or system LibreOffice.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ENGINES_DIR = ROOT_DIR / "engines"


def find_libreoffice_binary() -> Path | None:
    """Locate soffice.exe in bundled engines or system PATH / default locations."""
    # Check bundled portable LibreOffice
    bundled_candidates = [
        ENGINES_DIR / "LibreOfficePortable" / "App" / "libreoffice" / "program" / "soffice.exe",
        ENGINES_DIR / "LibreOfficePortable" / "LibreOfficePortable.exe",
        ENGINES_DIR / "libreoffice_portable" / "App" / "libreoffice" / "program" / "soffice.exe",
    ]
    for candidate in bundled_candidates:
        if candidate.exists():
            return candidate

    # Check system PATH
    sys_soffice = shutil.which("soffice")
    if sys_soffice:
        return Path(sys_soffice)

    # Standard Windows install paths
    std_paths = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ]
    for p in std_paths:
        if p.exists():
            return p

    return None


def convert_via_libreoffice(src: Path, dst_dir: Path, timeout: int = 120) -> Path:
    """Execute headless LibreOffice conversion with isolated user profile."""
    soffice_path = find_libreoffice_binary()
    if not soffice_path:
        raise RuntimeError(
            "Neither Microsoft Office nor LibreOffice was found. "
            "Please ensure LibreOffice Portable is in engines/ or installed on the system."
        )

    # Create isolated temp profile to prevent multi-instance deadlocks
    temp_profile_dir = Path(tempfile.mkdtemp(prefix="vert_lo_profile_"))
    try:
        # LibreOffice expects file URI for UserInstallation on Windows, e.g. file:///C:/temp/...
        profile_uri = temp_profile_dir.as_uri()
        cmd = [
            str(soffice_path),
            "--headless",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to",
            "pdf",
            str(src),
            "--outdir",
            str(dst_dir),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )

        expected_output = dst_dir / f"{src.stem}.pdf"
        if not expected_output.exists():
            raise RuntimeError(
                f"LibreOffice failed to generate PDF. Exit code: {result.returncode}. "
                f"Stderr: {result.stderr.strip()}"
            )
        return expected_output
    finally:
        shutil.rmtree(temp_profile_dir, ignore_errors=True)


def convert_docx_via_msword(src: Path, dst: Path) -> Path:
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore

    pythoncom.CoInitialize()
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # wdAlertsNone
        doc = word.Documents.Open(str(src), ReadOnly=True)
        # 17 = wdFormatPDF
        doc.SaveAs2(str(dst), FileFormat=17)
        return dst
    finally:
        if doc:
            try:
                doc.Close(False)
            except Exception:
                pass
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def convert_xlsx_via_msexcel(src: Path, dst: Path) -> Path:
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore

    pythoncom.CoInitialize()
    excel = None
    wb = None
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(src), ReadOnly=True)
        # 0 = xlTypePDF
        wb.ExportAsFixedFormat(0, str(dst))
        return dst
    finally:
        if wb:
            try:
                wb.Close(False)
            except Exception:
                pass
        if excel:
            try:
                excel.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def convert_pptx_via_msppt(src: Path, dst: Path) -> Path:
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore

    pythoncom.CoInitialize()
    ppt = None
    pres = None
    try:
        ppt = win32com.client.DispatchEx("PowerPoint.Application")
        # 32 = ppSaveAsPDF
        pres = ppt.Presentations.Open(str(src), WithWindow=False)
        pres.SaveAs(str(dst), 32)
        return dst
    finally:
        if pres:
            try:
                pres.Close()
            except Exception:
                pass
        if ppt:
            try:
                ppt.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def convert_office_to_pdf(src_path: Path | str, dst_path: Path | str) -> Path:
    """Convert DOCX, XLSX, or PPTX to PDF using COM fallback or LibreOffice."""
    src = Path(src_path).resolve()
    dst = Path(dst_path).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    ext = src.suffix.lower()

    # Try native MS Office COM first if available
    try:
        if ext == ".docx":
            return convert_docx_via_msword(src, dst)
        elif ext == ".xlsx":
            return convert_xlsx_via_msexcel(src, dst)
        elif ext == ".pptx":
            return convert_pptx_via_msppt(src, dst)
    except Exception:
        # COM failed or MS Office not installed, fall through to LibreOffice
        pass

    # Fallback to headless LibreOffice
    temp_dir = Path(tempfile.mkdtemp(prefix="vert_office_"))
    try:
        temp_pdf = convert_via_libreoffice(src, temp_dir)
        if temp_pdf != dst:
            shutil.move(str(temp_pdf), str(dst))
        return dst
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
