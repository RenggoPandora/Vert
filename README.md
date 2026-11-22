# Vert

**Vert** is a free, 100% offline, standalone desktop file converter and PDF suite for Windows.

Most users rely on public web services (like iLovePDF, Smallpdf, or CloudConvert) to convert everyday documents, images, and media. These services introduce privacy concerns, file-size limits, watermarks, paywalls, and mandatory internet connectivity. 

Vert runs proven conversion engines locally on your machine with **zero telemetry, zero cloud uploads, and zero subscription fees**.

---

## Key Features

### 1. PDF Suite
* **Split PDF with Visual Previews:** Real-time thumbnail rendering for every page. Select pages visually to extract into one combined PDF or split into individual files.
* **Merge PDF:** Combine multiple PDFs into a single document with drag-and-drop page reordering.
* **Images to PDF:** Select multiple JPG, PNG, WebP, or BMP images, reorder them, and compile into a multi-page PDF.
* **PDF to Office:** Extract tables directly into Excel (`.xlsx`) or convert text documents to editable Word (`.docx`).

### 2. Office Documents
* **Office to PDF:** Convert Word (`.docx`), Excel (`.xlsx`), and PowerPoint (`.pptx`) directly into high-fidelity PDFs.
* **Hybrid Engine:** Uses native Microsoft Office silently if present, or transparently falls back to bundled LibreOffice Portable with isolated temporary user profiles.

### 3. Images & Media
* **Universal Image Converter:** Convert between PNG, JPG, WebP, ICO, BMP, and TIFF with automatic color-mode adaptation (RGBA alpha flattening for JPEG/PDF).
* **Audio & Video (Bundled FFmpeg):** Extract audio (MP3, WAV, FLAC) from video files (MP4, MKV, AVI, MOV), convert containers, or generate animated GIFs.

### 4. Structured Data
* **Lightweight Data Converter:** Convert spreadsheets and data files between CSV, XLSX, and JSON without heavy data-science dependencies.

### 5. Thoughtful Interface & Design
* **Minimalist Typography:** Built with the **Plus Jakarta Sans** type system.
* **Dual-Theme Support:** One-click toggle between **Dark Mode** (Obsidian / Slate / Royal Blue) and **Light Mode** (Crisp White / Slate / Blue).
* **Responsive Grid:** Tools hub automatically adapts across 1 to 4 columns based on window dimensions.
* **Safe Naming:** Never overwrites existing files automatically (e.g. saves as `report (1).pdf`).

---

## Installation (For Users)

1. Download the latest installer **`Vert_Setup.exe`** (or `Vert-v1.0.0-windows-portable.zip`) from [GitHub Releases](https://github.com/RenggoPandora/Vert/releases).
2. Run the installer. A Desktop shortcut and Start Menu entry will be created automatically.
3. **If Windows 11 Smart App Control flags the file:**
   * Right-click `Vert_Setup.exe` → Select **Properties**.
   * Under the **General** tab, check the box **Unblock** at the bottom → Click **OK**.
   * *(Windows flags newly published unsigned executables until they establish cloud reputation).*
4. Launch Vert. You can disconnect from Wi-Fi — Vert is 100% offline.

---

## Development Setup

### Prerequisites
* Windows 10 or 11 (64-bit)
* Python 3.11+
* Git

### Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RenggoPandora/Vert.git
   cd Vert
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   ./venv/Scripts/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Fetch local binaries (FFmpeg):**
   ```bash
   python scripts/download_engines.py --all
   ```

5. **Run the desktop app:**
   ```bash
   python main.py
   ```

---

## Testing

Run the automated test suite covering format routing, safe naming, converter engines, UI views, and update checks:

```bash
pytest -v
```

*(All 43 tests pass out of the box).*

---

## Building the Installer (`Vert_Setup.exe`)

Vert uses PyInstaller for packaging and Inno Setup for generating the Windows installer:

1. Install Inno Setup 6 (or run `winget install JRSoftware.InnoSetup`).
2. Run the automated release pipeline:
   ```bash
   python scripts/build_installer.py
   ```
3. The resulting standalone installer will be output to:
   ```text
   dist/Vert_Setup.exe
   ```

---

## Project Architecture

```text
Vert/
├── main.py                     # Entry point (splash transition, taskbar AppID, theme)
├── vert.spec                   # PyInstaller bundle specification
├── requirements.txt            # Python dependencies
├── ui/
│   ├── main_window.py          # App shell, navigation header, update checker, theme switcher
│   ├── hub_view.py             # Categorized Tools Hub dashboard with search and 3D cards
│   ├── queue_view.py           # Universal 1:1 batch conversion queue
│   ├── pdf_tools_view.py       # PDF Merge & Split (with interactive page thumbnail gallery)
│   ├── images_to_pdf_view.py   # Multi-image sequence arranger & PDF compiler
│   ├── splash.py               # Minimalist Plus Jakarta Sans splash screen
│   ├── icons.py                # Crisp vector SVG icon renderer (no emojis)
│   ├── theme.py                # Light / Dark stylesheet definitions
│   └── styles.qss              # Baseline Qt stylesheet
├── core/
│   ├── router.py               # File extension normalization and target format routing
│   ├── naming.py               # Safe non-overwriting file naming logic
│   ├── worker.py               # Non-blocking QThreadPool worker runner
│   ├── office_converter.py     # DOCX/XLSX/PPTX -> PDF (COM + isolated LibreOffice fallback)
│   ├── pdf_tools.py            # PDF merge, split, extraction, and rendering
│   ├── image_converter.py      # Pillow image format conversions & alpha adaptation
│   ├── media_converter.py      # FFmpeg audio/video extraction & GIF conversion
│   ├── data_converter.py       # Lightweight CSV <-> XLSX <-> JSON conversions
│   ├── updater.py              # On-demand GitHub Releases version check
│   └── version.py              # Application version metadata
├── assets/
│   └── fonts/                  # Plus Jakarta Sans font files
├── engines/                    # Portable binary cache (ffmpeg.exe)
├── installer/
│   └── vert_setup.iss          # Inno Setup 6 installation script
├── scripts/
│   ├── build_installer.py      # One-click test, compile, and package script
│   ├── download_engines.py     # Local engine fetcher
│   └── generate_samples.py     # Sample test file generator
└── tests/                      # Automated test suite (43 tests)
```

---

## Privacy Guarantee

* **Zero Network Requests at Runtime:** All conversion logic executes strictly on your local CPU.
* **No Telemetry or Tracking:** Vert contains no analytics, telemetry, or user tracking code.
* **On-Demand Updates Only:** Checking for updates only contacts GitHub's public API when explicitly triggered by the user via the "Check for Updates" button.

---

## License & Credits

Built by **Hadora Works** / Pandora.  
Released under the MIT License.
