# Wordlists

## Summary

- A wordlist is a text file where each line is a path.
- Unlike other tools, dirsearch only replaces the `%EXT%` keyword with extensions from the `-e` flag.
- For wordlists without `%EXT%`, such as [SecLists](https://github.com/danielmiessler/SecLists), use `-f` / `--force-extensions` to append extensions and `/` to every wordlist entry.
- To apply selected extensions to entries that already have extensions, use `--overwrite-extensions`.
- Some extensions are excluded from overwrite behavior, such as `.log`, `.json`, `.xml`, and media extensions like `.jpg` and `.png`.
- Multiple wordlists can be separated with commas, for example `wordlist1.txt,wordlist2.txt`.
- Bundled wordlist categories live in `db/categories/` and can be selected with `--wordlist-categories`.
- Wordlist generation uses `--wordlist-backend=auto` by default. `python` selects the built-in backend and `native` requires a native backend build.
- Template wordlists live in `db/templates/` and support placeholders.
- Use `--wordlist-status` to preview resolved wordlist files and generated entry count before scanning.
- Use `--wordlist-max-size` to cap generation.

## Extensions

Normal extension replacement:

```text
index.%EXT%
```

Passing `asp` and `aspx` as extensions generates:

```text
index
index.asp
index.aspx
```

Force extensions:

```text
admin
```

Passing `php` and `html` as extensions with `-f` / `--force-extensions` generates:

```text
admin
admin.php
admin.html
admin/
```

Overwrite extensions:

```text
login.html
```

Passing `jsp` and `jspa` as extensions with `--overwrite-extensions` generates:

```text
login.html
login.jsp
login.jspa
```

## Categories

Bundled wordlist categories are stored in `db/categories/`.

Available categories:

- `extensions`
- `conf`
- `vcs`
- `backups`
- `db`
- `logs`
- `keys`
- `web`
- `common`

Use `all` to include everything:

```sh
python3 dirsearch.py -u https://target --wordlist-categories all
```

## Templates

Template wordlists live in `db/templates/` and support placeholders such as:

- `%SUBJECT%`
- `%CRUD_OP%`
- `%AUTH_OP%`
- `%ADMIN_OP%`
- `%ENV%`
- `%DATE%`
- `%API_VERSION%`
- `%CATEGORY:name%`
- `%EXT%`

Preview resolved files and generated entry counts without scanning:

```sh
python3 dirsearch.py -u https://target --wordlist-status
```

Limit generated entries:

```sh
python3 dirsearch.py -u https://target --wordlist-max-size 500000
```

## Prefixes and Suffixes

Use `--prefixes` to add custom prefixes to all entries:

```sh
python3 dirsearch.py -e php -u https://target --prefixes .,admin,_
```

Wordlist:

```text
tools
```

Generated with prefixes:

```text
tools
.tools
admintools
_tools
```

Use `--suffixes` to add custom suffixes to all entries:

```sh
python3 dirsearch.py -e php -u https://target --suffixes ~
```

Wordlist:

```text
index.php
internal
```

Generated with suffixes:

```text
index.php
internal
index.php~
internal~
```

## Wordlist Formats

Supported transformations: lowercase, uppercase, and capitalization.

Lowercase:

```text
admin
index.html
```

Uppercase:

```text
ADMIN
INDEX.HTML
```

Capital:

```text
Admin
Index.html
```

## Exclude Extensions

Use `--exclude-extensions` with an extension list to remove all paths in the wordlist that contain the given extensions.

```sh
python3 dirsearch.py -u https://target --exclude-extensions jsp
```

Wordlist:

```text
admin.php
test.jsp
```

After:

```text
admin.php
```
