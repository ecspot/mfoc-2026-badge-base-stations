"""Pure protocol and game logic for the Pico Simon variant."""

STATION_ADDRESS = 0xFB30
UNLOCK_COMMAND = 0x07
ROUND_LENGTHS = (3, 4, 5, 6)
COLOR_COUNT = 4
BUTTON_DEBOUNCE_MS = 30
GAME_TIMEOUT_MS = 60000

EVENT_ROUND_COMPLETE = "round_complete"
EVENT_WRONG = "wrong"
EVENT_GAME_COMPLETE = "game_complete"


class ButtonPressDetector:
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


def encode_nec_frame(address, command):
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)


def is_badge_trigger_command(command):
    return command == 0x01 or 0x20 <= command <= 0x2F


def game_timed_out(now_ms, started_ms, ticks_diff_fn=None):
    elapsed_ms = ticks_diff_fn or (lambda current, previous: current - previous)
    return elapsed_ms(now_ms, started_ms) >= GAME_TIMEOUT_MS


def sequence_from_random_values(values):
    if len(values) < ROUND_LENGTHS[-1]:
        raise ValueError("six random values are required")
    return tuple(value % COLOR_COUNT for value in values[: ROUND_LENGTHS[-1]])


class SimonGame:
    def __init__(self, sequence):
        if len(sequence) != ROUND_LENGTHS[-1]:
            raise ValueError("Simon sequence must contain six colors")
        if any(color < 0 or color >= COLOR_COUNT for color in sequence):
            raise ValueError("colors must be in the range 0..3")
        self.sequence = tuple(sequence)
        self.round_index = 0
        self.input_index = 0

    @property
    def round_length(self):
        return ROUND_LENGTHS[self.round_index]

    def press(self, color):
        if color != self.sequence[self.input_index]:
            return EVENT_WRONG

        self.input_index += 1
        if self.input_index < self.round_length:
            return None

        self.input_index = 0
        if self.round_index + 1 >= len(ROUND_LENGTHS):
            return EVENT_GAME_COMPLETE

        self.round_index += 1
        return EVENT_ROUND_COMPLETE
