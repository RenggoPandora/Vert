"""On-demand update checker using GitHub Releases API (zero startup calls)."""

import json
import urllib.request
from typing import Optional, Tuple
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
            if resp.status != 200:
                raise RuntimeError(f"GitHub returned HTTP status {resp.status}")
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

    except Exception as exc:
        raise RuntimeError(f"Could not connect to update server: {exc}")


class UpdateSignals(QObject):
    checked = Signal(bool, str, str, str)  # has_update, tag, url, body
    failed = Signal(str)                   # error message


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
