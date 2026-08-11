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

from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import TestCase

from scripts.configure_stack import configure


CONFIG = """\
[general]
async = False

[dictionary]
wordlist-backend = auto

[request]
request-backend = python
"""


class TestReleaseScripts(TestCase):
    def configure_stack(self, stack):
        with TemporaryDirectory() as directory:
            config = Path(directory) / "config.ini"
            config.write_text(CONFIG, encoding="utf-8")
            configure(config, stack)
            return config.read_text(encoding="utf-8")

    def test_configure_threaded_stack(self):
        text = self.configure_stack("threaded")

        self.assertIn("async = False", text)
        self.assertIn("request-backend = python", text)
        self.assertIn("wordlist-backend = auto", text)

    def test_configure_async_stack(self):
        text = self.configure_stack("async")

        self.assertIn("async = True", text)
        self.assertIn("request-backend = python", text)
        self.assertIn("wordlist-backend = auto", text)

    def test_configure_native_rust_stack(self):
        text = self.configure_stack("native-rust")

        self.assertIn("async = False", text)
        self.assertIn("request-backend = native", text)
        self.assertIn("wordlist-backend = native", text)
