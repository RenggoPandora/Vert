# Vert — Development Progress Tracker

**Current Phase:** Phase 1 — MVP: Core UI, Office & Images  
**Target Release:** v1.0.0 (Windows Offline Installer)  

---

## Phase 0: Project Setup & Architecture
- [x] Define core concept and offline engine strategy
- [x] Draft `BRD.md` and `PRD.md` with best practices (no pandas, process isolation, profile separation)
- [x] Initialize Git repository, `.gitignore`, and project folder structure
- [x] Create Python virtual environment (`venv`) and minimal `requirements.txt`
- [x] Create `scripts/download_engines.py` to fetch portable binaries (`ffmpeg.exe`, `LibreOfficePortable`)

---

## Phase 1: MVP — Core UI, Office & Images
- [ ] Build main desktop window with Mode Switcher (Convert Queue vs. PDF Toolbox) & Drag-and-Drop (`ui/`)
- [ ] Implement format router (`core/router.py`) for auto-detecting valid target formats
- [ ] Implement async execution worker with process isolation (`core/worker.py`) so UI never freezes
- [ ] Build **Image Converter** (`Pillow`: PNG, JPG, WebP, ICO, PDF)
- [ ] Build **Office → PDF Converter** (Hybrid: MS Office COM check with alert suppression + LibreOffice Portable with `-env:UserInstallation` fallback)
- [ ] Build **PDF → Office Converter** (`pdf2docx`, `pdfplumber` + `openpyxl` table extraction)
- [ ] Add safe file naming logic (prevent overwriting existing files)

---

## Phase 2: Media, PDF Utilities & Data
- [ ] Build **Media Converter** (`ffmpeg.exe` via `QProcess`: MP4, MKV, MP3, WAV, GIF)
- [ ] Build **PDF Toolbox** (`PyMuPDF` / `pypdf`: Merge N:1, Split 1:N, PDF → PNG/JPG)
- [ ] Build **Data Converter** (stdlib `csv` + `json` + `openpyxl`: CSV ↔ XLSX ↔ JSON)

---

## Phase 3: Batch Processing & Polish
- [ ] Multi-file batch queue with per-file status badges (`Queued`, `Converting`, `Done`, `Failed`)
- [ ] Custom output folder selector + "Open Output Folder" action
- [ ] Plain-language error handling (locked files, corrupt files, password-protected PDFs)
- [ ] Light/Dark theme polish (`ui/styles.qss`) and application icon (`vert.ico`)

---

## Phase 4: Packaging, QA & Release
- [ ] Package app with PyInstaller (`--windowed`, bundle `engines/`)
- [ ] Write Inno Setup script (`installer/vert_setup.iss`) with LZMA2 compression
- [ ] Build `Vert_Setup.exe`
- [ ] **Offline QA Test:** Install on a clean Windows PC (no Python, no Office, Wi-Fi off) and verify all 6 conversion categories
- [ ] Verify clean uninstall via Windows Settings
- [ ] Publish v1.0.0 to GitHub Releases

---

## Change Log
| Date | Version | Notes |
|---|---|---|
| 2026-11-22 | v0.3 | Completed Phase 0: git, project layout, venv, requirements, download_engines script. |
| 2026-11-22 | v0.2 | Refined architecture: drop pandas/numpy bloat, separate 1:1 queue from PDF toolbox, add LibreOffice user profile isolation and QProcess runner. |
| 2026-11-22 | v0.1 | Initialized BRD, PRD, and Progress Tracker for Vert. |
