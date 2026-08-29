"""Pure behavior and locked protocol values for Pico Station 1."""

STATION_ADDRESS = 0xFB21
UNLOCK_COMMAND = 0x07

HOLD_SUCCESS = "success"
HOLD_TOO_SHORT = "too_short"
HOLD_TOO_LONG = "too_long"


class ButtonPressDetector:
    """Report one event after a continuous hold and re-arm after release."""

    def __init__(self, hold_ms, release_debounce_ms, elapsed_ms=None):
        self._hold_ms = hold_ms
        self._release_debounce_ms = release_debounce_ms
        self._elapsed_ms = elapsed_ms or (lambda current, previous: current - previous)
        self._candidate_pressed = False
        self._candidate_since_ms = 0
        self._press_reported = False

    def update(self, is_pressed, now_ms):
        if is_pressed != self._candidate_pressed:
            self._candidate_pressed = is_pressed
            self._candidate_since_ms = now_ms
            return False

        elapsed_ms = self._elapsed_ms(now_ms, self._candidate_since_ms)
        if not is_pressed:
            if elapsed_ms >= self._release_debounce_ms:
                self._press_reported = False
            return False
        if self._press_reported or elapsed_ms < self._hold_ms:
            return False

        self._press_reported = True
        return True


class ButtonHoldDetector:
    """Classify a debounced hold when released or when its limit expires."""

    def __init__(
        self,
        minimum_hold_ms,
        maximum_hold_ms,
        press_debounce_ms,
        release_debounce_ms,
        elapsed_ms=None,
    ):
        self._minimum_hold_ms = minimum_hold_ms
        self._maximum_hold_ms = maximum_hold_ms
        self._press_debounce_ms = press_debounce_ms
        self._release_debounce_ms = release_debounce_ms
        self._elapsed_ms = elapsed_ms or (lambda current, previous: current - previous)
        self._candidate_pressed = False
        self._candidate_since_ms = 0
        self._stable_pressed = False
        self._pressed_since_ms = None
        self._timed_out = False

    def update(self, is_pressed, now_ms):
        if is_pressed != self._candidate_pressed:
            self._candidate_pressed = is_pressed
            self._candidate_since_ms = now_ms

        debounce_ms = (
            self._press_debounce_ms
            if self._candidate_pressed
            else self._release_debounce_ms
        )
        if (
            self._candidate_pressed != self._stable_pressed
            and self._elapsed_ms(now_ms, self._candidate_since_ms) >= debounce_ms
        ):
            self._stable_pressed = self._candidate_pressed
            if self._stable_pressed:
                self._pressed_since_ms = self._candidate_since_ms
                self._timed_out = False
            else:
                held_ms = self._elapsed_ms(
                    self._candidate_since_ms,
                    self._pressed_since_ms,
                )
                self._pressed_since_ms = None
                if self._timed_out:
                    self._timed_out = False
                    return None
                if held_ms >= self._minimum_hold_ms:
                    return HOLD_SUCCESS, held_ms
                return HOLD_TOO_SHORT, held_ms

        if self._stable_pressed and not self._timed_out:
            held_ms = self._elapsed_ms(now_ms, self._pressed_since_ms)
            if held_ms >= self._maximum_hold_ms:
                self._timed_out = True
                return HOLD_TOO_LONG, held_ms

        return None
