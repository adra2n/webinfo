# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

from unittest import TestCase

from lib.core.settings import DUMMY_URL
from lib.utils.crawl import Crawler


class TestCrawl(TestCase):
    def test_text_crawl(self):
        html_doc = f'Link: {DUMMY_URL}foobar'
        self.assertEqual(Crawler.text_crawl(DUMMY_URL, DUMMY_URL, html_doc), {"foobar"})

    def test_html_crawl(self):
        html_doc = f'<a href="{DUMMY_URL}foo">link</a><script src="/bar.js"><img src="/bar.png">'
        self.assertEqual(Crawler.html_crawl(DUMMY_URL, DUMMY_URL, html_doc), {"foo", "bar.js"})

    def test_html_crawl_handles_rtl_override(self):
        html_doc = '<a href="/admin/\u202eexe.txt/">link</a>'

        self.assertEqual(
            Crawler.html_crawl(DUMMY_URL, DUMMY_URL, html_doc),
            {"admin/\u202eexe.txt/"},
        )

    def test_html_crawl_handles_large_zwj_emoji_sequence(self):
        family = "👨‍👩‍👧‍👦" * 500
        html_doc = f'<a href="/admin/{family}/ok">link</a>'

        self.assertEqual(
            Crawler.html_crawl(DUMMY_URL, DUMMY_URL, html_doc),
            {f"admin/{family}/ok"},
        )

    def test_robots_crawl(self):
        robots_txt = """
User-agent: Googlebot
Disallow: /path1

User-agent: *
        Allow: /path2"""
        self.assertEqual(Crawler.robots_crawl(DUMMY_URL, DUMMY_URL, robots_txt), {"path1", "path2"})
