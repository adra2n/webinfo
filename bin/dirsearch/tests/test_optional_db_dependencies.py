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

from __future__ import annotations

import importlib
import sys
from contextlib import contextmanager
from importlib.abc import MetaPathFinder
from unittest import TestCase


class BlockedDependencyFinder(MetaPathFinder):
    def __init__(self, blocked: set[str]) -> None:
        self.blocked = blocked

    def find_spec(self, fullname, path, target=None):
        if fullname in self.blocked or any(
            fullname.startswith(f"{name}.") for name in self.blocked
        ):
            raise ModuleNotFoundError(f"No module named '{fullname}'")
        return None


@contextmanager
def block_dependencies(*module_names: str):
    blocked = set(module_names)
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name in blocked
        or any(name.startswith(f"{blocked_name}.") for blocked_name in blocked)
    }
    for name in list(saved_modules):
        sys.modules.pop(name, None)

    finder = BlockedDependencyFinder(blocked)
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)
        for name in list(sys.modules):
            if name in blocked or any(
                name.startswith(f"{blocked_name}.") for blocked_name in blocked
            ):
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)


class TestOptionalDBDependencies(TestCase):
    def test_core_imports_without_database_drivers(self):
        with block_dependencies("mysql", "psycopg"):
            importlib.import_module("dirsearch")
            importlib.import_module("lib.controller.session")
            importlib.import_module("lib.report.manager")

    def test_file_reports_import_without_database_drivers(self):
        modules = (
            "lib.report.csv_report",
            "lib.report.html_report",
            "lib.report.json_report",
            "lib.report.markdown_report",
            "lib.report.plain_text_report",
            "lib.report.simple_report",
            "lib.report.sqlite_report",
            "lib.report.xml_report",
        )

        with block_dependencies("mysql", "psycopg"):
            for module in modules:
                importlib.import_module(module)

    def test_mysql_report_fails_only_when_driver_is_used(self):
        from lib.core.exceptions import CannotConnectException

        with block_dependencies("mysql"):
            module = importlib.import_module("lib.report.mysql_report")
            with self.assertRaises(CannotConnectException):
                module.MySQLReport().initiate(
                    "mysql://user:pass@localhost/db", "results"
                )

    def test_postgresql_report_fails_only_when_driver_is_used(self):
        from lib.core.exceptions import CannotConnectException

        with block_dependencies("psycopg"):
            module = importlib.import_module("lib.report.postgresql_report")
            with self.assertRaises(CannotConnectException):
                module.PostgreSQLReport().initiate(
                    "postgresql://user:pass@localhost/db", "results"
                )
