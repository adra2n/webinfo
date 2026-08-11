from pathlib import Path
from unittest import TestCase


class TestNativeInstallPackaging(TestCase):
    def test_entrypoints_include_native_builder(self):
        self.assertIn(
            'dirsearch-build-native = "dirsearch.lib.core.native_builder:main"',
            Path("pyproject.toml").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "dirsearch-build-native=dirsearch.lib.core.native_builder:main",
            Path("setup.py").read_text(encoding="utf-8"),
        )

    def test_package_data_includes_native_sources(self):
        setup_py = Path("setup.py").read_text(encoding="utf-8")

        self.assertIn('*package_files(ROOT / "native")', setup_py)
        self.assertIn('"target"', setup_py)

    def test_setup_uses_standard_package_dir_mapping(self):
        setup_py = Path("setup.py").read_text(encoding="utf-8")

        self.assertIn('"dirsearch": "."', setup_py)
        self.assertIn('"dirsearch.lib": "lib"', setup_py)
        self.assertNotIn("tempfile.mkdtemp", setup_py)
        self.assertNotIn("shutil.copytree", setup_py)
        self.assertNotIn("os.chdir", setup_py)

    def test_ntlm_auth_is_not_a_direct_dependency(self):
        requirement_files = (
            Path("requirements.txt"),
            Path("requirements/runtime.txt"),
        )

        for path in requirement_files:
            with self.subTest(path=str(path)):
                self.assertNotIn(
                    "ntlm-auth",
                    path.read_text(encoding="utf-8"),
                )
        self.assertNotIn(
            "ntlm_auth",
            Path("pyinstaller/dirsearch.spec").read_text(encoding="utf-8"),
        )

    def test_install_docs_use_native_builder_flow(self):
        docs = Path("docs/installation.md").read_text(encoding="utf-8")

        self.assertIn("dirsearch-build-native", docs)
        self.assertIn("python3.14-dev", docs)
        self.assertIn("python3.14-devel", docs)
        self.assertNotIn("maturin develop", docs)
