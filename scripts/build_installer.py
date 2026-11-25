"""Automated release build script for Vert.

Steps:
1. Runs full test suite (pytest) to guarantee zero regressions.
2. Compiles standalone bundle using PyInstaller ('vert.spec').
3. Looks for Inno Setup compiler (iscc.exe) to generate 'Vert_Setup.exe'.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"


def log(msg: str):
    print(f"\n[Vert Release Builder] === {msg} ===")


def find_inno_compiler() -> Path | None:
    # Check PATH
    iscc = shutil.which("iscc")
    if iscc:
        return Path(iscc)

    # Check standard install locations
    candidates = [
        Path(os.path.expanduser(r"~\AppData\Local\Programs\Inno Setup 6\ISCC.exe")),
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def run_tests():
    log("Running automated test suite")
    cmd = [sys.executable, "-m", "pytest", "-v"]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print("\nERROR: Tests failed! Aborting build.")
        sys.exit(1)
    print("All tests passed!")


def build_pyinstaller():
    log("Building PyInstaller standalone executable")
    spec_file = ROOT_DIR / "vert.spec"
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", str(spec_file)]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print("\nERROR: PyInstaller build failed!")
        sys.exit(1)

    built_exe = DIST_DIR / "Vert" / "Vert.exe"
    if not built_exe.exists():
        print(f"\nERROR: Expected executable not found at {built_exe}")
        sys.exit(1)

    print(f"PyInstaller standalone package built at: {DIST_DIR / 'Vert'}")


def build_inno_installer():
    log("Compiling Inno Setup installer (Vert_Setup.exe)")
    iscc_bin = find_inno_compiler()
    if not iscc_bin:
        print(
            "\n[NOTE] Inno Setup compiler (ISCC.exe) was not found on this system.\n"
            "To generate the single-click 'Vert_Setup.exe' installer:\n"
            "  1. Download Inno Setup 6 (free) from: https://jrsoftware.org/isdl.php\n"
            "  2. Right-click 'installer/vert_setup.iss' and select 'Compile'.\n"
            f"The standalone app folder is already ready at: '{DIST_DIR / 'Vert'}'"
        )
        return

    iss_file = ROOT_DIR / "installer" / "vert_setup.iss"
    cmd = [str(iscc_bin), str(iss_file)]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print("\nERROR: Inno Setup compilation failed!")
        sys.exit(1)

    setup_exe = DIST_DIR / "Vert_Setup.exe"
    if setup_exe.exists():
        mb_size = setup_exe.stat().st_size / (1024 * 1024)
        print(f"\nSUCCESS: Setup installer created at:\n  {setup_exe} ({mb_size:.1f} MB)")


def main():
    print("Starting Vert Release Build Pipeline...")
    run_tests()
    build_pyinstaller()
    build_inno_installer()


if __name__ == "__main__":
    main()
