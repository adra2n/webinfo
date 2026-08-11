# PyInstaller Build Configuration

This directory contains the PyInstaller spec and local build script for standalone dirsearch executables.

## Release Targets

| Platform | Architecture | Artifact suffix |
|----------|--------------|-----------------|
| Windows | x64 | `windows-x64` |
| Linux | x64 | `linux-x64` |
| Linux | ARM64 | `linux-arm64` |
| macOS | Intel x86_64 | `macos-intel` |
| macOS | Apple Silicon ARM64 | `macos-silicon` |

Each target is built as:

- `async`
- `threaded`
- `native-rust`

## Local Build

```bash
./pyinstaller/build.sh async
./pyinstaller/build.sh threaded
./pyinstaller/build.sh native-rust
./pyinstaller/build.sh all
```

The script installs runtime and optional DB dependencies from wheels. The `native-rust` stack also builds the PyO3 extension with maturin.

## Output

Binaries are created in `pyinstaller/dist/`:

```text
dirsearch-v0.5.0-rc1-linux-x64-async
dirsearch-v0.5.0-rc1-linux-arm64-native-rust
dirsearch-v0.5.0-rc1-windows-x64-threaded.exe
dirsearch-v0.5.0-rc1-macos-intel-async
dirsearch-v0.5.0-rc1-macos-silicon-native-rust
```

Some antivirus engines flag PyInstaller bootloaders heuristically. For users affected by that, publish and recommend the portable folder archives built by `.github/workflows/portable-builds.yml`.

## Troubleshooting

### Missing Modules

Add hidden imports to `pyinstaller/dirsearch.spec`.

### Native Rust Variant

Install Rust and maturin before building:

```bash
rustup default stable
python3.14 -m pip install --only-binary=:all: maturin
python3.14 scripts/build_native.py --out dist/native-wheels
```

### macOS Code Signing

For distribution, sign binaries with:

```bash
codesign --sign "Developer ID" pyinstaller/dist/dirsearch-v0.5.0-rc1-macos-*
```
