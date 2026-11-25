# Vert — Enhancement v1: Product & Technical Specification

- **Project:** Vert (`https://github.com/RenggoPandora/Vert`)
- **Enhancement Version:** `v1.0`
- **Document Status:** Proposed / Planned (0% Implemented)
- **Target Platform:** Windows (Local-First Desktop Application)

---

## 1. Project Context & Repository Baseline

### 1.1 Project Context
Vert is a free, open-source, local-first file processing application built for Windows. Rather than routing user files through remote servers, cloud APIs, or paid subscription tiers, Vert executes processing directly on the user's machine while respecting file integrity and user autonomy.

Enhancement v1 (`v1.0`) introduces two major capabilities—**Audio-to-Text** and **Advanced File Compression**—designed to expand Vert's utility while maintaining strict adherence to its core principles.

### 1.2 Current vs. Proposed Implementation Boundaries
> **Repository Inspection Note:** External repository inspection of `https://github.com/RenggoPandora/Vert` did not return publicly indexed repository files or directory trees during specification authoring. Accordingly, this specification **does not assume** specific existing file paths, UI frameworks, or internal module names beyond the Windows local-first context and Python/FFmpeg considerations noted in the brief.

- **Current Baseline (Existing / Assumed Unverified):**
  - Core Windows desktop application shell and existing file processing workflows (exact module layout and UI framework to be verified during **M0 — Repository & Architecture Review**).
  - Existing dependency/packaging patterns and potential reusable utilities or FFmpeg availability (to be verified in **M0** before adding duplicate binaries).
- **Proposed Enhancement v1 (Planned — 0% Implemented):**
  - **Feature 01 (Audio-to-Text):** Local speech-to-text transcription powered by `whisper.cpp` with FFmpeg audio decoding/preprocessing, on-demand model management, transcript editing, and multi-format export (`TXT`, `SRT`, `VTT`, `JSON`).
  - **Feature 02 (Advanced File Compression):** Format-aware local file compression featuring iterative **Target-Size Compression**, format-specific parameter controls, estimation/reporting, and non-destructive output handling.

No Enhancement v1 components have been implemented yet. All implementation milestones (`M0`–`M7`) begin at `0%`.

---

## 2. Product Principles

Every feature, architecture decision, and UI interaction in Enhancement v1 must uphold Vert's core principles:

1. **Privacy-First:** User audio, media, documents, and transcripts are processed locally on the user's machine. Nothing is uploaded to external servers or cloud services. Sensitive file content and transcript text must not be written to diagnostic logs by default.
2. **Offline-First:** Once required engines (such as `whisper.cpp` and FFmpeg) and selected speech models are installed locally, core transcription and compression workflows operate without an active internet connection.
3. **Free and Open Source:** Zero subscriptions, paid feature gates, artificial usage limits, or watermarks. All v1 capabilities are available to every user.
4. **Lightweight:** Avoid bloating the default installer with unnecessarily large AI models or redundant third-party runtimes. Support on-demand model downloads and reuse existing project dependencies where practical.
5. **User Control:** Give users explicit control over models, languages, target sizes, quality/compression levels, output formats (when supported), and destination directories—with no silent background model downloads or unrequested format conversions.
6. **Original Preservation:** Source files must never be overwritten, mutated in place, or deleted by default. Outputs are written to explicit destinations or new files while keeping source inputs intact.

---

## 3. Feature Objectives & Positioning

### 3.1 Feature 01 — Audio-to-Text
- **Objective:** Enable users to extract spoken words from local audio files and convert them into searchable, editable text via locally executed speech recognition.
- **Proposed Positioning:** *"Transform audio recordings into searchable, editable text — privately and entirely offline."*

### 3.2 Feature 02 — Advanced File Compression
- **Objective:** Provide format-aware local file compression with granular user control over target output size, quality, and compression settings—differentiating Vert from rigid preset-only or cloud-based tools through **Target-Size Compression**.
- **Proposed Positioning:** *"Compress files locally with control over output size, quality, and processing settings."*

