#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


STACKS = {
    "threaded": {
        "async": "False",
        "request-backend": "python",
        "wordlist-backend": "auto",
    },
    "async": {
        "async": "True",
        "request-backend": "python",
        "wordlist-backend": "auto",
    },
    "native-rust": {
        "async": "False",
        "request-backend": "native",
        "wordlist-backend": "native",
    },
}


def replace_setting(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^({re.escape(key)}\s*=\s*).*$", re.MULTILINE)
    replaced, count = pattern.subn(rf"\g<1>{value}", text)
    if count != 1:
        raise ValueError(f"Expected exactly one '{key}' setting, found {count}")
    return replaced


def configure(config_path: Path, stack: str) -> None:
    settings = STACKS[stack]
    text = config_path.read_text(encoding="utf-8")
    for key, value in settings.items():
        text = replace_setting(text, key, value)
    config_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure dirsearch release stack defaults")
    parser.add_argument("config", type=Path, help="Path to config.ini")
    parser.add_argument("stack", choices=sorted(STACKS), help="Release stack to configure")
    args = parser.parse_args()

    configure(args.config, args.stack)


if __name__ == "__main__":
    main()
