import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import (
    BUTTON_DEBOUNCE_MS,
    CODES_REQUIRED,
    EVENT_CODE_CORRECT,
    EVENT_CODE_WRONG,
    EVENT_GAME_COMPLETE,
    GAME_TIMEOUT_MS,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    WAKE_LED_SEQUENCE,
    SafecrackerGame,
    ButtonPressDetector,
    code_from_random_values,
    encode_nec_frame,
    game_timed_out,
    is_badge_trigger_command,
    next_digit,
    previous_digit,
    segments_for_digit,
    step_delta_for_digit_change,
)


class SafecrackerProtocolTests(unittest.TestCase):
    def test_station_five_identity_and_frame_are_locked(self):
        self.assertEqual(STATION_ADDRESS, 0xFB25)
        self.assertEqual(UNLOCK_COMMAND, 0x07)
        self.assertEqual(encode_nec_frame(STATION_ADDRESS, UNLOCK_COMMAND), 0xF807FB25)

    def test_wake_sequence_is_red_green_red_green_both_both(self):
        self.assertEqual(
            WAKE_LED_SEQUENCE,
            (
                (True, False),
                (False, True),
                (True, False),
                (False, True),
                (True, True),
                (True, True),
            ),
        )

    def test_code_generation_uses_three_to_five_digits(self):
        self.assertEqual(code_from_random_values([0, 1, 2, 3, 4, 5]), (1, 2, 3))
        self.assertEqual(code_from_random_values([1, 9, 8, 7, 6, 5]), (9, 8, 7, 6))
        self.assertEqual(code_from_random_values([2, 0, 11, 22, 33, 44]), (0, 1, 2, 3, 4))

    def test_digit_controls_wrap(self):
        self.assertEqual(next_digit(9), 0)
        self.assertEqual(next_digit(4), 5)
        self.assertEqual(previous_digit(0), 9)
        self.assertEqual(previous_digit(4), 3)

    def test_ten_digit_steps_make_nominal_half_step_revolution(self):
        forward_steps = sum(
            step_delta_for_digit_change(digit, 1) for digit in range(10)
        )
        backward_steps = sum(
            step_delta_for_digit_change(digit, -1) for digit in range(10)
        )
        self.assertEqual(forward_steps, 4096)
        self.assertEqual(backward_steps, -4096)

    def test_badge_commands_arm_the_game(self):
        self.assertTrue(is_badge_trigger_command(0x01))
        self.assertTrue(is_badge_trigger_command(0x20))
        self.assertTrue(is_badge_trigger_command(0x2F))
        self.assertFalse(is_badge_trigger_command(0x00))
        self.assertFalse(is_badge_trigger_command(0x30))

    def test_timeout_blocks_input_at_exact_deadline(self):
        self.assertEqual(GAME_TIMEOUT_MS, 120000)
        self.assertFalse(game_timed_out(119999, 0))
        self.assertTrue(game_timed_out(120000, 0))
        self.assertTrue(game_timed_out(120001, 0))

    def test_common_cathode_display_patterns(self):
        self.assertEqual(segments_for_digit(0), (1, 1, 1, 1, 1, 1, 0))
        self.assertEqual(segments_for_digit(8), (1, 1, 1, 1, 1, 1, 1))
        self.assertEqual(segments_for_digit(9), (1, 1, 1, 1, 0, 1, 1))


class ButtonTests(unittest.TestCase):
    def test_press_reports_once_and_release_rearms(self):
        detector = ButtonPressDetector()
        self.assertFalse(detector.update(True, 100))
        self.assertTrue(detector.update(True, 100 + BUTTON_DEBOUNCE_MS))
        self.assertFalse(detector.update(True, 500))
        self.assertFalse(detector.update(False, 600))
        self.assertFalse(detector.update(False, 600 + BUTTON_DEBOUNCE_MS))
        self.assertFalse(detector.update(True, 700))
        self.assertTrue(detector.update(True, 700 + BUTTON_DEBOUNCE_MS))


class SafecrackerGameTests(unittest.TestCase):
    def test_wrong_code_preserves_prior_correct_progress(self):
        game = SafecrackerGame()
        game.begin_code((1, 2, 3))
        self.assertIsNone(game.select_digit(1))
        self.assertIsNone(game.select_digit(2))
        self.assertEqual(game.select_digit(3), EVENT_CODE_CORRECT)
        self.assertEqual(game.correct_codes, 1)

        game.begin_code((4, 5, 6))
        game.select_digit(4)
        game.select_digit(5)
        self.assertEqual(game.select_digit(7), EVENT_CODE_WRONG)
        self.assertEqual(game.correct_codes, 1)

    def test_three_correct_codes_complete_game(self):
        game = SafecrackerGame()
        self.assertEqual(CODES_REQUIRED, 3)

        for code in ((1, 2, 3), (4, 5, 6, 7), (8, 9, 0, 1, 2)):
            game.begin_code(code)
            result = None
            for digit in code:
                result = game.select_digit(digit)

        self.assertEqual(result, EVENT_GAME_COMPLETE)
        self.assertEqual(game.correct_codes, 3)

    def test_select_waits_for_full_code_length(self):
        game = SafecrackerGame()
        game.begin_code((3, 1, 4, 1, 5))
        for digit in (3, 1, 4, 1):
            self.assertIsNone(game.select_digit(digit))
        self.assertEqual(game.select_digit(5), EVENT_CODE_CORRECT)


if __name__ == "__main__":
    unittest.main()