---

## 4. Functional Requirements

### 4.1 Feature 01: Audio-to-Text

#### MVP Functional Requirements
1. **Audio File Import:** Allow users to select audio files via a native file picker and via drag-and-drop.
2. **Supported Audio Formats & Validation:** Support common audio formats subject to format/integrity validation:
   - `MP3`
   - `WAV`
   - `M4A`
   - `FLAC`
   - `OGG`
   - `AAC`
3. **Automatic Language Detection:** Support automatic spoken language identification during transcription when selected.
4. **Manual Language Selection:** Allow users to explicitly choose a target/source spoken language (including Indonesian and other languages supported by the selected model/engine).
5. **Selectable Speech Recognition Models:** Allow users to choose among available/installed speech models based on hardware and accuracy trade-offs.
6. **Local Audio Transcription:** Execute speech recognition locally on the user's device without cloud APIs.
7. **Progress & Error Handling:** Display processing status/progress updates and surface clear, actionable error messages (e.g., missing model, corrupted or unsupported audio, preprocessing failure, cancellation).
8. **Transcript Preview & Editing:** Provide an in-app preview and editor so users can inspect and refine transcribed text before copying or exporting.
9. **Clipboard Copy:** Allow one-click copying of the transcript to the system clipboard.
10. **Multi-Format Export:** Export transcripts to:
    - `TXT` (plain text)
    - `SRT` (SubRip subtitles with timestamps)
    - `VTT` (WebVTT subtitles with timestamps)
    - `JSON` (structured transcript output including segments/metadata as applicable)
11. **Offline Operation:** Support complete end-to-end transcription offline once the engine and desired model(s) are installed locally.

#### Model Management Requirements
AI speech models must be **downloaded on demand** rather than bundled in full inside the default installer.

| Model | Intended Usage | Notes |
| :--- | :--- | :--- |
| **Tiny** | Low-resource devices | Fastest execution, lowest resource footprint, lower accuracy |
| **Base** | General-purpose default | Balanced speed and accuracy for everyday use |
| **Small** | Better transcription quality | Higher accuracy for clearer speech/noisy audio; heavier compute |
| **Medium** | Higher-resource option | Stronger accuracy for demanding workloads; requires capable hardware |

Model management must enforce:
- **Explicit User-Initiated Downloads:** Never download models automatically or without explicit user consent.
- **Status & Size Visibility:** Display approximate/actual model download size and current installation status (`Not Installed`, `Downloading`, `Installed`, `Corrupted/Incomplete`).
- **Local Storage & Removal:** Store models in a managed local directory and allow users to delete/remove installed models to reclaim disk space.
- **Integrity Verification:** Verify downloaded model integrity (e.g., checksum/hash or size verification where available) before marking ready for use.

---

### 4.2 Feature 02: Advanced File Compression

#### MVP Functional Requirements
1. **File Selection:** Allow users to select input file(s) for compression.
2. **Format Detection & Metadata Inspection:** Detect actual file format/container and inspect relevant metadata (dimensions, duration/bitrate, page count/embedded media, compression characteristics).
3. **Format-Specific Compression Settings:** Present compression parameters tailored to the detected file type.
4. **Target Output Size:** Allow users to specify a desired target output size where technically feasible (including quick presets such as `500 KB`, `1 MB`, `2 MB`, `5 MB`, plus a custom numeric size input with unit selection).
5. **Compression Level Selection:** Allow selecting compression effort/level where supported by the format/adapter.
6. **Quality Adjustment:** Allow adjusting visual/encoding quality where supported by the format/adapter.
7. **Estimated Output Size:** Display an estimated output size where meaningful/calculable prior to or during execution.
8. **Actual Output Size Reporting:** Measure and display the exact byte/human-readable size of generated output file(s).
9. **Compression Reduction Statistics:** Report size reduction (e.g., bytes saved and percentage reduction relative to original file size).
10. **Output Directory Selection:** Allow choosing the output directory (defaulting safely without overwriting the original source file).
11. **Batch Processing (Planned Capability):** Support processing multiple files in a batch according to v1 scope and milestone maturity (`M3`–`M6`).
12. **Original File Preservation:** Never overwrite or delete original source files by default.

