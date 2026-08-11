# -*- coding: utf-8 -*-

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from lib.core.data import options
from lib.view.terminal import CLI, safe_display_text


class TestTerminalOutput(TestCase):
    def setUp(self):
        self.original_options = dict(options)
        options["color"] = True
        options["verbose"] = False

    def tearDown(self):
        options.clear()
        options.update(self.original_options)

    def test_safe_display_text_strips_controls_and_truncates(self):
        value = "admin/\u202eexe.txt/" + ("👨‍👩‍👧‍👦" * 500)
        rendered = safe_display_text(value)

        self.assertNotIn("\u202e", rendered)
        self.assertNotIn("\u200d", rendered)
        self.assertLessEqual(len(rendered), 240)

    def test_status_report_sanitizes_path_and_redirect(self):
        family = "👨‍👩‍👧‍👦" * 500
        response = SimpleNamespace(
            datetime="2026-05-29 12:00:00",
            status=200,
            size="1B",
            full_path=f"admin/\u202eexe.txt/{family}",
            url=f"http://example.com/admin/\u202eexe.txt/{family}",
            redirect=f"/next/\u202eexe.txt/{family}",
            history=[f"http://example.com/old/\u202eexe.txt/{family}"],
            elapsed=0,
            type="text/plain",
        )
        cli = CLI()

        with patch.object(cli, "new_line") as new_line:
            cli.status_report(response, False)

        message = new_line.call_args.args[0]
        self.assertNotIn("\u202e", message)
        self.assertNotIn("\u200d", message)
        self.assertLess(len(message), 900)
