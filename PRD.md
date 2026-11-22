# Product Requirements Document (PRD): Vert

**Product Name:** Vert  
**Version:** 1.0  
**Date:** November 22, 2026  
**Target Platform:** Windows 10 / 11 (Desktop `.exe`)  

---

## 1. Product Overview

**Vert** is a native, offline-first desktop file converter designed around a minimal 3-step workflow: **Drop → Select → Convert**. Under the hood, Vert routes files to bundled open-source conversion engines so users never have to install dependencies or upload private files to the web.

---

## 2. User Flow

1. **Launch:** User opens Vert from the Desktop or Start Menu shortcut.
2. **Input:** User drags and drops one or more files into the drop zone (or clicks **Browse Files**).
3. **Auto-Detect & Filter:** Vert reads each file's extension and populates the **Convert To** dropdown with only valid target formats.
4. **Output Path:** Defaults to the source file's folder (with an optional toggle to pick a custom output folder).
5. **Convert:** User clicks **Convert**. Background worker threads process the queue while displaying per-file progress (`Queued` → `Converting...` → `Done` / `Failed`).
6. **Finish:** User clicks **Open Folder** to view the converted files immediately.

---

## 3. Functional Requirements

### 3.1 Supported Conversion Matrix

| ID | Category | Input Formats | Target Output Formats | Bundled Engine |
|---|---|---|---|---|
| **FR-01** | **Office → PDF** | `.docx`, `.xlsx`, `.pptx` | `.pdf` | LibreOffice Portable (`soffice --headless -env:UserInstallation=...`) + MS Office COM fallback |
| **FR-02** | **PDF → Office** | `.pdf` | `.docx`, `.xlsx` *(Table Extraction)* | `pdf2docx`, `pdfplumber` + `openpyxl` |
| **FR-03** | **PDF Utilities** | `.pdf` | Merge (N:1), Split (1:N), `.png`, `.jpg` | `PyMuPDF` (`fitz`) / `pypdf` |
| **FR-04** | **Images** | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.ico`, `.tiff` | `.png`, `.jpg`, `.webp`, `.ico`, `.pdf` | `Pillow` |
| **FR-05** | **Audio & Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.mp3`, `.wav`, `.flac` | `.mp4`, `.mp3`, `.wav`, `.gif` | `ffmpeg.exe` (Bundled CLI via `QProcess`) |
| **FR-06** | **Data Files** | `.csv`, `.xlsx`, `.json` | `.csv`, `.xlsx`, `.json` | Standard library `csv` + `json` + `openpyxl` *(no pandas/numpy)* |

### 3.2 UI & Queue Features

* **FR-07 (Drag & Drop):** Accept single or multiple files dropped anywhere on the main window.
* **FR-08 (Batch Queue - Convert Mode):** Display 1:1 conversion queue showing filename, detected type, target format selector, and live status badge.
* **FR-08b (PDF Toolbox Mode):** Dedicated interface for N:1 and 1:N PDF workflows:
  * **Merge Mode:** Orderable list of input PDFs with drag-reorder and single merged output.
  * **Split Mode:** Single input PDF with page range selector (e.g., `1-3, 5, 8-10`) or "Extract all pages".
* **FR-08c (Images to PDF):** Dedicated tool allowing users to select/drop multiple images (JPG, PNG, WebP, BMP, TIFF), arrange page sequence, and export a unified PDF.
* **FR-09 (Safe Naming):** Never overwrite an existing file. If `report.pdf` already exists, save as `report (1).pdf`.
* **FR-10 (Clear Error Messages):** Translate engine failures into plain-language messages (e.g., *"File is open in another program"*, *"Password-protected PDFs are not supported"*, *"PDF contains no tabular data"*).
* **FR-11 (Theme Support):** Clean, modern UI with Light and Dark mode support.
* **FR-12 (iLovePDF-Style Tools Hub):** Card-based dashboard categorizing workflows (`PDF`, `Office`, `Images`, `Media`, `Data`) with live search and 1-click launch.

---

## 4. Non-Functional Requirements

* **NFR-01 (Offline Autonomy):** Zero network requests at install time or runtime.
* **NFR-02 (Non-Blocking UI & Concurrency Isolation):**
  * Binary subprocesses (`ffmpeg.exe`, `soffice`) managed via non-blocking asynchronous runners (`QProcess` / subprocess) with timeouts and process-kill guarantees.
  * Python-heavy tasks (`pdf2docx`, `Pillow`) executed outside the GUI thread (worker process or GIL-released routines) so the Qt event loop never stutters.
  * LibreOffice calls must inject isolated temp user profile (`-env:UserInstallation=file:///...`) to prevent process collision and locks.
* **NFR-03 (Resource Cleanup):** Temporary files and isolated LibreOffice profiles created during conversion must be written to OS temp directory and deleted upon completion or error.
* **NFR-04 (System Footprint):** Runs smoothly on Windows 10/11 with 4 GB RAM and < 500 MB disk space after installation. Eliminates heavy data-science dependencies (`pandas`, `numpy`).
* **NFR-05 (Clean Uninstall):** Standard Windows uninstaller removes the app and all bundled engines cleanly.

---

## 5. Technical Architecture

* **Language:** Python 3.11+
* **Desktop UI:** PySide6 (Qt)
* **Packaging:** PyInstaller (`--windowed`) → Inno Setup (`Vert_Setup.exe` with LZMA2 compression)
* **Binary Distribution:** Engines stored externally during development; fetched via `scripts/download_engines.py` and staged at package time. Never committed to Git repo.
* **Distribution:** GitHub Releases

### Project Directory Structure

```text
Vert/
├── .gitignore                  # Ignores venv/, engines/, build/, dist/
├── main.py                     # Application entry point
├── ui/
│   ├── main_window.py          # Main window shell & mode switcher (Convert / PDF Toolbox)
│   ├── queue_view.py           # 1:1 batch conversion queue
│   ├── pdf_tools_view.py       # PDF Merge & Split views
│   └── styles.qss              # Clean light/dark styling
├── core/
│   ├── router.py               # Maps file extensions to valid outputs & engines
│   ├── worker.py               # Async worker runner for non-blocking jobs
│   ├── office_converter.py     # DOCX/XLSX/PPTX <-> PDF (MS COM fallback + isolated LibreOffice)
│   ├── pdf_tools.py            # Merge, split, PDF -> Images, PDF -> DOCX/XLSX
│   ├── image_converter.py      # Pillow image conversions
│   ├── media_converter.py      # FFmpeg QProcess wrapper
│   └── data_converter.py       # Lightweight CSV <-> XLSX <-> JSON (stdlib + openpyxl)
├── engines/                    # Bundled offline binaries (local only, gitignored)
│   ├── ffmpeg.exe
│   └── libreoffice_portable/
├── scripts/
│   └── download_engines.py     # Script to download and verify portable engines for local dev & CI
├── docs/
│   ├── BRD.md
│   └── PRD.md
├── installer/
│   └── vert_setup.iss          # Inno Setup script
├── ProgressTracker.md
└── requirements.txt