#### Target-Size Compression & Optimization Algorithm
Target size is an **optimization objective, not a universal guarantee**. The system must never promise exact byte matches when format structure, encoding limits, or source entropy make that impossible.

For supported formats, the **Target-Size Optimization Algorithm** follows these steps:
1. **Inspect Source File & Metadata:** Read format, dimensions/duration/structure, and baseline byte size.
2. **Validate Target Size:** Check that the requested target size is positive, sensible relative to file constraints, and compatible with format rules; surface clear guidance if targets are unrealistic or unsupported.
3. **Calculate Initial Encoding Parameters:** Derive starting quality, bitrate, or compression parameters from source size, target size, and format characteristics.
4. **Generate Compression Candidate:** Produce a candidate output file using the calculated parameters.
5. **Measure Actual Output Size:** Inspect the resulting candidate's actual file size on disk.
6. **Adjust Compression Parameters:** Tune quality/bitrate/parameters based on whether the candidate is above or below the target.
7. **Retry Within Bounded Iteration Budget:** Repeat within a strict, finite iteration cap—avoiding infinite loops or excessive repeated lossy re-encoding degradation.
8. **Preserve Best Valid Candidate:** Retain the best valid candidate produced (e.g., meeting the target within acceptable quality bounds, or closest valid non-destructive result if exact target cannot be met).
9. **Report Outcome:** Clearly report whether the target was achieved, show the actual output size and reduction metrics, and explain why if the target could not be reached.

Algorithmic invariants:
- No unbounded retries.
- No uncontrolled repeated lossy re-encoding of already-compressed lossy outputs.
- Original source file remains untouched.
- Actual output size is always measured and reported.
- Unachievable targets are explained transparently.
- Never silently alter output format or dimensions without explicit user action/consent.

#### Format Feasibility Matrix
Initial feasibility assessments (subject to empirical verification during `M3`–`M4`; not guaranteed performance SLAs):

| Format | Target-Size Feasibility | Technical Approach |
| :--- | :--- | :--- |
| **JPEG** | High | Iterative quality adjustment |
| **WebP** | High | Quality and encoding parameter adjustment |
| **PNG** | Limited | Lossless optimization; optional format conversion (only with explicit user choice) |
| **PDF** | Best-effort | Image optimization, metadata and structure optimization |
| **MP4** | High in many cases | Bitrate calculation and two-pass encoding (where supported) |
| **ZIP / 7Z** | Limited | Compression depends heavily on source data compressibility/entropy |

#### Format-Driven UI Controls
Expose only relevant controls based on detected file format and supported capabilities:
- Target Size (presets + custom input, where feasible)
- Compression Level (where supported)
- Quality (where supported)
- Resolution / Dimensions (where applicable)
- Output Format (where supported and explicitly selected by user)
- Estimated Output Size (where meaningful)
- Actual Output Size (post-run)
- Compression Reduction (post-run metrics)

Irrelevant controls for a given format/mode must be hidden or disabled with clear explanations rather than shown as misleading options.

---

## 5. Non-Functional & Cross-Feature Requirements

Both Audio-to-Text and Advanced File Compression must satisfy all cross-feature requirements:

