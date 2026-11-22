# Vert — Development Progress Tracker

**Current Phase:** Phase 4 — Packaging, QA & Release  
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
- [x] Build main desktop window with Mode Switcher (Convert Queue vs. PDF Toolbox) & Drag-and-Drop (`ui/`)
- [x] Implement format router (`core/router.py`) for auto-detecting valid target formats
- [x] Implement async execution worker with process isolation (`core/worker.py`) so UI never freezes
- [x] Build **Image Converter** (`Pillow`: PNG, JPG, WebP, ICO, PDF)
- [x] Build **Office → PDF Converter** (Hybrid: MS Office COM check with alert suppression + LibreOffice Portable with `-env:UserInstallation` fallback)
- [x] Build **PDF → Office Converter** (`pdf2docx`, `pdfplumber` + `openpyxl` table extraction)
- [x] Add safe file naming logic (prevent overwriting existing files)

---

## Phase 2: Media, PDF Utilities & Data
- [x] Build **Media Converter** (`ffmpeg.exe`: MP4, MKV, MP3, WAV, GIF)
- [x] Build **PDF Toolbox** (`PyMuPDF` / `pypdf`: Merge N:1, Split 1:N, PDF → PNG/JPG)
- [x] Build **Data Converter** (stdlib `csv` + `json` + `openpyxl`: CSV ↔ XLSX ↔ JSON)

---

## Phase 3: Batch Processing & Polish
- [x] Multi-file batch queue with per-file status badges (`Queued`, `Converting`, `Done`, `Failed`)
- [x] Custom output folder selector + "Open Output Folder" action
- [x] Plain-language error handling (locked files, corrupt files, password-protected PDFs)
- [x] Modern emerald dark theme styling (`ui/styles.qss`) and responsive UI

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
| 2026-11-22 | v0.9 | Rebuilt splash screen from scratch: removed image logo, implemented obsidian monolith with typographic wordmark, glowing laser progress track, smooth cubic-bezier easing, and fade-out transition. |
| 2026-11-22 | v0.8 | Fixed QueueView converting deadlock, added Hadora Works boot splash, configured Vert.ico desktop icon, implemented on-demand GitHub update checker, wrote Inno Setup script & release builder. 41 tests passing. |
| 2026-11-22 | v0.7 | UI anti-slop overhaul: eliminated all emojis in favor of crisp SVG vector icons, implemented Light (White/Grey/Blue) and Dark (Black/Grey/Blue) theme switcher, fluid responsive grid layout, 39 automated tests passing. |
| 2026-11-22 | v0.6 | Added visual page preview to Split PDF with interactive thumbnail cards, multi-mode extraction (single combined PDF vs. separate files), and updated test suite (36 tests passing). |
| 2026-11-22 | v0.5 | Added iLovePDF-style Tools Hub dashboard with category filters & search, dedicated Images-to-PDF tool view and backend, updated unit tests to 34 passing. |
| 2026-11-22 | v0.4 | Completed Phase 1, 2, 3: Full PySide6 UI with 1:1 Batch Queue and PDF Toolbox (Merge/Split), all converter backends, and comprehensive test suite (31 tests passing). |
| 2026-11-22 | v0.3 | Completed Phase 0: git, project layout, venv, requirements, download_engines script. |
| 2026-11-22 | v0.2 | Refined architecture: drop pandas/numpy bloat, separate 1:1 queue from PDF toolbox, add LibreOffice user profile isolation and QProcess runner. |
| 2026-11-22 | v0.1 | Initialized BRD, PRD, and Progress Tracker for Vert. |
