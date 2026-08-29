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
    def make_detector(self):
        return station_logic.ButtonPressDetector(
            hold_ms=3000,
            release_debounce_ms=30,
        )

    def test_press_activates_after_three_second_hold(self):
        detector = self.make_detector()

        self.assertFalse(detector.update(False, 0))
        self.assertFalse(detector.update(True, 10))
        self.assertFalse(detector.update(True, 3009))
        self.assertTrue(detector.update(True, 3010))

    def test_held_button_does_not_repeat(self):
        detector = self.make_detector()

        detector.update(True, 0)
        self.assertTrue(detector.update(True, 3000))
        self.assertFalse(detector.update(True, 3001))
        self.assertFalse(detector.update(True, 10000))

    def test_release_before_three_seconds_cancels_attempt(self):
        detector = self.make_detector()

        detector.update(True, 0)
        self.assertFalse(detector.update(True, 2999))
        self.assertFalse(detector.update(False, 3000))
        self.assertFalse(detector.update(False, 3030))
        self.assertFalse(detector.update(True, 3040))
        self.assertFalse(detector.update(True, 6039))
        self.assertTrue(detector.update(True, 6040))

    def test_release_rearms_the_next_press(self):
        detector = self.make_detector()

        detector.update(True, 0)
        self.assertTrue(detector.update(True, 3000))
        self.assertFalse(detector.update(False, 3010))
        self.assertFalse(detector.update(False, 3040))
        self.assertFalse(detector.update(True, 3050))
        self.assertTrue(detector.update(True, 6050))


if __name__ == "__main__":
    unittest.main()
