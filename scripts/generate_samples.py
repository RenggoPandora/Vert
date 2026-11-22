"""Generate real test samples across all file types for testing Vert."""

from pathlib import Path
from PIL import Image
import pymupdf as fitz
import subprocess
import shutil

ROOT_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT_DIR / "test_samples"
ENGINES_DIR = ROOT_DIR / "engines"


def generate_all():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating test files in: {SAMPLES_DIR}")

    # 1. Images
    img1 = SAMPLES_DIR / "sample_image1.png"
    Image.new("RGB", (320, 240), (46, 204, 113)).save(img1)
    img2 = SAMPLES_DIR / "sample_image2.jpg"
    Image.new("RGB", (320, 240), (52, 152, 219)).save(img2)
    print("[OK] Created sample_image1.png, sample_image2.jpg")

    # 2. PDF
    doc = fitz.open()
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 60), "Vert Offline Converter - Sample PDF Page 1", fontsize=18)
    p1.insert_text((50, 100), "First column | Second column | Status\n100 | Active | Verified", fontsize=12)
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((50, 60), "Sample PDF Page 2", fontsize=18)
    pdf_path = SAMPLES_DIR / "sample_multipage.pdf"
    doc.save(str(pdf_path))
    doc.close()
    print("[OK] Created sample_multipage.pdf")

    # 3. Data CSV & JSON
    csv_path = SAMPLES_DIR / "sample_data.csv"
    csv_path.write_text("id,department,budget\n1,Engineering,150000\n2,Design,80000\n", encoding="utf-8")
    json_path = SAMPLES_DIR / "sample_records.json"
    json_path.write_text('[{"product": "Widget A", "units": 50}, {"product": "Widget B", "units": 120}]', encoding="utf-8")
    print("[OK] Created sample_data.csv, sample_records.json")

    # 4. Video MP4 (if ffmpeg exists)
    ffmpeg_bin = ENGINES_DIR / "ffmpeg.exe"
    if not ffmpeg_bin.exists():
        sys_ffmpeg = shutil.which("ffmpeg")
        if sys_ffmpeg:
            ffmpeg_bin = Path(sys_ffmpeg)

    if ffmpeg_bin.exists():
        mp4_path = SAMPLES_DIR / "sample_video.mp4"
        cmd = [
            str(ffmpeg_bin),
            "-y",
            "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=2",
            "-c:v", "libx264", "-c:a", "aac",
            str(mp4_path),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[OK] Created sample_video.mp4")
    else:
        print("[WARN] Skipped sample_video.mp4 (ffmpeg.exe missing in engines/)")

    print("\nAll sample files ready in 'test_samples/'!")


if __name__ == "__main__":
    generate_all()
