import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import (
    EVENT_GAME_COMPLETE,
    EVENT_STEP_COMPLETE,
    HOLD_MS,
    MAX_TARGETS,
    MIN_TARGETS,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    DistanceGame,
    ZONE_FAR,
    ZONE_MIDDLE,
    ZONE_NEAR,
    classify_distance_cm,
    encode_nec_frame,
    is_badge_trigger_command,
    sequence_from_random_values,
)


class UltrasonicProtocolTests(unittest.TestCase):
    def test_station_six_identity_is_locked(self):
        self.assertEqual(STATION_ADDRESS, 0xFB40)
        self.assertEqual(UNLOCK_COMMAND, 0x07)
        self.assertEqual(encode_nec_frame(STATION_ADDRESS, UNLOCK_COMMAND), 0xF807FB40)

    def test_distance_zones_have_safety_gaps(self):
        self.assertEqual(classify_distance_cm(8), ZONE_NEAR)
        self.assertEqual(classify_distance_cm(14), ZONE_NEAR)
        self.assertIsNone(classify_distance_cm(15))
        self.assertEqual(classify_distance_cm(18), ZONE_MIDDLE)
        self.assertEqual(classify_distance_cm(26), ZONE_MIDDLE)
        self.assertIsNone(classify_distance_cm(27))
        self.assertEqual(classify_distance_cm(32), ZONE_FAR)
        self.assertEqual(classify_distance_cm(45), ZONE_FAR)
        self.assertIsNone(classify_distance_cm(46))

    def test_random_sequence_length_ranges_from_four_to_seven(self):
        self.assertEqual(MIN_TARGETS, 4)
        self.assertEqual(MAX_TARGETS, 7)
        for selector, expected_length in enumerate(range(MIN_TARGETS, MAX_TARGETS + 1)):
            sequence = sequence_from_random_values(
                (selector, 0, 0, 0, 0, 0, 0, 0)
            )
            self.assertEqual(len(sequence), expected_length)
            for current_zone, next_zone in zip(sequence, sequence[1:]):
                self.assertNotEqual(current_zone, next_zone)

    def test_badge_commands_arm_the_game(self):
        self.assertTrue(is_badge_trigger_command(0x01))
        self.assertTrue(is_badge_trigger_command(0x20))
        self.assertTrue(is_badge_trigger_command(0x2F))
        self.assertFalse(is_badge_trigger_command(0x30))


class DistanceGameTests(unittest.TestCase):
    def test_matching_distance_must_hold_for_750_ms(self):
        game = DistanceGame((ZONE_NEAR, ZONE_MIDDLE, ZONE_FAR, ZONE_NEAR))
        self.assertEqual(HOLD_MS, 750)
        self.assertIsNone(game.update(ZONE_NEAR, 100))
        self.assertIsNone(game.update(ZONE_NEAR, 849))
        self.assertEqual(game.update(ZONE_NEAR, 850), EVENT_STEP_COMPLETE)

    def test_leaving_zone_resets_current_hold(self):
        game = DistanceGame((ZONE_NEAR, ZONE_MIDDLE, ZONE_FAR, ZONE_NEAR))
        game.update(ZONE_NEAR, 0)
        game.update(None, 700)
        self.assertIsNone(game.update(ZONE_NEAR, 701))
        self.assertIsNone(game.update(ZONE_NEAR, 1450))
        self.assertEqual(game.update(ZONE_NEAR, 1451), EVENT_STEP_COMPLETE)

    def test_all_targets_finish_game(self):
        game = DistanceGame((ZONE_NEAR, ZONE_MIDDLE, ZONE_FAR, ZONE_NEAR))
        result = None
        for start, zone in (
            (0, ZONE_NEAR),
            (1000, ZONE_MIDDLE),
            (2000, ZONE_FAR),
            (3000, ZONE_NEAR),
        ):
            game.update(zone, start)
            result = game.update(zone, start + HOLD_MS)
        self.assertEqual(result, EVENT_GAME_COMPLETE)

    def test_game_rejects_target_counts_outside_randomized_range(self):
        with self.assertRaises(ValueError):
            DistanceGame((ZONE_NEAR, ZONE_MIDDLE, ZONE_FAR))
        with self.assertRaises(ValueError):
            DistanceGame((ZONE_NEAR,) * 8)


if __name__ == "__main__":
    unittest.main()
