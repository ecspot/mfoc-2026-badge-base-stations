"""Pure protocol and button logic for the Pico IR trigger utility."""

NEC_ADDRESS = 0xFF00
TRIGGER_COMMAND = 0x01
BUTTON_DEBOUNCE_MS = 30


def encode_nec_frame(address, command):
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)


class ButtonPressDetector:
    """Debounce an active-high button and report once per press."""

    def __init__(self, ticks_diff_fn=None):
        self._ticks_diff = ticks_diff_fn or (lambda left, right: left - right)
        self._candidate_pressed = False
        self._candidate_since_ms = 0
        self._press_reported = False

    def update(self, is_pressed, now_ms):
        if is_pressed != self._candidate_pressed:
            self._candidate_pressed = is_pressed
            self._candidate_since_ms = now_ms
            return False

        if self._ticks_diff(now_ms, self._candidate_since_ms) < BUTTON_DEBOUNCE_MS:
            return False

        if not is_pressed:
            self._press_reported = False
            return False

        if self._press_reported:
            return False

        self._press_reported = True
        return True
