import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omarchy_calendar_sync import manage_ical


class TestManageIcal(unittest.TestCase):
    def test_add_reads_subscription_url_from_stdin(self):
        secret_url = "https://example.com/private/calendar-token/basic.ics"
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "calendar-sync.json"
            with (
                patch.object(manage_ical.config, "CONFIG_PATH", config_path),
                patch.object(manage_ical, "ensure_runtime") as ensure_runtime,
                patch.object(manage_ical.cli, "main", return_value=0),
                patch.object(manage_ical.sys, "stdin", io.StringIO(secret_url + "\n")),
            ):
                code = manage_ical.main(["--add", "--color", "#4285f4"])

            self.assertEqual(code, 0)
            ensure_runtime.assert_called_once_with(secret_url)
            feed = json.loads(config_path.read_text())["ical"]["feeds"][0]
            self.assertEqual(feed["url"], secret_url)

    def test_add_rejects_missing_stdin_url(self):
        with patch.object(manage_ical.sys, "stdin", io.StringIO("")):
            with self.assertRaisesRegex(ValueError, "standard input"):
                manage_ical.main(["--add"])

    def test_runtime_reentry_keeps_subscription_url_out_of_argv(self):
        secret_url = "https://example.com/private/calendar-token/basic.ics"
        with tempfile.TemporaryDirectory() as tmp:
            venv = Path(tmp) / "venv"
            python = venv / "bin" / "python"
            python.parent.mkdir(parents=True)
            python.touch()
            with (
                patch.object(manage_ical, "_venv_path", return_value=venv),
                patch.object(manage_ical.sys, "argv", [
                    "manage-ical", "--add", "--color", "#4285f4",
                ]),
                patch.object(manage_ical.subprocess, "run") as run,
            ):
                with self.assertRaises(SystemExit):
                    manage_ical.ensure_runtime(secret_url)

            command = run.call_args.args[0]
            self.assertNotIn(secret_url, command)
            self.assertEqual(run.call_args.kwargs["input"], secret_url + "\n")


if __name__ == "__main__":
    unittest.main()
