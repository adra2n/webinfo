from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from lib.core.exceptions import InvalidRawRequest
from lib.parse.rawrequest import parse_raw, parse_raw_content


class TestRawRequestParser(TestCase):
    def _write_raw_request(self, directory: str, raw_request: bytes) -> str:
        request_file = Path(directory, "request.txt")
        request_file.write_bytes(raw_request)
        return str(request_file)

    def test_origin_form_request_target(self):
        with TemporaryDirectory() as directory:
            request_file = self._write_raw_request(
                directory,
                b"GET /admin HTTP/1.1\r\n"
                b"Host: example.com\r\n"
                b"\r\n",
            )

            urls, method, headers, body = parse_raw(request_file)

        self.assertEqual(urls, ["example.com/admin"])
        self.assertEqual(method, "GET")
        self.assertEqual(headers, {"host": "example.com"})
        self.assertEqual(body, b"")

    def test_origin_form_can_use_explicit_scheme(self):
        request = parse_raw_content(
            b"GET /admin?debug=true HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"\r\n",
            scheme="https",
        )

        self.assertEqual(request.url, "https://example.com/admin?debug=true")

    def test_absolute_form_request_target(self):
        request = parse_raw_content(
            b"GET https://example.com:8443/admin?debug=true HTTP/1.1\r\n"
            b"Host: proxy.local\r\n"
            b"\r\n",
        )

        self.assertEqual(request.url, "https://example.com:8443/admin?debug=true")
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.headers, {"host": "proxy.local"})
        self.assertEqual(request.body, b"")

    def test_absolute_form_does_not_require_host_header(self):
        request = parse_raw_content(
            b"GET http://example.com/admin HTTP/1.1\r\n"
            b"\r\n",
        )

        self.assertEqual(request.url, "http://example.com/admin")
        self.assertEqual(request.headers, {})

    def test_body_bytes_are_preserved(self):
        request = parse_raw_content(
            b"POST /submit HTTP/1.1\r\n"
            b"Host: example.com\r\n"
            b"Content-Type: application/octet-stream\r\n"
            b"\r\n"
            b"payload-\xff",
        )

        self.assertEqual(request.body, b"payload-\xff")
        self.assertEqual(
            request.headers,
            {"host": "example.com", "content-type": "application/octet-stream"},
        )

    def test_origin_form_requires_host_header(self):
        with self.assertRaises(InvalidRawRequest):
            parse_raw_content(b"GET /admin HTTP/1.1\r\n\r\n")
