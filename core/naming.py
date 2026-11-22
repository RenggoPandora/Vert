"""Safe file naming utilities."""

from pathlib import Path


def get_safe_output_path(target_dir: Path | str, base_filename: str, target_extension: str) -> Path:
    """Generate collision-free destination file path.

    If target file already exists, appends ' (1)', ' (2)', etc.
    """
    directory = Path(target_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)

    # Normalize target extension to ensure leading dot
    ext = target_extension if target_extension.startswith(".") else f".{target_extension}"
    stem = Path(base_filename).stem

    candidate = directory / f"{stem}{ext}"
    if not candidate.exists():
        return candidate

    counter = 1
    while True:
        candidate = directory / f"{stem} ({counter}){ext}"
        if not candidate.exists():
            return candidate
        counter += 1
