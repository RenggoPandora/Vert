"""Speech recognition model management for whisper.cpp in Vert."""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import shutil
import urllib.request
from typing import Callable, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODELS_DIR = ROOT_DIR / "engines" / "models" / "whisper"


@dataclass(frozen=True)
class WhisperModelInfo:
    name: str
    display_name: str
    filename: str
    size_mb: int
    url: str
    sha256: str
    description: str


# Official ggml models hosted on Hugging Face ggerganov/whisper.cpp
MODEL_CATALOG: dict[str, WhisperModelInfo] = {
    "tiny": WhisperModelInfo(
        name="tiny",
        display_name="Tiny (Fastest, ~75 MB)",
        filename="ggml-tiny.bin",
        size_mb=75,
        url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
        sha256="bd577a113a864445d4c299885e8aa5cd9556bd7d00482f508e0fa20328f47786",
        description="Fastest execution, lowest memory footprint. Good for quick draft transcriptions.",
    ),
    "base": WhisperModelInfo(
        name="base",
        display_name="Base (Default, ~142 MB)",
        filename="ggml-base.bin",
        size_mb=142,
        url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
        sha256="465707469f3560b2b881a605159081b7a1a089b8b09f3b68656cb9c465a9f6d0",
        description="Best balance of speed and accuracy for everyday use.",
    ),
    "small": WhisperModelInfo(
        name="small",
        display_name="Small (Accurate, ~466 MB)",
        filename="ggml-small.bin",
        size_mb=466,
        url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
        sha256="55356645c2b361a969dfd0ef2c5a50d530abb43a3170557a4427f35ccd24d33e",
        description="Higher accuracy, handles background noise and accents better. Moderate compute.",
    ),
    "medium": WhisperModelInfo(
        name="medium",
        display_name="Medium (High Precision, ~1.5 GB)",
        filename="ggml-medium.bin",
        size_mb=1533,
        url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
        sha256="fd9727b6e1217c2f614f9b698455c4aff8246382f2b3733cf96e49a204e470fa",
        description="Strong accuracy for complex or multilingual audio. Requires capable hardware.",
    ),
}


def get_models_dir() -> Path:
    """Return local directory used to store downloaded whisper models."""
    target_dir = DEFAULT_MODELS_DIR
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = target_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        return target_dir
    except (OSError, PermissionError):
        user_dir = Path.home() / ".vert" / "models" / "whisper"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir


def get_model_path(name: str) -> Optional[Path]:
    """Return Path to local model file if installed, else None."""
    info = MODEL_CATALOG.get(name.lower())
    if not info:
        return None
    model_file = get_models_dir() / info.filename
    if model_file.exists() and model_file.stat().st_size > 1024 * 1024:
        return model_file
    return None


def is_model_installed(name: str) -> bool:
    """Check if model exists locally and has valid file size."""
    return get_model_path(name) is not None


def verify_model_checksum(name: str) -> bool:
    """Verify SHA-256 checksum of installed model."""
    info = MODEL_CATALOG.get(name.lower())
    path = get_model_path(name)
    if not info or not path:
        return False
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower() == info.sha256.lower()


def delete_model(name: str) -> bool:
    """Remove installed model from disk."""
    path = get_model_path(name)
    if path and path.exists():
        path.unlink()
        return True
    return False


def download_model(
    name: str,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    is_cancelled: Optional[Callable[[], bool]] = None,
) -> Path:
    """Download model with explicit user trigger and progress tracking."""
    info = MODEL_CATALOG.get(name.lower())
    if not info:
        raise ValueError(f"Unknown whisper model: {name}")

    dest_dir = get_models_dir()
    final_path = dest_dir / info.filename
    temp_path = dest_dir / f"{info.filename}.part"

    if final_path.exists() and final_path.stat().st_size > 1024 * 1024:
        if progress_callback:
            progress_callback(100.0, "Model already installed.")
        return final_path

    req = urllib.request.Request(
        info.url,
        headers={"User-Agent": "Vert-Desktop-SpeechRecognition/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get("content-length", info.size_mb * 1024 * 1024))
            downloaded = 0
            block_size = 1024 * 128  # 128 KB chunks

            with open(temp_path, "wb") as out_file:
                while True:
                    if is_cancelled and is_cancelled():
                        out_file.close()
                        if temp_path.exists():
                            temp_path.unlink()
                        raise InterruptedError("Download cancelled by user.")

                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback and total_size > 0:
                        pct = min(100.0, (downloaded / total_size) * 100)
                        mb_curr = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        progress_callback(pct, f"Downloading: {mb_curr:.1f} / {mb_tot:.1f} MB ({pct:.0f}%)")

        if temp_path.exists():
            if final_path.exists():
                final_path.unlink()
            temp_path.rename(final_path)

        if progress_callback:
            progress_callback(100.0, "Download complete.")
        return final_path

    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
