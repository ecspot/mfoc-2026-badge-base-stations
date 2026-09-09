import os
import sys
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
if STATION_DIR not in sys.path:
    sys.path.insert(0, STATION_DIR)

from nec_codec import decode_nec_edges


def make_edges(address, command):
    levels = [0, 1]
    durations = [9000, 4500]
    value = address | (command << 16) | ((command ^ 0xFF) << 24)
    for bit_index in range(32):
        levels.extend((0, 1))
        durations.extend((560, 1690 if value & (1 << bit_index) else 560))
    return levels, durations


class NecCodecTests(unittest.TestCase):
    def test_decodes_any_valid_complete_nec_frame(self):
        levels, durations = make_edges(0xFB24, 0x2A)
        self.assertEqual(
            decode_nec_edges(levels, durations, len(levels)),
            (0xFB24, 0x2A),
        )

    def test_finds_frame_after_idle_edge(self):
        levels, durations = make_edges(0x1234, 0x56)
        levels.insert(0, 1)
        durations.insert(0, 15000)
        self.assertEqual(
            decode_nec_edges(levels, durations, len(levels)),
            (0x1234, 0x56),
        )

    def test_rejects_bad_command_complement(self):
        levels, durations = make_edges(0xFB24, 0x2A)
        durations[-1] = 560 if durations[-1] == 1690 else 1690
        self.assertIsNone(decode_nec_edges(levels, durations, len(levels)))

    def test_rejects_incomplete_frame(self):
        levels, durations = make_edges(0xFB24, 0x2A)
        self.assertIsNone(decode_nec_edges(levels[:-2], durations[:-2], len(levels) - 2))


if __name__ == "__main__":
    unittest.main()
