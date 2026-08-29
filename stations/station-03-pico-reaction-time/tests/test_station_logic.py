import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from station_logic import (
    BUTTON_DEBOUNCE_MS,
    ButtonPressDetector,
    EVENT_FALSE_START,
    EVENT_GO,
    EVENT_MISSED,
    EVENT_SUCCESS,
    EVENT_TIMEOUT,
    MAX_WAIT_MS,
    MIN_WAIT_MS,
    REACTION_WINDOW_MS,
    ReactionGame,
    STATE_GO,
    STATE_IDLE,
    STATE_NEEDS_RESTART,
    STATE_WAITING,
    STATION_ADDRESS,
    UNLOCK_COMMAND,
    encode_nec_frame,
    is_badge_trigger_command,
    wait_from_random_bits,
)


class StationThreeProtocolTests(unittest.TestCase):
    def test_protocol_is_locked_to_station_three(self):
        self.assertEqual(STATION_ADDRESS, 0xFB24)
        self.assertEqual(UNLOCK_COMMAND, 0x07)

    def test_nec_frame_contains_station_three_unlock(self):
        self.assertEqual(
            encode_nec_frame(STATION_ADDRESS, UNLOCK_COMMAND),
            0xF807FB24,
        )

    def test_recognizes_only_badge_trigger_commands(self):
        self.assertTrue(is_badge_trigger_command(0x01))
        self.assertTrue(is_badge_trigger_command(0x20))
        self.assertTrue(is_badge_trigger_command(0x2F))
        self.assertFalse(is_badge_trigger_command(0x00))
        self.assertFalse(is_badge_trigger_command(0x30))

    def test_reaction_timing_is_locked(self):
        self.assertEqual(MIN_WAIT_MS, 2000)
        self.assertEqual(MAX_WAIT_MS, 5000)
        self.assertEqual(REACTION_WINDOW_MS, 750)

    def test_random_wait_mapping_stays_inside_locked_range(self):
        self.assertEqual(wait_from_random_bits(0), 2000)
        self.assertEqual(wait_from_random_bits(3000), 5000)
        self.assertEqual(wait_from_random_bits(3001), 2000)


class ReactionGameTests(unittest.TestCase):
    def test_signal_appears_only_after_wait_delay(self):
        game = ReactionGame()
        game.arm(now_ms=1000, wait_ms=2000)

        self.assertEqual(game.state, STATE_WAITING)
        self.assertIsNone(game.update(now_ms=2999, button_pressed=False))
        self.assertEqual(game.update(now_ms=3000, button_pressed=False), EVENT_GO)
        self.assertEqual(game.state, STATE_GO)

    def test_press_at_reaction_deadline_succeeds(self):
        game = ReactionGame()
        game.arm(now_ms=0, wait_ms=2000)
        game.update(now_ms=2000, button_pressed=False)

        self.assertEqual(
            game.update(now_ms=2750, button_pressed=True),
            EVENT_SUCCESS,
        )
        self.assertEqual(game.state, STATE_IDLE)

    def test_press_before_signal_is_false_start(self):
        game = ReactionGame()
        game.arm(now_ms=0, wait_ms=3000)

        self.assertEqual(
            game.update(now_ms=2999, button_pressed=True),
            EVENT_FALSE_START,
        )
        self.assertEqual(game.state, STATE_NEEDS_RESTART)

    def test_expired_reaction_window_requires_restart(self):
        game = ReactionGame()
        game.arm(now_ms=0, wait_ms=2000)
        game.update(now_ms=2000, button_pressed=False)

        self.assertEqual(
            game.update(now_ms=2751, button_pressed=False),
            EVENT_MISSED,
        )
        self.assertEqual(game.state, STATE_NEEDS_RESTART)

    def test_retry_uses_a_new_wait_from_restart_time(self):
        game = ReactionGame()
        game.arm(now_ms=0, wait_ms=2000)
        game.update(now_ms=1000, button_pressed=True)

        game.restart_attempt(now_ms=1500, wait_ms=3000)
        self.assertIsNone(game.update(now_ms=4499, button_pressed=False))
        self.assertEqual(game.update(now_ms=4500, button_pressed=False), EVENT_GO)

    def test_overall_game_times_out_without_transmitting(self):
        game = ReactionGame()
        game.arm(now_ms=100, wait_ms=5000)

        self.assertEqual(
            game.update(now_ms=30100, button_pressed=False),
            EVENT_TIMEOUT,
        )
        self.assertEqual(game.state, STATE_IDLE)


class ButtonPressDetectorTests(unittest.TestCase):
    def test_stable_press_reports_after_debounce(self):
        detector = ButtonPressDetector()

        self.assertFalse(detector.update(is_pressed=True, now_ms=100))
        self.assertFalse(
            detector.update(
                is_pressed=True,
                now_ms=100 + BUTTON_DEBOUNCE_MS - 1,
            )
        )
        self.assertTrue(
            detector.update(
                is_pressed=True,
                now_ms=100 + BUTTON_DEBOUNCE_MS,
            )
        )

    def test_held_button_does_not_repeat(self):
        detector = ButtonPressDetector()
        detector.update(is_pressed=True, now_ms=0)
        self.assertTrue(detector.update(is_pressed=True, now_ms=BUTTON_DEBOUNCE_MS))
        self.assertFalse(detector.update(is_pressed=True, now_ms=1000))

    def test_stable_release_rearms_next_press(self):
        detector = ButtonPressDetector()
        detector.update(is_pressed=True, now_ms=0)
        detector.update(is_pressed=True, now_ms=BUTTON_DEBOUNCE_MS)

        detector.update(is_pressed=False, now_ms=100)
        detector.update(is_pressed=False, now_ms=100 + BUTTON_DEBOUNCE_MS)
        detector.update(is_pressed=True, now_ms=200)
        self.assertTrue(
            detector.update(
                is_pressed=True,
                now_ms=200 + BUTTON_DEBOUNCE_MS,
            )
        )


if __name__ == "__main__":
    unittest.main()