| Requirement | Expected Behavior |
| :--- | :--- |
| **Privacy** | Zero file uploads to external servers; no transcript text or sensitive file content written to logs by default. |
| **Processing** | Executed locally on the user's Windows machine. |
| **Offline Operation** | Functions offline after required engines and models are installed. |
| **Cost & Licensing** | Free and open-source; no subscriptions, watermarks, or usage paywalls. |
| **Original Preservation** | Source files are never overwritten or deleted by default. |
| **Dependency Reuse** | Reuse existing Vert engines, utilities, and dependencies where practical; avoid redundant runtimes. |
| **Error Handling** | Clear, user-friendly, and actionable error messages for invalid inputs, missing models, failed runs, or disk issues. |
| **Cancellation** | Safe cancellation of in-flight jobs where supported, cleaning up partial/temporary artifacts. |
| **Temporary Files** | Temporary working files and intermediate artifacts are cleaned up reliably after completion, error, or cancellation. |
| **Logging** | Diagnostic logging avoids sensitive file content, full paths if sensitive in shared logs (to be defined in `M0`), and transcript contents by default. |
| **Windows Packaging** | Compatible with Vert's Windows distribution and packaging workflow. |

---

## 6. Proposed Technology & Dependency Considerations

### 6.1 Audio-to-Text Stack
- **Primary Engine Candidate:** `whisper.cpp` (`https://github.com/ggml-org/whisper.cpp`)
  - Local inference without cloud APIs.
  - Supports CPU inference and Windows targets.
  - Multilingual speech recognition, including Indonesian.
  - Multiple model sizes (`Tiny`, `Base`, `Small`, `Medium`) for varying hardware profiles.
  - Integrable with Python-based application layers via subprocess execution or native bindings (exact integration mechanism to be evaluated in `M0`/`M1`).
- **Audio Preprocessing:** Reuse **FFmpeg** for audio decoding, format normalization, and preprocessing into the format required by `whisper.cpp`.
- **License Review:** Engine (`whisper.cpp`), FFmpeg integration mode, and model licenses must be independently reviewed prior to distribution (`M6`/`M7`).

### 6.2 Compression Stack
- Reuse existing Vert engines and libraries wherever appropriate (to be audited in `M0`).
- Introduce format-specific adapters for image, document/PDF, video (`MP4`), and archive (`ZIP`/`7Z`) targets as defined in `M3`–`M4`, avoiding unnecessary external dependencies when existing tools or lightweight libraries suffice.

---

## 7. Technical Architecture

Enhancement v1 enforces strict separation between **UI presentation** and **background processing / domain logic** so long-running transcription or multi-pass compression never freezes the Windows UI.

### 7.1 Feature 01 Architecture — Audio-to-Text
Suggested logical components (to be mapped to concrete repository paths in `M0`):
- **Audio Validator:** Checks file existence, extension/container validity, and basic audio integrity.
- **FFmpeg Audio Adapter:** Invokes FFmpeg to decode/convert input audio into standardized PCM/WAV format expected by `whisper.cpp`.
- **Model Manager:** Manages on-demand model downloads (with explicit user consent), local storage, installation status, integrity checks, and model removal.
- **Whisper Engine Adapter:** Encapsulates execution of `whisper.cpp` (subprocess or binding), language options, progress/cancellation hooks, and raw output retrieval.
- **Transcription Service:** Orchestrates validation, preprocessing, model availability checks, inference execution, cancellation, and temporary file cleanup.
- **Transcript Processor:** Normalizes segments, timestamps, and text for preview, manual editing, and clipboard copy.
- **Transcript Exporter:** Serializes edited transcripts into `TXT`, `SRT`, `VTT`, and `JSON`.

### 7.2 Feature 02 Architecture — Advanced File Compression
Suggested logical components (modular, format-specific adapter architecture):
- **Compression Coordinator:** Manages job lifecycle, batch coordination (as planned), cancellation, temporary file cleanup, and result aggregation.
- **File Inspector:** Detects file format and extracts metadata (size, dimensions, media/document properties) to drive UI controls and adapter selection.
- **Compression Adapter Interface:** Defines a common contract across format adapters (capabilities, parameter validation, single-pass/standard compression, and size-guided compression hooks).
- **Format-Specific Adapters:** Dedicated implementations for supported formats (e.g., JPEG, WebP, PNG, PDF, MP4, ZIP/7Z, as scoped in `M3`–`M4`).
- **Target-Size Optimizer:** Executes the bounded iterative optimization loop, parameter adjustment, and best-candidate selection for supported formats.
- **Output Validator:** Verifies output file existence, non-empty integrity, source non-mutation, and target-size status.
- **Compression Result Reporter:** Computes actual output size, compression reduction metrics, target-achieved vs. unachievable status, and explanatory messages.

