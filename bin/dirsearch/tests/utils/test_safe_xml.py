from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from xml.etree import ElementTree

from lib.utils import safe_xml
from lib.utils.safe_xml import UnsafeXML


class TestSafeXML(TestCase):
    def test_fromstring_parses_valid_xml_string(self):
        root = safe_xml.fromstring('<root><child name="foo">bar</child></root>')

        self.assertEqual(root.tag, "root")
        self.assertEqual(root.find("child").get("name"), "foo")
        self.assertEqual(root.findtext("child"), "bar")

    def test_fromstring_parses_valid_xml_bytes(self):
        root = safe_xml.fromstring(b'<?xml version="1.0"?><root><child /></root>')

        self.assertEqual(root.tag, "root")
        self.assertEqual(root.find("child").tag, "child")

    def test_parse_file_parses_valid_xml(self):
        with TemporaryDirectory() as directory:
            xml_file = Path(directory, "report.xml")
            xml_file.write_text("<root><item>ok</item></root>", encoding="utf-8")

            tree = safe_xml.parse_file(xml_file)

        self.assertEqual(tree.getroot().findtext("item"), "ok")

    def test_invalid_xml_still_raises_parse_error(self):
        with self.assertRaises(ElementTree.ParseError):
            safe_xml.fromstring("<root>")

    def test_rejects_doctype_declarations(self):
        with self.assertRaises(UnsafeXML):
            safe_xml.fromstring('<?xml version="1.0"?><!DOCTYPE root><root />')

    def test_rejects_entity_declarations(self):
        with self.assertRaises(UnsafeXML):
            safe_xml.fromstring(
                '<?xml version="1.0"?><!ENTITY xxe SYSTEM "file:///etc/passwd"><root />'
            )

    def test_rejects_case_insensitive_unsafe_markup(self):
        with self.assertRaises(UnsafeXML):
            safe_xml.fromstring('<?xml version="1.0"?><!doctype root><root />')

    def test_rejects_utf16_unsafe_markup(self):
        payload = '<?xml version="1.0"?><!DOCTYPE root><root />'.encode("utf-16")

        with self.assertRaises(UnsafeXML):
            safe_xml.fromstring(payload)

    def test_rejects_utf32_unsafe_markup(self):
        payload = '<?xml version="1.0"?><!DOCTYPE root><root />'.encode("utf-32")

        with self.assertRaises(UnsafeXML):
            safe_xml.fromstring(payload)

    def test_parse_file_rejects_unsafe_xml(self):
        with TemporaryDirectory() as directory:
            xml_file = Path(directory, "report.xml")
            xml_file.write_text(
                '<?xml version="1.0"?><!DOCTYPE root><root />',
                encoding="utf-8",
            )

            with self.assertRaises(UnsafeXML):
                safe_xml.parse_file(xml_file)
