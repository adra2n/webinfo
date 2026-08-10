import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import ScanDB


class TestScanDB(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = ScanDB(self.db_path)

    def tearDown(self):
        self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_scan(self):
        scan_id = self.db.create_scan("example.com")
        self.assertEqual(scan_id, 1)
        scan = self.db.get_scan("example.com")
        self.assertIsNotNone(scan)
        self.assertEqual(scan["domain"], "example.com")

    def test_create_scan_duplicate(self):
        self.db.create_scan("example.com")
        self.db.create_scan("example.com")
        scan = self.db.get_scan("example.com")
        self.assertIsNotNone(scan)

    def test_add_subdomain(self):
        scan_id = self.db.create_scan("example.com")
        self.db.add_subdomain(scan_id, name="test.example.com", domain="example.com", ip="1.2.3.4")
        rows = self.db.query("SELECT * FROM subdomain WHERE scan_id=?", (scan_id,))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "test.example.com")

    def test_add_port(self):
        scan_id = self.db.create_scan("example.com")
        self.db.add_port(scan_id, host="1.2.3.4", port=80, service="http", product="nginx")
        rows = self.db.query("SELECT * FROM port WHERE scan_id=?", (scan_id,))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["host"], "1.2.3.4")

    def test_add_vuln(self):
        scan_id = self.db.create_scan("example.com")
        self.db.add_vuln(scan_id, host="1.2.3.4", port=6379, service="redis", level="High", vuln="Redis 未授权")
        rows = self.db.query("SELECT * FROM vuln WHERE scan_id=?", (scan_id,))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["level"], "High")

    def test_add_finding(self):
        scan_id = self.db.create_scan("example.com")
        self.db.add_finding(scan_id, category="header", severity="Medium", title="CSP 缺失", host="1.2.3.4")
        rows = self.db.query("SELECT * FROM finding WHERE scan_id=?", (scan_id,))
        self.assertEqual(len(rows), 1)

    def test_update_scan_status(self):
        scan_id = self.db.create_scan("example.com")
        self.db.update_scan_status(scan_id, "done:dm")
        scan = self.db.get_scan("example.com")
        self.assertEqual(scan["status"], "done:dm")

    def test_add_ports_batch(self):
        scan_id = self.db.create_scan("example.com")
        ports = [
            {"host": "1.2.3.4", "port": 80, "service": "http", "product": "nginx", "version": "", "title": "", "source": "nmap"},
            {"host": "1.2.3.4", "port": 443, "service": "https", "product": "nginx", "version": "", "title": "", "source": "nmap"},
        ]
        self.db.add_ports_batch(scan_id, ports)
        rows = self.db.query("SELECT * FROM port WHERE scan_id=?", (scan_id,))
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
