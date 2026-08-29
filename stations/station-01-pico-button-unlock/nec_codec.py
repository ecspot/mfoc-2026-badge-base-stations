"""Extended-NEC frame encoding for the standalone Station 1 transmitter."""


def encode_nec_frame(address, command):
    """Return a 32-bit extended-NEC frame in least-significant-bit order."""
    if not 0 <= address <= 0xFFFF:
        raise ValueError("address must be in the range 0x0000..0xFFFF")
    if not 0 <= command <= 0xFF:
        raise ValueError("command must be in the range 0x00..0xFF")
    return address | (command << 16) | ((command ^ 0xFF) << 24)
