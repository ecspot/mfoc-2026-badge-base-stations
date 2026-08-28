"""Shared protocol constants for the MFOC badge base station."""

UNLOCK_ADDRESS_BASE = 0xFB20
UNLOCK_COMMAND = 0x07
MIN_STATION_NUMBER = 1
MAX_STATION_NUMBER = 5


def make_unlock_address(station_number):
    """Return the intended one-hot unlock address for station 1 through 5."""
    if not MIN_STATION_NUMBER <= station_number <= MAX_STATION_NUMBER:
        raise ValueError("station_number must be in the range 1..5")
    return UNLOCK_ADDRESS_BASE | (1 << (station_number - 1))


def is_badge_trigger_command(command):
    """Recognize badge advertisement and unlocked-count report frames."""
    return command == 0x01 or 0x20 <= command <= 0x2F
