import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from nec_codec import decode_nec_edges, encode_nec_frame


def make_edges(address, command):
    levels = [0, 1]
    durations = [9000, 4500]
    value = address | (command << 16) | ((command ^ 0xFF) << 24)
    for bit in range(32):
        levels.extend((0, 1))
        durations.extend((560, 1690 if value & (1 << bit) else 560))
    return levels, durations


class NecCodecTests(unittest.TestCase):
    def test_encodes_extended_nec_address_and_command(self):
        self.assertEqual(encode_nec_frame(0xFB21, 0x07), 0xF807FB21)

    def test_rejects_out_of_range_encode_values(self):
        with self.assertRaises(ValueError):
            encode_nec_frame(0x10000, 0x07)
        with self.assertRaises(ValueError):
            encode_nec_frame(0xFB21, 0x100)

    def test_decodes_extended_nec_address_and_command(self):
        levels, durations = make_edges(0xFB21, 0x07)
        self.assertEqual(decode_nec_edges(levels, durations, len(levels)), (0xFB21, 0x07))

    def test_rejects_bad_command_complement(self):
        levels, durations = make_edges(0xFB21, 0x07)
        durations[-1] = 560 if durations[-1] == 1690 else 1690
        self.assertIsNone(decode_nec_edges(levels, durations, len(levels)))

    def test_finds_leader_after_idle_edge(self):
        levels, durations = make_edges(0x1234, 0x20)
        levels.insert(0, 1)
        durations.insert(0, 30000)
        self.assertEqual(decode_nec_edges(levels, durations, len(levels)), (0x1234, 0x20))


if __name__ == "__main__":
    unittest.main()
