"""Allocation-light NEC frame decoder usable by MicroPython and CPython tests."""


def _between(value, minimum, maximum):
    return minimum <= value <= maximum


def encode_nec_frame(address, command):
    """Return a 32-bit extended-NEC frame in least-significant-bit order."""
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)


def decode_nec_edges(levels, durations, count):
    """Decode edge durations into ``(16-bit address, command)`` or ``None``.

    ``levels[i]`` is the signal level that was held for ``durations[i]``
    microseconds before the edge. The function accepts leading idle/noise and
    locates a standard NEC 9 ms low + 4.5 ms high leader.
    """
    required_after_leader = 64
    leader_index = -1

    for index in range(max(0, count - (required_after_leader + 1))):
        if (
            levels[index] == 0
            and levels[index + 1] == 1
            and _between(durations[index], 8000, 10000)
            and _between(durations[index + 1], 3500, 5500)
        ):
            leader_index = index
            break

    if leader_index < 0 or leader_index + 2 + required_after_leader > count:
        return None

    value = 0
    offset = leader_index + 2
    for bit_index in range(32):
        low_index = offset + bit_index * 2
        high_index = low_index + 1
        low_time = durations[low_index]
        high_time = durations[high_index]

        if levels[low_index] != 0 or levels[high_index] != 1:
            return None
        if not _between(low_time, 350, 800):
            return None

        if _between(high_time, 350, 900):
            bit_value = 0
        elif _between(high_time, 1200, 2100):
            bit_value = 1
        else:
            return None

        value |= bit_value << bit_index

    address = value & 0xFFFF
    command = (value >> 16) & 0xFF
    inverted_command = (value >> 24) & 0xFF
    if (command ^ inverted_command) != 0xFF:
        return None

    return address, command
