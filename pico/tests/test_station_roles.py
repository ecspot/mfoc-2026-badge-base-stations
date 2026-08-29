import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from station_roles import (
    ROLE_RECEIVE_EVALUATE_UNLOCK,
    ROLE_RECEIVE_ONLY,
    ROLE_TRANSMIT_UNLOCK,
    role_uses_receiver,
    role_uses_transmitter,
    should_transmit_unlock,
    validate_station_role,
)


class StationRoleTests(unittest.TestCase):
    def test_receive_only_uses_receiver_without_transmitter(self):
        self.assertTrue(role_uses_receiver(ROLE_RECEIVE_ONLY))
        self.assertFalse(role_uses_transmitter(ROLE_RECEIVE_ONLY))
        self.assertFalse(should_transmit_unlock(ROLE_RECEIVE_ONLY, True, True))

    def test_receive_evaluate_unlock_responds_only_to_ready_trigger(self):
        self.assertTrue(role_uses_receiver(ROLE_RECEIVE_EVALUATE_UNLOCK))
        self.assertTrue(role_uses_transmitter(ROLE_RECEIVE_EVALUATE_UNLOCK))
        self.assertTrue(
            should_transmit_unlock(ROLE_RECEIVE_EVALUATE_UNLOCK, True, True)
        )
        self.assertFalse(
            should_transmit_unlock(ROLE_RECEIVE_EVALUATE_UNLOCK, False, True)
        )
        self.assertFalse(
            should_transmit_unlock(ROLE_RECEIVE_EVALUATE_UNLOCK, True, False)
        )

    def test_transmit_unlock_uses_transmitter_without_receiver(self):
        self.assertFalse(role_uses_receiver(ROLE_TRANSMIT_UNLOCK))
        self.assertTrue(role_uses_transmitter(ROLE_TRANSMIT_UNLOCK))

    def test_invalid_role_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_station_role("not-a-role")


if __name__ == "__main__":
    unittest.main()
