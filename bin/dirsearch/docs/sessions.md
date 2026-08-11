# Sessions

dirsearch supports saving and resuming scan sessions, allowing you to pause a long-running scan and continue it later.

## Session Format

Sessions are stored in JSON format using a directory-based structure for human readability and inspection. Legacy `.pickle` and `.pkl` session files are no longer supported.

```text
session_name/
├── meta.json        # Version, timestamps, output history
├── controller.json  # Scan state (URLs, directories, progress)
├── dictionary.json  # Wordlist state and position
└── options.json     # Command-line options used
```

## Saving a Session

When you pause a scan with `CTRL+C`, dirsearch prompts you to save the session:

```sh
python3 dirsearch.py -u https://target -e php
# Press CTRL+C during scan
# Select "save" and provide a session name
```

## Resuming a Session

Resume a saved session with `-s` / `--session`:

```sh
python3 dirsearch.py -s sessions/my_session
```

## Listing Available Sessions

View all resumable sessions with `--list-sessions`:

```sh
python3 dirsearch.py --list-sessions
```

The listing includes:

- Session path
- Target URL
- Remaining targets and directories
- Jobs processed
- Error count
- Last modified time

## Custom Sessions Directory

Specify a custom directory to search for sessions:

```sh
python3 dirsearch.py --list-sessions --sessions-dir /path/to/sessions
```

Default session locations:

- Source install: `<dirsearch>/sessions/`
- Bundled binary: `$HOME/.dirsearch/sessions/`

## Output History

Sessions maintain a history of previous scan outputs, allowing you to review results from interrupted scans. Each resume appends to the output history with timestamps.
