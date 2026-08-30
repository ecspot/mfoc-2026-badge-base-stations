"""NEC decoder for the self-contained Pico Simon game."""


def _between(value, minimum, maximum):
    return minimum <= value <= maximum


def decode_nec_edges(levels, durations, count):
    leader_index = -1
    for index in range(max(0, count - 65)):
        if (levels[index] == 0 and levels[index + 1] == 1
                and _between(durations[index], 8000, 10000)
                and _between(durations[index + 1], 3500, 5500)):
            leader_index = index
            break
    if leader_index < 0 or leader_index + 66 > count:
        return None
    value = 0
    offset = leader_index + 2
    for bit_index in range(32):
        low_index = offset + bit_index * 2
        high_index = low_index + 1
        if levels[low_index] != 0 or levels[high_index] != 1:
            return None
        if not _between(durations[low_index], 350, 800):
            return None
        high_time = durations[high_index]
        if _between(high_time, 350, 900):
            bit_value = 0
        elif _between(high_time, 1200, 2100):
            bit_value = 1
        else:
            return None
        value |= bit_value << bit_index
    address = value & 0xFFFF
    command = (value >> 16) & 0xFF
    if (command ^ ((value >> 24) & 0xFF)) != 0xFF:
        return None
    return address, command
