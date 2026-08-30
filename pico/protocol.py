"""Shared protocol constants for the MFOC badge base station."""

UNLOCK_COMMAND = 0x07
MIN_STATION_NUMBER = 1
UNLOCK_ADDRESSES = (
    0xFB21,
    0xFB22,
    0xFB24,
    0xFB28,
    0xFB30,
    0xFB40,
    0xFB80,
)
MAX_STATION_NUMBER = len(UNLOCK_ADDRESSES)


def make_unlock_address(station_number):
    """Return the registered one-hot unlock address for station 1 through 7."""
    if not MIN_STATION_NUMBER <= station_number <= MAX_STATION_NUMBER:
        raise ValueError("station_number must be in the range 1..7")
    return UNLOCK_ADDRESSES[station_number - 1]


def is_badge_trigger_command(command):
    """Recognize badge advertisement and unlocked-count report frames."""
    return command == 0x01 or 0x20 <= command <= 0x2F
