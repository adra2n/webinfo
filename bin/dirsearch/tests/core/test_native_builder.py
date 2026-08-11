import tempfile
from pathlib import Path
from unittest import TestCase

from lib.core.native_builder import (
    NATIVE_SOURCE_FILES,
    get_prerequisite_errors,
    install_hint,
    native_sources_available,
)


def create_native_source_tree(root: Path) -> Path:
    source = root / "native"
    for file_name in NATIVE_SOURCE_FILES:
        path = source / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return source


class TestNativeBuilder(TestCase):
    def test_native_sources_available_requires_all_files(self):
        with tempfile.TemporaryDirectory() as directory:
            source = create_native_source_tree(Path(directory))

            self.assertTrue(native_sources_available(source))

            (source / "Cargo.lock").unlink()

            self.assertFalse(native_sources_available(source))

    def test_prerequisite_errors_report_missing_commands_and_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            source = create_native_source_tree(Path(directory))
            errors = get_prerequisite_errors(
                source_dir=source,
                version_info=(3, 14, 0),
                which=lambda _: None,
                has_pip=True,
                has_python_headers=False,
            )

        self.assertIn("Required command not found: cargo", errors)
        self.assertIn("Required command not found: rustc", errors)
        self.assertIn("Required C compiler not found: cc, gcc, or clang", errors)
        self.assertIn("Python development headers not found for Python 3.14.", errors)

    def test_prerequisite_errors_report_python_version(self):
        with tempfile.TemporaryDirectory() as directory:
            source = create_native_source_tree(Path(directory))
            errors = get_prerequisite_errors(
                source_dir=source,
                version_info=(3, 12, 3),
                which=lambda _: "/usr/bin/tool",
                has_pip=True,
                has_python_headers=True,
            )

        self.assertEqual(len(errors), 1)
        self.assertIn("requires Python 3.14 or newer", errors[0])

    def test_install_hint_for_debian_like_systems(self):
        hint = install_hint({"ID": "debian", "ID_LIKE": ""})

        self.assertIn("apt-get install", hint)
        self.assertIn("python3.14-dev", hint)

    def test_install_hint_for_fedora_like_systems(self):
        hint = install_hint({"ID": "fedora", "ID_LIKE": ""})

        self.assertIn("dnf install", hint)
        self.assertIn("python3.14-devel", hint)
