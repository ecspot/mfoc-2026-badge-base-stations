"""Pure protocol and game logic for Station 6 Pico ultrasonic distance code."""

STATION_ADDRESS = 0xFB40
UNLOCK_COMMAND = 0x07
HOLD_MS = 750

ZONE_NEAR = "near"
ZONE_MIDDLE = "middle"
ZONE_FAR = "far"
ZONES = (ZONE_NEAR, ZONE_MIDDLE, ZONE_FAR)

EVENT_STEP_COMPLETE = "step_complete"
EVENT_GAME_COMPLETE = "game_complete"


def encode_nec_frame(address, command):
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)


def is_badge_trigger_command(command):
    return command == 0x01 or 0x20 <= command <= 0x2F


def classify_distance_cm(distance_cm):
    if 8 <= distance_cm <= 14:
        return ZONE_NEAR
    if 18 <= distance_cm <= 26:
        return ZONE_MIDDLE
    if 32 <= distance_cm <= 45:
        return ZONE_FAR
    return None


def sequence_from_random_values(values):
    sequence = []
    for value in values[:3]:
        zone_index = value % len(ZONES)
        if sequence and ZONES[zone_index] == sequence[-1]:
            zone_index = (zone_index + 1) % len(ZONES)
        sequence.append(ZONES[zone_index])
    if len(sequence) != 3:
        raise ValueError("three random values are required")
    return tuple(sequence)


class DistanceGame:
    def __init__(self, sequence, ticks_diff_fn=None):
        if len(sequence) != 3 or any(zone not in ZONES for zone in sequence):
            raise ValueError("sequence must contain three valid zones")
        self.sequence = tuple(sequence)
        self._ticks_diff = ticks_diff_fn or (lambda left, right: left - right)
        self.step_index = 0
        self._matching_since_ms = None

    @property
    def expected_zone(self):
        return self.sequence[self.step_index]

    def update(self, measured_zone, now_ms):
        if measured_zone != self.expected_zone:
            self._matching_since_ms = None
            return None

        if self._matching_since_ms is None:
            self._matching_since_ms = now_ms
            return None

        if self._ticks_diff(now_ms, self._matching_since_ms) < HOLD_MS:
            return None

        self.step_index += 1
        self._matching_since_ms = None
        if self.step_index >= len(self.sequence):
            return EVENT_GAME_COMPLETE
        return EVENT_STEP_COMPLETE
