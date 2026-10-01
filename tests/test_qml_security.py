import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class TestUntrustedCalendarText(unittest.TestCase):
    def assert_plain_text_binding(self, source, binding):
        start = source.index(binding)
        block = source[start:start + 500]
        self.assertIn(
            "textFormat: Text.PlainText",
            block,
            f"{binding} must be rendered as plain text",
        )

    def test_event_titles_and_locations_cannot_trigger_rich_text_fetches(self):
        source = (ROOT / "Panel.qml").read_text()
        for binding in (
            "text: root.upcomingEvent ? root.upcomingEvent.title",
            "text: eventRow.modelData.title",
            "return eventRow.modelData.location",
        ):
            with self.subTest(binding=binding):
                self.assert_plain_text_binding(source, binding)

    def test_remote_calendar_names_are_plain_text(self):
        source = (ROOT / "SettingsView.qml").read_text()
        self.assert_plain_text_binding(source, "text: toggle.label")


if __name__ == "__main__":
    unittest.main()
