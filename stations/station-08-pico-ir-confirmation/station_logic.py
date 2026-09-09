"""Pure command filtering for Station 8."""

TRIGGER_COMMAND = 0x01


def is_confirmation_trigger(command):
    return command == TRIGGER_COMMAND
