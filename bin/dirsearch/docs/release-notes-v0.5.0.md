# dirsearch v0.5.0-rc1

This prerelease includes all user-facing changes since the last published release, `v0.4.3`.

## Runtime and scanning

- Python support now targets Python 3.11-3.14, with release builds prepared on Python 3.14.
- Async scanning is available as the default runtime on supported Python versions; the legacy threaded stack remains available with `--sync`.
- A Rust native backend is available for supported GET scans and native wordlist generation through `--request-backend native` and `--wordlist-backend native`.
- Advanced match/filter controls are available for status, size, word count, line count, regex, and elapsed time.
- Wildcard and duplicate-result filtering were improved, including redirect-aware duplicate detection and stealth calibration words.
- New scan controls include maximum runtime per target, non-default network interfaces, Nmap XML target import, and `--disable-cli`.
- Async pause/stop handling, SSL error classification, proxy handling, streamed response timing, IPv6 handling, and encoded URL edge cases were fixed or improved.

## Wordlists and discovery data

- Category-based wordlists are available with `--wordlist-categories`, including PHP, Python, Java, .NET, Node, ColdFusion, and infrastructure categories.
- Template wordlists now support placeholders such as `%SUBJECT%`, `%CRUD_OP%`, `%AUTH_OP%`, `%DATE%`, `%API_VERSION%`, `%CATEGORY:name%`, and `%EXT%`.
- `--wordlist-status`, `--wordlist-max-size`, and selectable wordlist backends (`auto`, `python`, `native`) were added.
- Bundled discovery data was expanded with new framework paths, WordPress and WooCommerce entries, API/Ollama/OpenAI endpoints, traversal-oriented entries, and updated blacklists.

## Output, reports, and API

- Multiple output formats can be written from one run.
- Report paths and SQL table names can use variables.
- MySQL and PostgreSQL reports were added, and DB drivers are now optional extras: `dirsearch[mysql]`, `dirsearch[postgresql]`, and `dirsearch[db]`.
- `--verbose` can show response elapsed time and content type.
- A Python API was added with `FuzzerConfig`, `DirsearchFuzzer`, structured results, wordlist helpers, and template wordlist support.
- `python -m dirsearch` entrypoint support and packaged install metadata were fixed.

## Sessions and resumability

- Resumable sessions now use JSON controller state instead of pickle.
- `--list-sessions` and session resume by ID were added.
- Session paths are safer across platforms, including Windows-safe timestamps.
- Bundled builds store sessions under the user home directory.
- Ctrl+C pause/resume behavior was improved across threaded, async, and PyInstaller Linux builds.

## Security and dependencies

- Runtime requirements are pinned for supply-chain hardening.
- The old dependency installer path was removed.
- Optional DB dependencies are explicit extras instead of mandatory runtime dependencies.
- XML parsing was hardened with safe XML handling and tests.
- Legacy pickle sessions are no longer loaded directly; unsupported pickle sessions now warn.

## Packaging and distribution

- PyInstaller release builds now cover Windows x64, Linux x64, Linux ARM64, macOS Intel, and macOS Apple Silicon.
- Release artifacts are built in three default-stack variants: `async`, `threaded`, and `native-rust`.
- Portable CPython archives are provided with compiled dependencies for users affected by PyInstaller antivirus false positives.
- Linux x64 Docker images are published to GitHub Container Registry for each release stack.
- Nuitka was removed from the release build matrix for this prerelease.
- CI, CodeQL, Semgrep, Docker, PyInstaller, and draft-release workflows were refreshed.

## Documentation

- The README was split into focused pages under `docs/`.
- Installation, usage, configuration, sessions, wordlist, Python API, build, and native-backend benchmark docs were added or refreshed.
- Prompt-injection safety guidance was added for agent workflows.
