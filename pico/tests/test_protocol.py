import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from protocol import UNLOCK_COMMAND, is_badge_trigger_command, make_unlock_address


class ProtocolTests(unittest.TestCase):
    def test_unlock_addresses_are_one_hot(self):
        self.assertEqual(make_unlock_address(1), 0xFB21)
        self.assertEqual(make_unlock_address(2), 0xFB22)
        self.assertEqual(make_unlock_address(5), 0xFB30)

    def test_badge_trigger_commands(self):
        self.assertTrue(is_badge_trigger_command(0x01))
        self.assertTrue(is_badge_trigger_command(0x20))
        self.assertTrue(is_badge_trigger_command(0x2F))
        self.assertFalse(is_badge_trigger_command(0x07))
        self.assertFalse(is_badge_trigger_command(0x30))

    def test_unlock_command_matches_badge_firmware(self):
        self.assertEqual(UNLOCK_COMMAND, 0x07)


if __name__ == "__main__":
    unittest.main()
