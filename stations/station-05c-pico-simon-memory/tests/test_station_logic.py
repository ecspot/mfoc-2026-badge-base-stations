import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import (
    BUTTON_DEBOUNCE_MS,
    ButtonPressDetector,
    EVENT_GAME_COMPLETE,
    EVENT_ROUND_COMPLETE,
    EVENT_WRONG,
    GAME_TIMEOUT_MS,
    ROUND_LENGTHS,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    SimonGame,
    encode_nec_frame,
    game_timed_out,
    is_badge_trigger_command,
    sequence_from_random_values,
)


class SimonProtocolTests(unittest.TestCase):
    def test_station_five_variant_identity_is_locked(self):
        self.assertEqual(STATION_ADDRESS, 0xFB30)
        self.assertEqual(UNLOCK_COMMAND, 0x07)
        self.assertEqual(encode_nec_frame(STATION_ADDRESS, UNLOCK_COMMAND), 0xF807FB30)

    def test_four_rounds_grow_from_three_to_six(self):
        self.assertEqual(ROUND_LENGTHS, (3, 4, 5, 6))

    def test_sequence_maps_random_values_to_four_colors(self):
        self.assertEqual(
            sequence_from_random_values((0, 1, 2, 3, 4, 5)),
            (0, 1, 2, 3, 0, 1),
        )

    def test_badge_commands_arm_the_game(self):
        self.assertTrue(is_badge_trigger_command(0x01))
        self.assertTrue(is_badge_trigger_command(0x20))
        self.assertTrue(is_badge_trigger_command(0x2F))
        self.assertFalse(is_badge_trigger_command(0x30))

    def test_button_reports_once_until_released(self):
        detector = ButtonPressDetector()
        self.assertFalse(detector.update(True, 0))
        self.assertTrue(detector.update(True, BUTTON_DEBOUNCE_MS))
        self.assertFalse(detector.update(True, 500))
        detector.update(False, 600)
        detector.update(False, 600 + BUTTON_DEBOUNCE_MS)
        self.assertFalse(detector.update(True, 700))
        self.assertTrue(detector.update(True, 700 + BUTTON_DEBOUNCE_MS))

    def test_timeout_blocks_input_at_exact_deadline(self):
        self.assertEqual(GAME_TIMEOUT_MS, 60000)
        self.assertFalse(game_timed_out(59999, 0))
        self.assertTrue(game_timed_out(60000, 0))
        self.assertTrue(game_timed_out(60001, 0))


class SimonGameTests(unittest.TestCase):
    def test_wrong_color_fails_current_game(self):
        game = SimonGame((0, 1, 2, 3, 0, 1))
        self.assertEqual(game.press(1), EVENT_WRONG)

    def test_round_completes_after_exact_prefix(self):
        game = SimonGame((0, 1, 2, 3, 0, 1))
        self.assertIsNone(game.press(0))
        self.assertIsNone(game.press(1))
        self.assertEqual(game.press(2), EVENT_ROUND_COMPLETE)
        self.assertEqual(game.round_length, 4)

    def test_four_rounds_complete_game(self):
        sequence = (0, 1, 2, 3, 0, 1)
        game = SimonGame(sequence)
        result = None
        for length in ROUND_LENGTHS:
            for color in sequence[:length]:
                result = game.press(color)
        self.assertEqual(result, EVENT_GAME_COMPLETE)


if __name__ == "__main__":
    unittest.main()
