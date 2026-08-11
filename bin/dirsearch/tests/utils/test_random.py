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

from collections import Counter
import math
import re
from unittest import TestCase

from lib.utils.random import StealthWordGenerator, rand_string


class TestRandom(TestCase):
    def test_rand_string(self):
        test_omit = "abcde"
        self.assertEqual(len(rand_string(9)), 9, "Incorrect random string length")
        for x, y in zip(rand_string(5, omit=test_omit), test_omit):
            self.assertNotEqual(x, y, "Random string's characters are not distinct from omit")

    def test_stealth_words_have_low_entropy(self):
        generator = StealthWordGenerator(seed=1)
        for _ in range(1000):
            self.assertLess(self.shannon_entropy(generator.generate()), 4.0)

    def test_stealth_words_do_not_match_common_directories(self):
        generator = StealthWordGenerator(seed=2)
        common_directories = {"admin", "backup", "api", "test"}

        for _ in range(10000):
            value = generator.generate()
            self.assertNotIn(value, common_directories)
            self.assertTrue(
                common_directories.isdisjoint(re.split("[-_]", value))
            )

    def test_stealth_words_respect_url_format_constraints(self):
        generator = StealthWordGenerator(seed=3)
        word_counts = set()

        for _ in range(1000):
            value = generator.generate()
            word_counts.add(len(re.split("[-_]", value)))
            self.assertRegex(value, r"^[a-z]+([-_][a-z]+){1,2}$")
            self.assertGreaterEqual(len(value), 15)
            self.assertLessEqual(len(value), 30)
            self.assertNotIn("--", value)
            self.assertNotIn("__", value)
            self.assertNotIn("-_", value)
            self.assertNotIn("_-", value)

        self.assertEqual(word_counts, {2, 3})

    def test_stealth_words_are_reproducible_with_seed(self):
        first = StealthWordGenerator(seed=4)
        second = StealthWordGenerator(seed=4)

        self.assertEqual(
            [first.generate() for _ in range(50)],
            [second.generate() for _ in range(50)],
        )

    def test_stealth_words_honor_omit(self):
        generator = StealthWordGenerator(seed=5)
        first = generator.generate()

        self.assertNotEqual(generator.generate(omit=first), first)

    @staticmethod
    def shannon_entropy(value: str) -> float:
        length = len(value)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in Counter(value).values()
        )
