# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase, TestCase

from lib.connection.response import AsyncResponse, Response


class DummyResponse:
    status_code = 200
    history = []

    def __init__(self, headers=None, body=b"body", encoding="utf-8"):
        self.headers = headers or {}
        self._body = body
        self.encoding = encoding

    def iter_content(self, chunk_size):
        del chunk_size
        yield self._body


class DummyAsyncResponse:
    status_code = 200
    history = []

    def __init__(self, headers=None, body=b"body", encoding="utf-8"):
        self.headers = headers or {}
        self._body = body
        self.encoding = encoding

    async def aiter_bytes(self, chunk_size):
        del chunk_size
        yield self._body


class TestResponse(TestCase):
    def test_length_falls_back_to_body_for_invalid_content_length(self):
        response = Response(
            "http://example.com/admin",
            DummyResponse(headers={"content-length": "not-a-number"}, body=b"abc"),
        )

        self.assertEqual(response.length, 3)

    def test_length_falls_back_to_body_for_negative_content_length(self):
        response = Response(
            "http://example.com/admin",
            DummyResponse(headers={"content-length": "-10"}, body=b"abcd"),
        )

        self.assertEqual(response.length, 4)

    def test_length_keeps_valid_content_length(self):
        response = Response(
            "http://example.com/admin",
            DummyResponse(headers={"content-length": "10"}, body=b"abcd"),
        )

        self.assertEqual(response.length, 10)

    def test_cjk_length_uses_network_bytes(self):
        body = "测试".encode()
        response = Response(
            "http://example.com/admin/%E6%B5%8B%E8%AF%95",
            DummyResponse(headers={"content-length": str(len(body))}, body=body),
        )

        self.assertEqual(response.content, "测试")
        self.assertEqual(len(response.content), 2)
        self.assertEqual(response.length, 6)

    def test_case_expansion_length_uses_network_bytes(self):
        body = "/TEST-STRASSE".encode()
        response = Response(
            "http://example.com/test-stra%C3%9Fe",
            DummyResponse(headers={"content-length": str(len(body))}, body=body),
        )

        self.assertEqual(response.content, "/TEST-STRASSE")
        self.assertEqual(response.length, len(body))

    def test_invalid_utf8_uses_replacement_decoding(self):
        response = Response(
            "http://example.com/admin",
            DummyResponse(
                headers={"content-type": "text/html; charset=utf-8"},
                body=b"start\x96end",
                encoding="utf-8",
            ),
        )

        self.assertEqual(response.body, b"start\x96end")
        self.assertEqual(response.content, "start�end")
        self.assertEqual(response.length, len(response.body))

    def test_utf16_bom_artifact_body_does_not_raise_decode_error(self):
        response = Response(
            "http://example.com/%FF%FEadmin",
            DummyResponse(body=b"\xff\xfeadmin", encoding="utf-8"),
        )

        self.assertEqual(response.body, b"\xff\xfeadmin")
        self.assertEqual(response.content, "��admin")
        self.assertEqual(response.length, len(response.body))


class TestAsyncResponse(IsolatedAsyncioTestCase):
    async def test_cjk_length_uses_network_bytes(self):
        body = "测试".encode()
        response = await AsyncResponse.create(
            "http://example.com/admin/%E6%B5%8B%E8%AF%95",
            DummyAsyncResponse(headers={"content-length": str(len(body))}, body=body),
        )

        self.assertEqual(response.content, "测试")
        self.assertEqual(len(response.content), 2)
        self.assertEqual(response.length, 6)

    async def test_case_expansion_length_uses_network_bytes(self):
        body = "/TEST-STRASSE".encode()
        response = await AsyncResponse.create(
            "http://example.com/test-stra%C3%9Fe",
            DummyAsyncResponse(headers={"content-length": str(len(body))}, body=body),
        )

        self.assertEqual(response.content, "/TEST-STRASSE")
        self.assertEqual(response.length, len(body))

    async def test_invalid_utf8_uses_replacement_decoding(self):
        response = await AsyncResponse.create(
            "http://example.com/admin",
            DummyAsyncResponse(
                headers={"content-type": "text/html; charset=utf-8"},
                body=b"start\x96end",
                encoding="utf-8",
            ),
        )

        self.assertEqual(response.body, b"start\x96end")
        self.assertEqual(response.content, "start�end")
        self.assertEqual(response.length, len(response.body))

    async def test_utf16_bom_artifact_body_does_not_raise_decode_error(self):
        response = await AsyncResponse.create(
            "http://example.com/%FF%FEadmin",
            DummyAsyncResponse(body=b"\xff\xfeadmin", encoding="utf-8"),
        )

        self.assertEqual(response.body, b"\xff\xfeadmin")
        self.assertEqual(response.content, "��admin")
        self.assertEqual(response.length, len(response.body))
