"""Contracts, data classes, and base interfaces for file compression."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


class CompressionCategory(str, Enum):
    IMAGE = "Image"
    PDF = "PDF Document"
    VIDEO = "Video & Media"
    ARCHIVE = "Archive"
    UNSUPPORTED = "Unsupported"


@dataclass
class CompressionRequest:
    src_path: Path
    dst_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    # Target size: explicit bytes or relative percentage (1-99% of original size)
    target_size_bytes: Optional[int] = None
    target_percent: Optional[int] = None
    # Manual tuning overrides
    quality: Optional[int] = None  # 1 to 100
    resolution_scale: float = 1.0  # 0.1 to 1.0
    preset: str = "balanced"       # "fast", "balanced", "maximum"


@dataclass
class CompressionResult:
    success: bool
    src_path: Path
    dst_path: Path
    original_size_bytes: int
    compressed_size_bytes: int
    savings_bytes: int
    savings_ratio: float  # e.g. 0.40 = 40% reduction
    target_achieved: Optional[bool] = None
    target_unachievable_reason: Optional[str] = None
    iterations: int = 1
    message: str = ""

    @property
    def savings_percent_str(self) -> str:
        return f"{self.savings_ratio * 100:.1f}%"


def compute_safe_output_path(src_path: Path, output_dir: Optional[Path] = None, ext_override: Optional[str] = None) -> Path:
    """Generate safe destination path that never overwrites the source file."""
    src = Path(src_path).resolve()
    target_dir = Path(output_dir).resolve() if output_dir else src.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = ext_override if ext_override else src.suffix
    stem = src.stem

    # Suffix with _compressed
    candidate = target_dir / f"{stem}_compressed{ext}"
    counter = 1
    while candidate.resolve() == src or candidate.exists():
        candidate = target_dir / f"{stem}_compressed_{counter}{ext}"
        counter += 1

    return candidate


def format_bytes_human(num_bytes: int) -> str:
    """Format bytes to human readable string (KB, MB, GB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    elif num_bytes < 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.2f} MB"
    return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"


class CompressionAdapter(ABC):
    """Abstract interface for format-specific compression handlers."""

    @abstractmethod
    def can_handle(self, src_path: Path) -> bool:
        """Return True if this adapter supports compressing the given file."""
        pass

    @abstractmethod
    def compress(
        self,
        request: CompressionRequest,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> CompressionResult:
        """Execute compression on file according to request parameters."""
        pass

    def estimate_compressed_size(self, request: CompressionRequest) -> Optional[int]:
        """Optionally return an estimated output size in bytes."""
        return None
