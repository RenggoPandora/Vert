"""Engine download and verification script for Vert.

Fetches standalone portable binaries for development and installer packaging:
- ffmpeg (essentials build for Windows)
- LibreOffice Portable (or checks local installation)
"""

import argparse
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ENGINES_DIR = ROOT_DIR / "engines"

FFMPEG_URL = (
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
)


def log(msg: str) -> None:
    print(f"[Vert Engine Setup] {msg}")


def download_file(url: str, dest_path: Path) -> None:
    log(f"Downloading: {url} -> {dest_path.name}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Use curl if present for automatic resume and high speed
    curl_bin = shutil.which("curl")
    if curl_bin:
        ret = os.system(f'curl.exe -C - -L -o "{dest_path}" "{url}"')
        if ret == 0 and dest_path.exists():
            return

    def report_progress(block_num, block_size, total_size):
        if total_size <= 0:
            return
        downloaded = block_num * block_size
        percent = min(100.0, (downloaded / total_size) * 100)
        mb_down = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        sys.stdout.write(
            f"\r  Progress: {percent:5.1f}% ({mb_down:6.1f} MB / {mb_total:6.1f} MB)"
        )
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
    print()


def setup_ffmpeg() -> bool:
    ENGINES_DIR.mkdir(parents=True, exist_ok=True)
    target_ffmpeg = ENGINES_DIR / "ffmpeg.exe"

    if target_ffmpeg.exists():
        log(f"ffmpeg.exe already present: {target_ffmpeg}")
        return True

    # Check if system ffmpeg exists
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        log(f"System ffmpeg found at: {system_ffmpeg}. Copying to engines/...")
        shutil.copy2(system_ffmpeg, target_ffmpeg)
        return True

    zip_tmp = ENGINES_DIR / "ffmpeg_temp.zip"
    try:
        download_file(FFMPEG_URL, zip_tmp)
        log("Extracting ffmpeg.exe...")
        with zipfile.ZipFile(zip_tmp, "r") as zf:
            for member in zf.namelist():
                if member.endswith("bin/ffmpeg.exe"):
                    with zf.open(member) as src, open(target_ffmpeg, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    break
        if target_ffmpeg.exists():
            log(f"ffmpeg.exe extracted successfully: {target_ffmpeg}")
            return True
        else:
            log("Error: ffmpeg.exe not found in downloaded zip.")
            return False
    except Exception as exc:
        log(f"Failed to setup ffmpeg: {exc}")
        return False
    finally:
        if zip_tmp.exists():
            zip_tmp.unlink(missing_ok=True)


def check_status() -> None:
    ENGINES_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = ENGINES_DIR / "ffmpeg.exe"
    lo_dir = ENGINES_DIR / "LibreOfficePortable"

    print("\n--- Vert Engines Status ---")
    print(f"Directory: {ENGINES_DIR}")
    print(f"ffmpeg.exe:             {'[FOUND]' if ffmpeg_exe.exists() else '[MISSING]'}")
    print(f"LibreOfficePortable:    {'[FOUND]' if lo_dir.exists() else '[MISSING] (or system MS Office fallback)'}")
    print("---------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Download & verify Vert external engines")
    parser.add_argument("--check", action="store_true", help="Check engine status")
    parser.add_argument("--ffmpeg", action="store_true", help="Download/extract ffmpeg")
    parser.add_argument("--all", action="store_true", help="Setup all required engines")
    args = parser.parse_args()

    if args.check or (not args.ffmpeg and not args.all):
        check_status()
        return

    if args.ffmpeg or args.all:
        setup_ffmpeg()

    check_status()


if __name__ == "__main__":
    main()
