import pathlib
import sys
import unittest

STATION_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STATION_DIR))

import station_logic
import nec_codec


class StationOneProtocolTests(unittest.TestCase):
    def test_protocol_is_locked_to_station_one_unlock(self):
        self.assertEqual(station_logic.STATION_ADDRESS, 0xFB21)
        self.assertEqual(station_logic.UNLOCK_COMMAND, 0x07)

    def test_nec_frame_contains_station_one_unlock(self):
        self.assertEqual(
            nec_codec.encode_nec_frame(
                station_logic.STATION_ADDRESS,
                station_logic.UNLOCK_COMMAND,
            ),
            0xF807FB21,
        )


class ButtonPressDetectorTests(unittest.TestCase):
    def test_press_activates_after_debounce(self):
        detector = station_logic.ButtonPressDetector(debounce_ms=30)

        self.assertFalse(detector.update(False, 0))
        self.assertFalse(detector.update(True, 10))
        self.assertFalse(detector.update(True, 39))
        self.assertTrue(detector.update(True, 40))

    def test_held_button_does_not_repeat(self):
        detector = station_logic.ButtonPressDetector(debounce_ms=30)

        detector.update(True, 0)
        self.assertTrue(detector.update(True, 30))
        self.assertFalse(detector.update(True, 31))
        self.assertFalse(detector.update(True, 5000))

    def test_release_rearms_the_next_press(self):
        detector = station_logic.ButtonPressDetector(debounce_ms=30)

        detector.update(True, 0)
        self.assertTrue(detector.update(True, 30))
        self.assertFalse(detector.update(False, 40))
        self.assertFalse(detector.update(False, 70))
        self.assertFalse(detector.update(True, 80))
        self.assertTrue(detector.update(True, 110))


if __name__ == "__main__":
    unittest.main()
