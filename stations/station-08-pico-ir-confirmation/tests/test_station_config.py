import ast
import os
import unittest

STATION_DIR = os.path.dirname(os.path.dirname(__file__))
MAIN_PATH = os.path.join(STATION_DIR, "main.py")


def read_constants():
    with open(MAIN_PATH, "r", encoding="utf-8") as source_file:
        tree = ast.parse(source_file.read(), filename=MAIN_PATH)
    constants = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
            constants[target.id] = node.value.value
    return constants


class StationConfigurationTests(unittest.TestCase):
    def test_locked_pin_assignments(self):
        constants = read_constants()
        self.assertEqual(constants["IR_RECEIVER_PIN"], 16)
        self.assertEqual(constants["GREEN_LED_PIN"], 15)

    def test_confirmation_duration_is_two_seconds(self):
        self.assertEqual(read_constants()["CONFIRMATION_MS"], 2000)


if __name__ == "__main__":
    unittest.main()
