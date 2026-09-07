"""Pure protocol and interaction logic for Pico Station 3."""

STATION_ADDRESS = 0xFB24
UNLOCK_COMMAND = 0x07
MIN_WAIT_MS = 2000
MAX_WAIT_MS = 5000
REACTION_WINDOW_MS = 750
ROUNDS_REQUIRED = 3
TOTAL_SUCCESS_MS = 730
GAME_TIMEOUT_MS = 30000
BUTTON_DEBOUNCE_MS = 20

STATE_IDLE = "idle"
STATE_WAITING = "waiting"
STATE_GO = "go"
STATE_NEEDS_RESTART = "needs_restart"

EVENT_GO = "go"
EVENT_FALSE_START = "false_start"
EVENT_MISSED = "missed"
EVENT_ROUND_COMPLETE = "round_complete"
EVENT_SERIES_FAILED = "series_failed"
EVENT_SUCCESS = "success"
EVENT_TIMEOUT = "timeout"


def is_badge_trigger_command(command):
    return command == 0x01 or 0x20 <= command <= 0x2F


def wait_from_random_bits(random_bits):
    span = MAX_WAIT_MS - MIN_WAIT_MS + 1
    return MIN_WAIT_MS + (random_bits % span)


class ButtonPressDetector:
    """Debounce a button state and report once per stable press."""

    def __init__(self, ticks_diff_fn=None):
        self._ticks_diff = ticks_diff_fn or (lambda left, right: left - right)
        self._candidate_pressed = False
        self._candidate_since_ms = 0
        self._press_reported = False

    @property
    def is_pressed(self):
        return self._candidate_pressed

    @property
    def is_released_and_armed(self):
        return not self._candidate_pressed and not self._press_reported

    def update(self, is_pressed, now_ms):
        if is_pressed != self._candidate_pressed:
            self._candidate_pressed = is_pressed
            self._candidate_since_ms = now_ms
            return False

        stable_ms = self._ticks_diff(now_ms, self._candidate_since_ms)
        if stable_ms < BUTTON_DEBOUNCE_MS:
            return False

        if not is_pressed:
            self._press_reported = False
            return False

        if self._press_reported:
            return False

        self._press_reported = True
        return True


class ReactionGame:
    """Hardware-independent reaction-game state machine."""

    def __init__(self, ticks_diff_fn=None, ticks_add_fn=None):
        self._ticks_diff = ticks_diff_fn or (lambda left, right: left - right)
        self._ticks_add = ticks_add_fn or (lambda value, delta: value + delta)
        self.state = STATE_IDLE
        self._signal_at_ms = 0
        self._game_deadline_ms = 0
        self.last_reaction_ms = None
        self.last_total_ms = None
        self.reaction_times = []

    @staticmethod
    def _validate_wait(wait_ms):
        if not MIN_WAIT_MS <= wait_ms <= MAX_WAIT_MS:
            raise ValueError("wait_ms must be between 2000 and 5000")

    def arm(self, now_ms, wait_ms):
        self._validate_wait(wait_ms)
        self._game_deadline_ms = self._ticks_add(now_ms, GAME_TIMEOUT_MS)
        self.last_total_ms = None
        self.reaction_times = []
        self._start_attempt(now_ms, wait_ms)

    def _start_attempt(self, now_ms, wait_ms):
        self._validate_wait(wait_ms)
        self._signal_at_ms = self._ticks_add(now_ms, wait_ms)
        self.last_reaction_ms = None
        self.state = STATE_WAITING

    def restart_attempt(self, now_ms, wait_ms):
        if self.state != STATE_NEEDS_RESTART:
            raise RuntimeError("reaction attempt is not waiting for restart")
        self._game_deadline_ms = self._ticks_add(now_ms, GAME_TIMEOUT_MS)
        self._start_attempt(now_ms, wait_ms)

    def update(self, now_ms, button_pressed):
        if self.state == STATE_IDLE:
            return None

        if self._ticks_diff(now_ms, self._game_deadline_ms) >= 0:
            self.state = STATE_IDLE
            return EVENT_TIMEOUT

        if self.state == STATE_WAITING:
            if self._ticks_diff(now_ms, self._signal_at_ms) < 0:
                if button_pressed:
                    self.state = STATE_NEEDS_RESTART
                    return EVENT_FALSE_START
                return None

            self.state = STATE_GO
            if not button_pressed:
                return EVENT_GO

        if self.state == STATE_GO:
            elapsed_ms = self._ticks_diff(now_ms, self._signal_at_ms)
            if elapsed_ms > REACTION_WINDOW_MS:
                self.reaction_times = []
                self.state = STATE_NEEDS_RESTART
                return EVENT_MISSED
            if button_pressed:
                self.last_reaction_ms = elapsed_ms
                self.reaction_times.append(elapsed_ms)
                if len(self.reaction_times) < ROUNDS_REQUIRED:
                    self.state = STATE_NEEDS_RESTART
                    return EVENT_ROUND_COMPLETE

                self.last_total_ms = sum(self.reaction_times)
                if self.last_total_ms < TOTAL_SUCCESS_MS:
                    self.state = STATE_IDLE
                    return EVENT_SUCCESS

                self.reaction_times = []
                self.state = STATE_NEEDS_RESTART
                return EVENT_SERIES_FAILED

        return None


def encode_nec_frame(address, command):
    """Return a 32-bit extended-NEC frame in least-significant-bit order."""
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)
