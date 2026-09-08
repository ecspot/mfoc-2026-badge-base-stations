import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import (
    BUTTON_DEBOUNCE_MS,
    NEC_ADDRESS,
    TRIGGER_COMMAND,
    ButtonPressDetector,
    encode_nec_frame,
)


class ProtocolTests(unittest.TestCase):
    def test_standard_nec_address_and_trigger_command(self):
        self.assertEqual(NEC_ADDRESS, 0xFF00)
        self.assertEqual(TRIGGER_COMMAND, 0x01)
        self.assertEqual(
            encode_nec_frame(NEC_ADDRESS, TRIGGER_COMMAND),
            0xFE01FF00,
        )


class ButtonTests(unittest.TestCase):
    def test_active_high_press_reports_after_debounce(self):
        detector = ButtonPressDetector()
        self.assertFalse(detector.update(True, 100))
        self.assertFalse(detector.update(True, 100 + BUTTON_DEBOUNCE_MS - 1))
        self.assertTrue(detector.update(True, 100 + BUTTON_DEBOUNCE_MS))

    def test_held_button_sends_only_once(self):
        detector = ButtonPressDetector()
        detector.update(True, 0)
        self.assertTrue(detector.update(True, BUTTON_DEBOUNCE_MS))
        self.assertFalse(detector.update(True, 1000))

    def test_release_rearms_next_press(self):
        detector = ButtonPressDetector()
        detector.update(True, 0)
        detector.update(True, BUTTON_DEBOUNCE_MS)
        detector.update(False, 100)
        detector.update(False, 100 + BUTTON_DEBOUNCE_MS)
        detector.update(True, 200)
        self.assertTrue(detector.update(True, 200 + BUTTON_DEBOUNCE_MS))


if __name__ == "__main__":
    unittest.main()
