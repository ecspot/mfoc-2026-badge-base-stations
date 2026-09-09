import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import TRIGGER_COMMAND, is_confirmation_trigger


class StationLogicTests(unittest.TestCase):
    def test_badge_advertisement_triggers_confirmation(self):
        self.assertEqual(TRIGGER_COMMAND, 0x01)
        self.assertTrue(is_confirmation_trigger(0x01))

    def test_station_unlock_does_not_trigger_confirmation(self):
        self.assertFalse(is_confirmation_trigger(0x07))

    def test_report_and_unrelated_commands_do_not_trigger(self):
        self.assertFalse(is_confirmation_trigger(0x20))
        self.assertFalse(is_confirmation_trigger(0x2F))
        self.assertFalse(is_confirmation_trigger(0x00))


if __name__ == "__main__":
    unittest.main()
