from pathlib import Path
from core.updater import parse_semver, is_newer_version
from core.version import __version__


def test_parse_semver():
    assert parse_semver("1.0.0") == (1, 0, 0)
    assert parse_semver("v1.2.3") == (1, 2, 3)
    assert parse_semver("v2.10.4-beta") == (2, 10, 4)


def test_is_newer_version():
    assert is_newer_version("v1.0.1", "1.0.0")
    assert is_newer_version("2.0.0", "1.9.9")
    assert not is_newer_version("1.0.0", "1.0.0")
    assert not is_newer_version("0.9.0", "1.0.0")


from unittest.mock import patch
import urllib.error

def test_check_github_releases_empty_repo_handles_404():
    from core.updater import check_github_releases
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            url="https://api.github.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )
        has_update, tag, url, body = check_github_releases()
        assert has_update is False
        assert tag == f"v{__version__}"


def test_update_download_task_signals():
    from core.updater import UpdateDownloadTask
    task = UpdateDownloadTask("https://example.com/dummy.exe")
    assert task.download_url == "https://example.com/dummy.exe"
    task.cancel()
    assert task._is_cancelled is True


def test_update_dialog_creation(qapp):
    from ui.update_dialog import UpdateDialog
    dlg = UpdateDialog("v1.1.0", "https://example.com/setup.exe", "Release notes here")
    assert dlg.new_tag == "v1.1.0"
    assert "v1.1.0" in dlg.windowTitle() or "Software Update" in dlg.windowTitle()
    dlg.close()

