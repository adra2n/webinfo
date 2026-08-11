#!/usr/bin/env python3
"""Split db/dicc.txt into categorized wordlists."""

from __future__ import annotations

import argparse
import os
import re
from collections import OrderedDict


CATEGORY_ORDER = [
    "extensions",
    "conf",
    "vcs",
    "backups",
    "db",
    "logs",
    "keys",
    "web",
    "common",
]

CONF_EXTENSIONS = (
    ".ini",
    ".cfg",
    ".conf",
    ".config",
    ".cnf",
    ".toml",
    ".properties",
    ".prop",
    ".xml",
    ".yml",
    ".yaml",
    ".json",
)

BACKUP_SUFFIXES = (
    ".bak",
    ".old",
    ".swp",
    ".swo",
    ".swpx",
    ".backup",
    ".orig",
    ".original",
    "~",
)

DB_EXTENSIONS = (
    ".sql",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".mdb",
    ".accdb",
)

KEY_EXTENSIONS = (".pem", ".key")
KEY_FILENAMES = {"id_rsa", "id_rsa.pub", "id_dsa", "id_dsa.pub"}

WEB_EXTENSIONS = (
    ".php",
    ".html",
    ".htm",
    ".asp",
    ".aspx",
    ".jsp",
    ".jspx",
)

VCS_REGEX = re.compile(r"(^|/)\.(git|svn|hg)", re.IGNORECASE)


def is_extension_tag(line: str) -> bool:
    return "%ext%" in line.lower()


def is_conf(line: str) -> bool:
    lower = line.lower()
    base = os.path.basename(lower)

    if base.startswith(".env"):
        return True

    if base.startswith("config") or base.startswith("configuration"):
        return True

    if any(lower.endswith(ext) for ext in CONF_EXTENSIONS):
        return True

    if "/config" in lower or "/configuration" in lower:
        return True

    return False


def is_vcs(line: str) -> bool:
    cleaned = line.lstrip("!")
    return bool(VCS_REGEX.search(cleaned))


def is_backup(line: str) -> bool:
    return any(line.lower().endswith(suffix) for suffix in BACKUP_SUFFIXES)


def is_db(line: str) -> bool:
    return any(line.lower().endswith(ext) for ext in DB_EXTENSIONS)


def is_log(line: str) -> bool:
    return line.lower().endswith(".log")


def is_key(line: str) -> bool:
    lower = line.lower()
    base = os.path.basename(lower)
    return base in KEY_FILENAMES or any(lower.endswith(ext) for ext in KEY_EXTENSIONS)


def is_web(line: str) -> bool:
    return any(line.lower().endswith(ext) for ext in WEB_EXTENSIONS)


CATEGORY_RULES = OrderedDict(
    (
        ("extensions", is_extension_tag),
        ("conf", is_conf),
        ("vcs", is_vcs),
        ("backups", is_backup),
        ("db", is_db),
        ("logs", is_log),
        ("keys", is_key),
        ("web", is_web),
    )
)


def split_wordlists(source_path: str, dest_dir: str) -> dict[str, list[str]]:
    buckets = {name: [] for name in CATEGORY_ORDER}

    with open(source_path, "r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue

            matched = False
            for category, predicate in CATEGORY_RULES.items():
                if predicate(line):
                    buckets[category].append(line)
                    matched = True
                    break
            if not matched:
                buckets["common"].append(line)

    os.makedirs(dest_dir, exist_ok=True)
    for category in CATEGORY_ORDER:
        out_path = os.path.join(dest_dir, f"{category}.txt")
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(buckets[category]))
            handle.write("\n")

    return buckets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split db/dicc.txt into categorized wordlists"
    )
    parser.add_argument(
        "--source",
        default=os.path.join("db", "dicc.txt"),
        help="Source wordlist (default: db/dicc.txt)",
    )
    parser.add_argument(
        "--dest",
        default=os.path.join("db", "categories"),
        help="Destination directory for category files (default: db/categories)",
    )
    args = parser.parse_args()

    buckets = split_wordlists(args.source, args.dest)
    total = sum(len(entries) for entries in buckets.values())
    print(f"Wrote {total} entries into {args.dest}")
    for category in CATEGORY_ORDER:
        print(f"- {category}: {len(buckets[category])}")


if __name__ == "__main__":
    main()
