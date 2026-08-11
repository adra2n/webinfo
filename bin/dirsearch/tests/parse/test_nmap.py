from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.parse.nmap import parse_nmap
from lib.utils.safe_xml import UnsafeXML


class TestNmapParser(TestCase):
    def test_parse_nmap(self):
        self.assertEqual(parse_nmap("./tests/static/nmap.xml"), ["scanme.nmap.org:80"], "Nmap parser gives unexpected result")

    def test_parse_nmap_rejects_dtd(self):
        with TemporaryDirectory() as directory:
            report = Path(directory, "nmap.xml")
            report.write_text(
                '<?xml version="1.0"?><!DOCTYPE nmaprun [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><nmaprun />',
                encoding="utf-8",
            )

            with self.assertRaises(UnsafeXML):
                parse_nmap(str(report))
