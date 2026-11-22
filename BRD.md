# Business Requirements Document (BRD): Vert

**Project Name:** Vert  
**Version:** 1.0  
**Date:** November 22, 2026  
**Status:** Draft  

---

## 1. Executive Summary

**Vert** is a free, 100% offline, standalone desktop application that enables users to convert documents, PDFs, images, audio/video media, and structured data files directly on their own laptop or PC.

Most users rely on public web-based converters (e.g., iLovePDF, Smallpdf, CloudConvert) to convert everyday files like Word documents, Excel spreadsheets, and PDFs. These platforms introduce privacy risks, file-size limits, watermarks, paywalls, and internet dependency. Vert solves this by bundling proven open-source conversion engines into a single, easy-to-install desktop executable with a drag-and-drop interface.

---

## 2. Business Objectives

* **Zero-Cloud Privacy:** Guarantee that 100% of file processing happens locally on the user's machine with zero internet connection required and zero telemetry.
* **Frictionless Adoption:** Deliver a single downloadable installer (`Vert_Setup.exe`) that requires no technical setup, command-line knowledge, or separate third-party installations (such as Microsoft Office or Python).
* **All-in-One Consolidation:** Replace multiple single-purpose web tools with one unified desktop utility covering Office documents, PDFs, images, media, and data files.
* **Zero Cost to End Users:** Distribute Vert for free with no file-size caps, daily conversion limits, or paywalled formats.

---

## 3. Target Audience

* **Everyday Office & Academic Users:** Students, employees, and freelancers who frequently convert `.docx`, `.xlsx`, `.pptx`, and `.pdf` files and want to keep private documents off public servers.
* **Privacy-Conscious Professionals:** Users handling sensitive financial, medical, legal, or corporate records who cannot upload files to third-party websites.
* **Offline / Low-Connectivity Users:** Users working in environments with restricted, slow, or unavailable internet access.

---

## 4. Scope Definition

### In-Scope (v1.0 – v2.0)
* Native Windows desktop application (`.exe` installer).
* 100% offline file conversion across five core categories: Office Documents, PDFs, Images, Audio/Video, and Data.
* Drag-and-drop file selection and batch conversion.
* Automatic file-type detection and smart target-format filtering.
* Self-contained installer bundling all required local engines.

### Out-of-Scope (Initial Release)
* Web-based interface, browser extensions, or cloud storage integrations (Google Drive, Dropbox).
* OCR (Optical Character Recognition) for scanned, non-selectable image PDFs *(future release)*.
* Advanced video/photo editing (trimming, color grading, complex filters).
* Mobile (iOS/Android) applications.

---

## 5. High-Level Business Requirements

| ID | Category | Requirement |
|---|---|---|
| **BR-01** | **Privacy** | All conversions must execute locally without outbound network calls. |
| **BR-02** | **Office Support** | Must convert `.docx`, `.xlsx`, and `.pptx` to `.pdf`, and `.pdf` back to `.docx`/`.xlsx`, without requiring a paid MS Office license. |
| **BR-03** | **Universal Utility** | Must also support common Image, Audio/Video, PDF utility, and Data format conversions under one interface. |
| **BR-04** | **Distribution** | Must be packaged as a single downloadable installer that non-technical users can install via a standard Setup Wizard. |
| **BR-05** | **Usability** | Core workflow must take no more than 3 actions: Drop File → Pick Format → Convert. |

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| **Large Installer Size (~200–300 MB)** | Slower initial download due to bundling LibreOffice Portable and FFmpeg. | Use Inno Setup LZMA2 max compression; strip unused LibreOffice language packs; eliminate heavy Python libraries (`pandas`, `numpy`) in favor of stdlib + `openpyxl`; fetch binaries via setup script rather than storing in Git. |
| **Antivirus False Positives** | Windows Defender may flag unsigned PyInstaller `.exe` files. | Publish open-source code on GitHub for transparency; provide SHA-256 checksums; consider code signing if distributing widely. |
| **Office Formatting Shifts & Process Lockups** | LibreOffice may render complex layouts differently; concurrent headless calls may hang or lock profile. | Implement hybrid check (use MS Office silently with alert suppression if present, fallback to bundled LibreOffice Portable); execute headless conversions with isolated user profile (`-env:UserInstallation`) and process timeout guards. |

---

## 7. Acceptance Criteria (Definition of Done for v1.0)

1. A user with no Python, no FFmpeg, and no Microsoft Office installed can download `Vert_Setup.exe`, install it, disconnect from Wi-Fi, and successfully convert `.docx` → `.pdf`, `.pdf` → `.docx`, and `.png` → `.jpg`.
2. The UI remains responsive (draggable and clickable) while converting a 50 MB video or a 50-page document.
3. No temporary files are left behind in the user's working directory after conversion completes.