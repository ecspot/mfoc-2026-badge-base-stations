"""Pure protocol and game logic for the Pico stepper safecracker."""

STATION_ADDRESS = 0xFB30
UNLOCK_COMMAND = 0x07
CODES_REQUIRED = 3
BUTTON_DEBOUNCE_MS = 30
GAME_TIMEOUT_MS = 120000

DISPLAY_PATTERNS = (
    (1, 1, 1, 1, 1, 1, 0),
    (0, 1, 1, 0, 0, 0, 0),
    (1, 1, 0, 1, 1, 0, 1),
    (1, 1, 1, 1, 0, 0, 1),
    (0, 1, 1, 0, 0, 1, 1),
    (1, 0, 1, 1, 0, 1, 1),
    (1, 0, 1, 1, 1, 1, 1),
    (1, 1, 1, 0, 0, 0, 0),
    (1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 0, 1, 1),
)

STEPPER_DIGIT_BOUNDARIES = (
    0, 410, 819, 1229, 1638, 2048, 2458, 2867, 3277, 3686, 4096
)

EVENT_CODE_CORRECT = "code_correct"
EVENT_CODE_WRONG = "code_wrong"
EVENT_GAME_COMPLETE = "game_complete"


def is_badge_trigger_command(command):
    return command == 0x01 or 0x20 <= command <= 0x2F


def game_timed_out(now_ms, started_ms, ticks_diff_fn=None):
    elapsed_ms = ticks_diff_fn or (lambda current, previous: current - previous)
    return elapsed_ms(now_ms, started_ms) >= GAME_TIMEOUT_MS


def segments_for_digit(digit):
    if not 0 <= digit <= 9:
        raise ValueError("digit must be in the range 0..9")
    return DISPLAY_PATTERNS[digit]


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


def code_from_random_values(values):
    length = 3 + (values[0] % 3)
    return tuple(values[index + 1] % 10 for index in range(length))


def next_digit(digit):
    return (digit + 1) % 10


def previous_digit(digit):
    return (digit - 1) % 10


def step_delta_for_digit_change(current_digit, direction):
    if direction == 1:
        return (
            STEPPER_DIGIT_BOUNDARIES[current_digit + 1]
            - STEPPER_DIGIT_BOUNDARIES[current_digit]
        )
    if direction == -1:
        boundary_index = 10 if current_digit == 0 else current_digit
        return -(
            STEPPER_DIGIT_BOUNDARIES[boundary_index]
            - STEPPER_DIGIT_BOUNDARIES[boundary_index - 1]
        )
    raise ValueError("direction must be -1 or 1")


class SafecrackerGame:
    def __init__(self):
        self.correct_codes = 0
        self._code = None
        self._entry = []

    def reset(self):
        self.correct_codes = 0
        self._code = None
        self._entry = []

    def begin_code(self, code):
        if not 3 <= len(code) <= 5:
            raise ValueError("code must contain 3 to 5 digits")
        if any(digit < 0 or digit > 9 for digit in code):
            raise ValueError("code digits must be in the range 0..9")
        self._code = tuple(code)
        self._entry = []

    def select_digit(self, digit):
        if self._code is None:
            raise RuntimeError("no active code")
        if not 0 <= digit <= 9:
            raise ValueError("digit must be in the range 0..9")

        self._entry.append(digit)
        if len(self._entry) < len(self._code):
            return None

        is_correct = tuple(self._entry) == self._code
        self._code = None
        self._entry = []
        if not is_correct:
            return EVENT_CODE_WRONG

        self.correct_codes += 1
        if self.correct_codes >= CODES_REQUIRED:
            return EVENT_GAME_COMPLETE
        return EVENT_CODE_CORRECT
