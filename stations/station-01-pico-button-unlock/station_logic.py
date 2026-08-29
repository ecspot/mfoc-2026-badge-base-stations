"""Pure behavior and locked protocol values for Pico Station 1."""

STATION_ADDRESS = 0xFB21
UNLOCK_COMMAND = 0x07


class ButtonPressDetector:
    """Debounce an active-low button and report a confirmed press."""

    def __init__(self, debounce_ms, elapsed_ms=None):
        self._debounce_ms = debounce_ms
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
            if elapsed_ms >= self._debounce_ms:
                self._press_reported = False
            return False
        if self._press_reported or elapsed_ms < self._debounce_ms:
            return False

        self._press_reported = True
        return True
