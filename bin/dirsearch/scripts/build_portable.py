#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

try:
    from configure_stack import configure
except ModuleNotFoundError:
    from scripts.configure_stack import configure


PBS_REPOSITORY = "astral-sh/python-build-standalone"
PBS_API = f"https://api.github.com/repos/{PBS_REPOSITORY}/releases"
TARGETS = {
    "linux-x64": {
        "triple": "x86_64-unknown-linux-gnu",
        "archive": "tar.gz",
        "python": ("bin", "python3"),
    },
    "linux-arm64": {
        "triple": "aarch64-unknown-linux-gnu",
        "archive": "tar.gz",
        "python": ("bin", "python3"),
    },
    "windows-x64": {
        "triple": "x86_64-pc-windows-msvc",
        "archive": "zip",
        "python": ("python.exe",),
    },
    "macos-intel": {
        "triple": "x86_64-apple-darwin",
        "archive": "tar.gz",
        "python": ("bin", "python3"),
    },
    "macos-silicon": {
        "triple": "aarch64-apple-darwin",
        "archive": "tar.gz",
        "python": ("bin", "python3"),
    },
}


def run(command: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def github_request(url: str) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dirsearch-portable-builder",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def release_metadata(tag: str) -> dict:
    if tag == "latest":
        url = f"{PBS_API}/latest"
    else:
        url = f"{PBS_API}/tags/{tag}"

    with urllib.request.urlopen(github_request(url), timeout=60) as response:
        return json.load(response)


def select_python_asset(release: dict, python_version: str, target: str) -> dict:
    triple = TARGETS[target]["triple"]
    prefix = f"cpython-{python_version}."
    suffix = f"-{triple}-install_only_stripped.tar.gz"
    matches = [
        asset
        for asset in release["assets"]
        if asset["name"].startswith(prefix)
        and asset["name"].endswith(suffix)
        and "freethreaded" not in asset["name"]
    ]
    if len(matches) != 1:
        names = "\n".join(asset["name"] for asset in release["assets"] if triple in asset["name"])
        raise RuntimeError(
            f"Expected one python-build-standalone asset for {python_version} {target}; "
            f"found {len(matches)}.\nCandidates:\n{names}"
        )
    return matches[0]


def download(url: str, destination: Path) -> None:
    with urllib.request.urlopen(github_request(url), timeout=120) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def extract_python(archive: Path, destination: Path) -> Path:
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(destination)

    candidates = [
        path
        for path in destination.rglob("*")
        if path.is_dir() and ((path / "bin" / "python3").exists() or (path / "python.exe").exists())
    ]
    if not candidates:
        raise RuntimeError(f"No Python install directory found after extracting {archive}")

    return sorted(candidates, key=lambda path: len(path.parts))[0]


def copy_app(project_root: Path, destination: Path) -> None:
    ignored = shutil.ignore_patterns(
        ".git",
        ".github",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "benchmarks",
        "build",
        "dist",
        "portable",
        "sessions",
        "target",
        "tests",
    )
    shutil.copytree(project_root, destination, ignore=ignored)


def chmod_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_launchers(stage: Path, target: str) -> None:
    if target.startswith("windows"):
        launcher = stage / "dirsearch.cmd"
        launcher.write_text(
            "@echo off\r\n"
            "set DIRSEARCH_HOME=%~dp0\r\n"
            "\"%DIRSEARCH_HOME%python\\python.exe\" "
            "\"%DIRSEARCH_HOME%app\\dirsearch.py\" %*\r\n",
            encoding="utf-8",
        )
        return

    launcher = stage / "dirsearch"
    launcher.write_text(
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "DIRSEARCH_HOME=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)\n"
        "exec \"$DIRSEARCH_HOME/python/bin/python3\" "
        "\"$DIRSEARCH_HOME/app/dirsearch.py\" \"$@\"\n",
        encoding="utf-8",
    )
    chmod_executable(launcher)


def install_dependencies(python: Path, app: Path, stack: str) -> None:
    run([str(python), "-m", "ensurepip", "--upgrade"])
    run([str(python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--only-binary=:all:",
            "-r",
            str(app / "requirements.txt"),
            "-r",
            str(app / "requirements" / "db.txt"),
        ]
    )

    if stack == "native-rust":
        run([str(python), "-m", "pip", "install", "--only-binary=:all:", "maturin"])
        wheel_dir = app.parent / "native-wheels"
        run(
            [
                str(python),
                str(app / "scripts" / "build_native.py"),
                "--python",
                str(python),
                "--out",
                str(wheel_dir),
            ]
        )
        run([str(python), "-m", "pip", "uninstall", "-y", "maturin"])
        shutil.rmtree(wheel_dir, ignore_errors=True)
        shutil.rmtree(app / "native" / "target", ignore_errors=True)


def find_python(stage: Path, target: str) -> Path:
    return stage / "python" / Path(*TARGETS[target]["python"])


def archive_stage(stage: Path, output: Path, archive_type: str) -> None:
    if archive_type == "zip":
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for path in sorted(stage.rglob("*")):
                zip_file.write(path, path.relative_to(stage.parent))
        return

    with tarfile.open(output, "w:gz") as tar:
        tar.add(stage, arcname=stage.name)


def build(args: argparse.Namespace) -> None:
    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    release = release_metadata(args.python_build_standalone_release)
    asset = select_python_asset(release, args.python_version, args.target)
    print(f"Using {asset['name']} from python-build-standalone {release['tag_name']}")

    with tempfile.TemporaryDirectory(prefix="dirsearch-portable-") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / asset["name"]
        download(asset["browser_download_url"], archive)

        extracted = tmp_path / "extracted"
        extracted.mkdir()
        python_install = extract_python(archive, extracted)

        artifact_name = f"dirsearch-{args.release_tag}-{args.target}-{args.stack}-portable"
        stage = tmp_path / artifact_name
        shutil.copytree(python_install, stage / "python")
        copy_app(project_root, stage / "app")
        configure(stage / "app" / "config.ini", args.stack)
        install_dependencies(find_python(stage, args.target), stage / "app", args.stack)
        write_launchers(stage, args.target)

        suffix = ".zip" if TARGETS[args.target]["archive"] == "zip" else ".tar.gz"
        archive_stage(stage, output_dir / f"{artifact_name}{suffix}", TARGETS[args.target]["archive"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a portable dirsearch distribution")
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", default="portable/dist")
    parser.add_argument("--release-tag", default="v0.5.0-rc1")
    parser.add_argument("--python-version", default="3.14")
    parser.add_argument("--python-build-standalone-release", default="latest")
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument("--stack", choices=("threaded", "async", "native-rust"), required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    main()