---

## 8. Processing Pipelines

### 8.1 Audio-to-Text Pipeline
```text
Audio Input
  → Audio Validation
  → FFmpeg Audio Preparation (decode / resample / normalize in temp space)
  → Whisper.cpp Inference (background worker, model + language settings)
  → Transcript Processing (segments, timestamps, preview/edit)
  → User Review & Editing (plus optional clipboard copy)
  → Export (TXT / SRT / VTT / JSON) & Temp Cleanup
```

### 8.2 Advanced File Compression Pipeline
```text
Input File(s)
  → File Inspection (format detection + metadata)
  → Settings Validation (target size, quality, compression level, output path)
  → Format Adapter Selection
  → Optimization Loop (bounded iterations for target-size / parameter tuning; preserve best valid candidate)
  → Output Validation (verify output + confirm original untouched + clean temp files)
  → Compression Result Reporting (actual size, savings %, target status / explanation)
```

---

## 9. User Workflows

### 9.1 Audio-to-Text Workflow
1. **Open Audio & Speech:** Navigate to the Audio-to-Text feature area in Vert.
2. **Import Audio File:** Select an audio file via file picker or drag-and-drop (`MP3`, `WAV`, `M4A`, `FLAC`, `OGG`, `AAC`).
3. **Select Language:** Choose automatic language detection or manually select a specific language.
4. **Select Installed Model:** Choose an installed model (`Tiny`, `Base`, `Small`, `Medium`—or download one explicitly via Model Manager if none are installed).
5. **Start Transcription:** Trigger local transcription and monitor progress in the UI (with cancellation support where available).
6. **Review & Edit Transcript:** Inspect generated text/timestamps in the preview editor and make manual edits as needed.
7. **Copy or Export:** Copy the transcript to the clipboard or export to `TXT`, `SRT`, `VTT`, or `JSON`.

### 9.2 Advanced File Compression Workflow
1. **Select File(s):** Choose file(s) to compress.
2. **Inspect Format & Controls:** Review detected format/metadata and format-relevant compression controls.
3. **Configure Settings:** Set target size (preset or custom) where feasible, and/or adjust quality, compression level, dimensions/format (where supported), and output directory.
4. **Run Compression:** Execute compression locally without modifying the original source file.
5. **Inspect Results:** Review actual output size, compression reduction statistics, and whether the target size was achieved (or why it could not be reached).

---

## 10. Scope & Non-Goals (v1)

### 10.1 Explicitly Out of Scope for v1
- **Audio-to-Text Non-Goals:**
  - Real-time live microphone transcription.
  - Speaker diarization (identifying/labeling different speakers).
  - Automatic meeting summarization.
  - Cloud-based speech transcription.
  - AI-powered translation of transcripts.
- **Advanced File Compression Non-Goals:**
  - Guaranteed exact byte-for-byte target sizes across all formats.
  - Universal compression algorithms capable of arbitrarily shrinking incompressible data.
  - Cloud-based compression.
  - Destructive in-place overwriting of original source files by default.
  - Silent or automatic format conversion without explicit user consent.

---

## 11. Risks & Limitations

