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


class ButtonHoldDetectorTests(unittest.TestCase):
    def make_detector(self):
        return station_logic.ButtonHoldDetector(
            minimum_hold_ms=3000,
            maximum_hold_ms=4000,
            press_debounce_ms=30,
            release_debounce_ms=30,
        )

    def hold_and_release(self, held_ms):
        detector = self.make_detector()
        self.assertIsNone(detector.update(True, 0))
        self.assertIsNone(detector.update(True, 30))
        self.assertIsNone(detector.update(False, held_ms))
        return detector.update(False, held_ms + 30)

    def test_release_before_three_seconds_fails(self):
        self.assertEqual(
            self.hold_and_release(2999),
            (station_logic.HOLD_TOO_SHORT, 2999),
        )

    def test_release_at_three_seconds_succeeds(self):
        self.assertEqual(
            self.hold_and_release(3000),
            (station_logic.HOLD_SUCCESS, 3000),
        )

    def test_release_just_before_four_seconds_succeeds(self):
        self.assertEqual(
            self.hold_and_release(3999),
            (station_logic.HOLD_SUCCESS, 3999),
        )

    def test_four_second_hold_fails_immediately_and_only_once(self):
        detector = self.make_detector()
        detector.update(True, 0)
        detector.update(True, 30)

        self.assertEqual(
            detector.update(True, 4000),
            (station_logic.HOLD_TOO_LONG, 4000),
        )
        self.assertIsNone(detector.update(True, 5000))
        self.assertIsNone(detector.update(False, 5001))
        self.assertIsNone(detector.update(False, 5031))

    def test_release_after_timeout_rearms_next_attempt(self):
        detector = self.make_detector()
        detector.update(True, 0)
        detector.update(True, 30)
        detector.update(True, 4000)
        detector.update(False, 4100)
        detector.update(False, 4130)
        detector.update(True, 4200)
        detector.update(True, 4230)
        detector.update(False, 7200)

        self.assertEqual(
            detector.update(False, 7230),
            (station_logic.HOLD_SUCCESS, 3000),
        )


if __name__ == "__main__":
    unittest.main()
