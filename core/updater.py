"""On-demand update checker using GitHub Releases API (zero startup calls)."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Callable, Optional, Tuple
import urllib.error
import urllib.request
from PySide6.QtCore import QObject, QRunnable, Signal

from core.version import GITHUB_REPO, __version__


def parse_semver(v: str) -> tuple[int, ...]:
    clean = v.strip().lstrip("v").split("-")[0]
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def is_newer_version(latest_tag: str, current_ver: str = __version__) -> bool:
    return parse_semver(latest_tag) > parse_semver(current_ver)


def check_github_releases(timeout: int = 5) -> Tuple[bool, str, str, str]:
    """Check GitHub API for latest release.

    Returns:
        (has_update, latest_version_tag, download_url, release_body)
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Vert-Desktop/{__version__}"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag_name = data.get("tag_name", "").strip()
        body = data.get("body", "").strip()
        html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")

        # Find direct installer exe in release assets if available
        installer_url = html_url
        for asset in data.get("assets", []):
            name = asset.get("name", "").lower()
            if name.endswith(".exe") or "setup" in name:
                installer_url = asset.get("browser_download_url", html_url)
                break

        has_update = is_newer_version(tag_name, __version__)
        return (has_update, tag_name, installer_url, body)

    except urllib.error.HTTPError as http_err:
        if http_err.code == 404:
            # 404 means the GitHub repository has no published releases yet
            return (
                False,
                f"v{__version__}",
                f"https://github.com/{GITHUB_REPO}/releases",
                "No public release published on GitHub yet.",
            )
        raise RuntimeError(f"GitHub returned HTTP status {http_err.code} ({http_err.reason})")

    except Exception as exc:
        raise RuntimeError(f"Network error: {exc}")


class UpdateSignals(QObject):
    checked = Signal(bool, str, str, str)  # has_update, tag, url, body
    failed = Signal(str)                   # error message


class UpdateDownloadSignals(QObject):
    started = Signal()
    progress = Signal(float, str)          # percent, status message
    finished = Signal(str)                 # downloaded_installer_path
    failed = Signal(str)                   # error message
    cancelled = Signal()


class UpdateDownloadTask(QRunnable):
    """Downloads installer exe directly to system %TEMP% directory with progress tracking."""

    def __init__(self, download_url: str):
        super().__init__()
        self.download_url = download_url
        self.signals = UpdateDownloadSignals()
        self.setAutoDelete(False)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        self.signals.started.emit()
        temp_dir = Path(tempfile.gettempdir())
        dest_exe = temp_dir / "Vert_Setup_Update.exe"
        part_exe = temp_dir / "Vert_Setup_Update.part"

        req = urllib.request.Request(
            self.download_url,
            headers={
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Vert/{__version__}",
                "Accept": "*/*",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_bytes = int(resp.headers.get("content-length") or (170 * 1024 * 1024))
                downloaded = 0
                block_size = 1024 * 256  # 256 KB

                with open(part_exe, "wb") as f:
                    while True:
                        if self._is_cancelled:
                            f.close()
                            if part_exe.exists():
                                part_exe.unlink()
                            self.signals.cancelled.emit()
                            return

                        chunk = resp.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        pct = min(100.0, (downloaded / total_bytes) * 100) if total_bytes > 0 else 0
                        mb_curr = downloaded / (1024 * 1024)
                        mb_tot = total_bytes / (1024 * 1024)
                        self.signals.progress.emit(
                            pct,
                            f"Downloading update: {mb_curr:.1f} / {mb_tot:.1f} MB ({pct:.0f}%)",
                        )

            if part_exe.exists():
                if dest_exe.exists():
                    try:
                        dest_exe.unlink()
                    except OSError:
                        pass
                part_exe.rename(dest_exe)

            self.signals.finished.emit(str(dest_exe))

        except Exception as exc:
            if part_exe.exists():
                try:
                    part_exe.unlink()
                except OSError:
                    pass
            self.signals.failed.emit(str(exc))


def launch_installer_and_exit(installer_path: str):
    """Executes downloaded installer silently and restarts the application without manual prompts."""
    # /SILENT /CLOSEAPPLICATIONS ensures old running instance is closed cleanly and files replaced
    cmd = [installer_path, "/SILENT", "/CLOSEAPPLICATIONS"]
    creation_flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW or detach
    subprocess.Popen(cmd, creationflags=creation_flags)


class UpdateCheckTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = UpdateSignals()
        self.setAutoDelete(False)

    def run(self):
        try:
            has_up, tag, url, body = check_github_releases()
            self.signals.checked.emit(has_up, tag, url, body)
        except Exception as exc:
            self.signals.failed.emit(str(exc))
