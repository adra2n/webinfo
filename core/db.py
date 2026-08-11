from typing import Optional
import sqlite3
import os
from config import config
from utils.output import log

SCHEMA = """
CREATE TABLE IF NOT EXISTS scan (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    domain    TEXT NOT NULL UNIQUE,
    status    TEXT DEFAULT 'running',
    cache_dir TEXT,
    created   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subdomain (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER REFERENCES scan(id),
    name      TEXT,
    domain    TEXT,
    ip        TEXT,
    cidr      TEXT,
    asn       TEXT,
    desc      TEXT,
    tag       TEXT,
    source    TEXT
);

CREATE TABLE IF NOT EXISTS asset (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER REFERENCES scan(id),
    type      TEXT,
    value     TEXT
);

CREATE TABLE IF NOT EXISTS port (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER REFERENCES scan(id),
    ip        TEXT,
    host      TEXT,
    port      INTEGER,
    protocol  TEXT DEFAULT 'tcp',
    state     TEXT,
    service   TEXT,
    product   TEXT,
    version   TEXT,
    title     TEXT,
    source    TEXT
);

CREATE TABLE IF NOT EXISTS path (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id         INTEGER REFERENCES scan(id),
    url             TEXT,
    status          INTEGER,
    content_length  INTEGER,
    title           TEXT
);

CREATE TABLE IF NOT EXISTS vuln (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER REFERENCES scan(id),
    host      TEXT,
    port      INTEGER,
    service   TEXT,
    level     TEXT,
    vuln      TEXT,
    detail    TEXT
);

CREATE TABLE IF NOT EXISTS finding (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER REFERENCES scan(id),
    category  TEXT,
    severity  TEXT,
    title     TEXT,
    detail    TEXT,
    evidence  TEXT,
    host      TEXT,
    port      INTEGER,
    path      TEXT
);

CREATE INDEX IF NOT EXISTS idx_port_scan ON port(scan_id);
CREATE INDEX IF NOT EXISTS idx_port_host ON port(host);
CREATE INDEX IF NOT EXISTS idx_vuln_scan ON vuln(scan_id);
CREATE INDEX IF NOT EXISTS idx_vuln_level ON vuln(level);
CREATE INDEX IF NOT EXISTS idx_subdomain_scan ON subdomain(scan_id);
CREATE INDEX IF NOT EXISTS idx_path_scan ON path(scan_id);
CREATE INDEX IF NOT EXISTS idx_finding_scan ON finding(scan_id);
CREATE INDEX IF NOT EXISTS idx_asset_scan ON asset(scan_id);
"""


class ScanDB:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or config.DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self):
        """数据库迁移"""
        # 检查 port 表是否有 ip 列
        cursor = self.conn.execute("PRAGMA table_info(port)")
        columns = [row[1] for row in cursor.fetchall()]
        if "ip" not in columns:
            self.conn.execute("ALTER TABLE port ADD COLUMN ip TEXT")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_port_ip ON port(ip)")

    def create_scan(self, domain: str) -> int:
        """创建扫描任务，返回 scan_id"""
        cache_dir = os.path.join(config.CACHE_DIR, domain)
        os.makedirs(cache_dir, exist_ok=True)
        self.conn.execute(
            "INSERT OR IGNORE INTO scan (domain, cache_dir) VALUES (?, ?)",
            (domain, cache_dir),
        )
        self.conn.commit()
        row = self.conn.execute("SELECT id FROM scan WHERE domain=?", (domain,)).fetchone()
        return row["id"]

    def get_scan(self, domain: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM scan WHERE domain=?", (domain,)).fetchone()
        return dict(row) if row else None

    def get_scan_by_id(self, scan_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM scan WHERE id=?", (scan_id,)).fetchone()
        return dict(row) if row else None

    def update_scan_status(self, scan_id: int, status: str):
        self.conn.execute(
            "UPDATE scan SET status=?, updated=CURRENT_TIMESTAMP WHERE id=?",
            (status, scan_id),
        )
        self.conn.commit()

    def add_subdomain(self, scan_id: int, **kwargs):
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        self.conn.execute(
            f"INSERT INTO subdomain (scan_id, {cols}) VALUES (?, {placeholders})",
            (scan_id, *kwargs.values()),
        )
        self.conn.commit()

    def add_asset(self, scan_id: int, asset_type: str, value: str):
        self.conn.execute(
            "INSERT INTO asset (scan_id, type, value) VALUES (?, ?, ?)",
            (scan_id, asset_type, value),
        )
        self.conn.commit()

    def add_port(self, scan_id: int, **kwargs):
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        self.conn.execute(
            f"INSERT INTO port (scan_id, {cols}) VALUES (?, {placeholders})",
            (scan_id, *kwargs.values()),
        )
        self.conn.commit()

    def add_path(self, scan_id: int, **kwargs):
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        self.conn.execute(
            f"INSERT INTO path (scan_id, {cols}) VALUES (?, {placeholders})",
            (scan_id, *kwargs.values()),
        )
        self.conn.commit()

    def add_vuln(self, scan_id: int, **kwargs):
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        self.conn.execute(
            f"INSERT INTO vuln (scan_id, {cols}) VALUES (?, {placeholders})",
            (scan_id, *kwargs.values()),
        )
        self.conn.commit()

    def add_finding(self, scan_id: int, **kwargs):
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        self.conn.execute(
            f"INSERT INTO finding (scan_id, {cols}) VALUES (?, {placeholders})",
            (scan_id, *kwargs.values()),
        )
        self.conn.commit()

    def add_ports_batch(self, scan_id: int, rows: list[dict]):
        if not rows:
            return
        cols = ", ".join(rows[0].keys())
        placeholders = ", ".join(["?"] * len(rows[0]))
        self.conn.executemany(
            f"INSERT INTO port (scan_id, {cols}) VALUES (?, {placeholders})",
            [(scan_id, *r.values()) for r in rows],
        )
        self.conn.commit()

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        return [dict(row) for row in self.conn.execute(sql, params).fetchall()]

    def query_one(self, sql: str, params: tuple = ()) -> dict | None:
        row = self.conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