1. **Target-Size Unachievability:** Already-compressed files (e.g., high-entropy archives, already-compressed media, or files near their information-theoretic floor) or strict size targets may prevent reaching the requested size without severe quality loss or structural constraints. Vert must communicate this transparently rather than claiming impossible guarantees.
2. **Format-Specific Nuances:** Lossless formats like `PNG` or container/archive formats like `ZIP`/`7Z` behave very differently from lossy image (`JPEG`/`WebP`) or video (`MP4`) formats; forcing uniform controls across all formats would confuse users.
3. **Hardware & Inference Performance:** CPU inference with `whisper.cpp` and multi-pass compression (such as `MP4`) can be CPU- and memory-intensive on low-spec Windows machines. Model size selection (`Tiny`–`Medium`) and bounded optimization budgets mitigate but do not eliminate hardware limits.
4. **Repository Unknowns Prior to M0:** Because exact existing directory paths, UI components, and packaging scripts were not directly verified prior to drafting, architectural mappings in this document are logical blueprints until confirmed in `M0`.
5. **Licensing & Dependency Compliance:** Third-party engines (`whisper.cpp`, FFmpeg, codecs/libraries) and model weights carry distinct licenses that must be verified before distribution.

---

## 12. Acceptance Criteria

- **Audio-to-Text:**
  - Users can import supported audio formats (`MP3`, `WAV`, `M4A`, `FLAC`, `OGG`, `AAC`) via file picker and drag-and-drop, with clear errors for invalid/corrupted files.
  - Models (`Tiny`, `Base`, `Small`, `Medium` candidates) are not auto-downloaded without user consent; users can see size/status, download on demand, verify integrity where supported, and remove models.
  - Transcription runs locally and offline after setup without freezing the UI, supports language selection (auto and manual), and allows editing before copying or exporting to `TXT`, `SRT`, `VTT`, and `JSON`.
- **Advanced File Compression:**
  - Users can inspect formats/metadata, choose output directories, and compress files while keeping original source files intact.
  - Target-size optimization runs within a bounded iteration budget, preserves the best valid candidate, reports actual output size and reduction metrics, and clearly explains when a target cannot be met.
  - UI displays format-appropriate controls without exposing misleading or irrelevant options.
- **Cross-Feature:**
  - Offline operation works after required setup; no external uploads occur; sensitive file/transcript content is not logged by default; temporary files are cleaned up; Windows packaging succeeds.

---

## 13. Implementation Roadmap (`M0`–`M7`)

- **M0 — Repository & Architecture Review:** Inspect existing project structure, UI conventions, FFmpeg integration, packaging/dependency management, and technical constraints.
- **M1 — Audio-to-Text Foundation:** Integrate `whisper.cpp`, implement model management, implement FFmpeg audio preprocessing, implement transcription service, and validate offline execution.
- **M2 — Audio-to-Text UI & Export:** Build transcription interface, add language and model selection, add transcript editor, and implement `TXT`, `SRT`, `VTT`, and `JSON` export.
- **M3 — Compression Foundation:** Define compression adapter interface, implement file inspection, select initial supported formats, and define target-size request and validation.
- **M4 — Target-Size Optimization:** Implement format-specific optimization, iterative compression within bounded retries, output measurement, and target-achieved / target-unachievable reporting.
- **M5 — Compression UI:** Add compression interface, target-size controls, quality/compression settings, and estimation/result reporting.
- **M6 — Integration & QA:** Test both features, offline behavior, cancellation and error handling, source file preservation, Windows packaging, and license review.
- **M7 — Documentation & Release:** Update `README`, document supported formats and limitations, update dependency notices, and prepare release notes.

---

## 14. Definition of Done

Enhancement v1 is complete when all of the following are satisfied:
1. Audio files can be transcribed locally.
2. Transcription works offline after model installation.
3. Users can review and export transcripts in all promised formats (`TXT`, `SRT`, `VTT`, `JSON`).
4. Compression supports documented format-specific settings.
5. Target-size optimization works for supported formats.
6. Actual output sizes are measured and reported.
7. Impossible targets are communicated transparently.
8. Original files remain untouched by default.
9. Both features are integrated into Vert's existing UI and architecture.
10. Functional testing, privacy validation, and Windows packaging are completed.