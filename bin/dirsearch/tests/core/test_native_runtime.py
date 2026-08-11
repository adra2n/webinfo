from unittest import TestCase
from unittest.mock import patch

from lib.core.native_runtime import (
    get_native_backend_install_error,
    get_native_python_version_error,
    get_native_runtime_error,
)


class TestNativeRuntime(TestCase):
    def test_native_rejects_python_before_314(self):
        error = get_native_python_version_error((3, 12, 3))

        self.assertIn("requires Python 3.14 or newer", error)
        self.assertIn("current: Python 3.12.3", error)
        self.assertIn("dirsearch-build-native", error)

    def test_python_backends_do_not_require_native_module(self):
        self.assertIsNone(
            get_native_runtime_error(
                request_backend="python",
                wordlist_backend="auto",
                version_info=(3, 12, 3),
            )
        )

    def test_native_reports_missing_engine_on_supported_python(self):
        with patch("lib.core.native_runtime.is_native_backend_available", return_value=False):
            error = get_native_runtime_error(
                request_backend="native",
                wordlist_backend="native",
                version_info=(3, 14, 0),
            )

        self.assertIn("Native Rust backend is not installed", error)
        self.assertIn("dirsearch-build-native", error)

    def test_native_accepts_installed_engine_on_supported_python(self):
        with patch("lib.core.native_runtime.is_native_backend_available", return_value=True):
            self.assertIsNone(
                get_native_runtime_error(
                    request_backend="native",
                    wordlist_backend="native",
                    version_info=(3, 14, 0),
                )
            )

    def test_install_error_uses_python_version_error_first(self):
        error = get_native_backend_install_error((3, 13, 9))

        self.assertIn("requires Python 3.14 or newer", error)
        self.assertNotIn("not installed", error)
