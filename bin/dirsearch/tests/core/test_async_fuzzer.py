from unittest import IsolatedAsyncioTestCase

from lib.connection.response import NativeResponse
from lib.core.data import blacklists, options
from lib.core.fuzzer import AsyncFuzzer


class DummyDictionary:
    def __init__(self, paths):
        self.paths = paths
        self.index = 0

    def __next__(self):
        if self.index >= len(self.paths):
            raise StopIteration
        self.index += 1
        return self.paths[self.index - 1]

    def __len__(self):
        return len(self.paths)


class DummyAsyncRequester:
    async def request(self, path):
        if path in ("", "home.html"):
            return NativeResponse(
                f"https://example.com/{path}",
                200,
                [("Content-Type", "text/plain")],
                b"same homepage body",
            )

        return NativeResponse(
            f"https://example.com/{path}",
            404,
            [("Content-Type", "text/plain")],
            b"not found",
        )


class TestAsyncFuzzer(IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_options = dict(options)
        self.original_blacklists = dict(blacklists)
        options.update(
            {
                "thread_count": 1,
                "delay": 0,
                "exclude_response": None,
                "exclude_status_codes": set(),
                "include_status_codes": {200},
                "exclude_sizes": set(),
                "minimum_response_size": 0,
                "maximum_response_size": 0,
                "exclude_texts": [],
                "exclude_regex": None,
                "exclude_redirect": None,
                "filter_threshold": 0,
                "prefixes": (),
                "suffixes": (),
                "extensions": (),
            }
        )
        blacklists.clear()

    def tearDown(self):
        options.clear()
        options.update(self.original_options)
        blacklists.clear()
        blacklists.update(self.original_blacklists)

    async def test_does_not_filter_response_matching_index_page(self):
        dictionary = DummyDictionary(["home.html"])
        matches = []
        misses = []
        errors = []
        fuzzer = AsyncFuzzer(
            DummyAsyncRequester(),
            dictionary,
            match_callbacks=(matches.append,),
            not_found_callbacks=(misses.append,),
            error_callbacks=(errors.append,),
        )

        await fuzzer.start()

        self.assertEqual(dictionary.index, 1)
        self.assertEqual([response.full_path for response in matches], ["home.html"])
        self.assertEqual(misses, [])
        self.assertEqual(errors, [])
