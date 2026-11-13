"""Tests for the Qt-free auto-update helpers."""

import hashlib

import pytest

from dwellpy.utils import updater
from dwellpy.utils.updater import InstallMethod, ReleaseAsset, ReleaseInfo


@pytest.mark.parametrize("candidate,current,expected", [
    ("0.13.0", "0.12.3", True),
    ("v0.12.4", "0.12.3", True),
    ("1.0", "0.99.99", True),
    ("0.12.3", "0.12.3", False),
    ("0.12.2", "0.12.3", False),
    ("0.12.3", "0.12.3-rc1", True),
    ("0.12.3-rc1", "0.12.3", False),
    ("0.12.10", "0.12.9", True),
])
def test_is_newer_version(candidate, current, expected):
    assert updater.is_newer_version(candidate, current) is expected


def test_parse_version_rejects_garbage():
    with pytest.raises(ValueError):
        updater.parse_version("latest")


def _release_json(**overrides):
    data = {
        "tag_name": "v0.13.0",
        "html_url": "https://github.com/code0nwheels/Dwellpy/releases/tag/v0.13.0",
        "body": "notes",
        "draft": False,
        "prerelease": False,
        "assets": [
            {"name": "dwellpy-installer-0.13.0-windows-x64.exe", "size": 10,
             "digest": "sha256:aa", "browser_download_url": "https://example/win.exe"},
            {"name": "dwellpy-0.13.0-linux-debian-x64.deb", "size": 20,
             "browser_download_url": "https://example/x64.deb"},
            {"name": "dwellpy-0.13.0-linux-debian-arm64.deb", "size": 20,
             "browser_download_url": "https://example/arm64.deb"},
            {"name": "dwellpy-installer-0.13.0-macos-x64.dmg", "size": 30,
             "browser_download_url": "https://example/mac.dmg"},
        ],
    }
    data.update(overrides)
    return data


def test_parse_release():
    release = updater.parse_release(_release_json())
    assert release.version == "0.13.0"
    assert release.tag == "v0.13.0"
    assert len(release.assets) == 4
    assert release.assets[0].digest == "sha256:aa"
    assert release.assets[1].digest is None


def test_parse_release_rejects_prerelease():
    with pytest.raises(ValueError):
        updater.parse_release(_release_json(prerelease=True))


@pytest.mark.parametrize("method,machine,expected", [
    (InstallMethod.WINDOWS_INSTALLER, "AMD64", "dwellpy-installer-0.13.0-windows-x64.exe"),
    (InstallMethod.MACOS_DMG, "arm64", "dwellpy-installer-0.13.0-macos-x64.dmg"),
    (InstallMethod.LINUX_DEB, "x86_64", "dwellpy-0.13.0-linux-debian-x64.deb"),
    (InstallMethod.LINUX_DEB, "aarch64", "dwellpy-0.13.0-linux-debian-arm64.deb"),
    (InstallMethod.LINUX_DEB, "riscv64", None),
    (InstallMethod.MANUAL, "x86_64", None),
])
def test_select_asset(method, machine, expected):
    release = updater.parse_release(_release_json())
    asset = updater.select_asset(release, method, machine=machine)
    assert (asset.name if asset else None) == expected


def test_select_asset_missing_platform():
    release = ReleaseInfo(version="0.13.0", tag="v0.13.0", html_url="x",
                          assets=[ReleaseAsset("dwellpy-0.13.0-linux-debian-x64.deb", "u")])
    assert updater.select_asset(release, InstallMethod.WINDOWS_INSTALLER) is None


def test_detect_install_method():
    assert updater.detect_install_method("Windows", frozen=False) is InstallMethod.MANUAL
    assert updater.detect_install_method("Windows", frozen=True) is InstallMethod.WINDOWS_INSTALLER
    assert updater.detect_install_method(
        "Darwin", frozen=True, executable="/Applications/Dwellpy.app/Contents/MacOS/Dwellpy"
    ) is InstallMethod.MACOS_DMG
    assert updater.detect_install_method(
        "Darwin", frozen=True, executable="/usr/local/bin/dwellpy") is InstallMethod.MANUAL
    assert updater.detect_install_method(
        "Linux", frozen=True, executable="/opt/elsewhere/dwellpy") is InstallMethod.MANUAL


def test_verify_digest(tmp_path):
    f = tmp_path / "pkg.bin"
    f.write_bytes(b"dwellpy")
    good = "sha256:" + hashlib.sha256(b"dwellpy").hexdigest()
    assert updater.verify_digest(f, good)
    assert updater.verify_digest(f, good.upper().replace("SHA256", "sha256"))
    assert not updater.verify_digest(f, "sha256:" + "0" * 64)
    assert not updater.verify_digest(f, "md5:abc")
    assert updater.verify_digest(f, None)


def test_launch_installer_manual_raises():
    with pytest.raises(updater.InstallLaunchError):
        updater.launch_installer(InstallMethod.MANUAL, "x")


def test_linux_deb_install_command(monkeypatch):
    monkeypatch.setattr(updater, "_which", lambda cmd: "/usr/bin/pkexec")
    assert updater.linux_deb_install_command("/tmp/x.deb") == ["pkexec", "dpkg", "-i", "/tmp/x.deb"]
    monkeypatch.setattr(updater, "_which", lambda cmd: None)
    with pytest.raises(updater.InstallLaunchError):
        updater.linux_deb_install_command("/tmp/x.deb")
