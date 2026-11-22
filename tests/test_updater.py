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


def test_check_github_releases_empty_repo_handles_404():
    from core.updater import check_github_releases
    has_update, tag, url, body = check_github_releases()
    assert has_update is False
    assert tag == f"v{__version__}"

