"""Pure station-role decisions shared by the Pico application and tests."""

ROLE_RECEIVE_ONLY = "receive_only"
ROLE_RECEIVE_EVALUATE_UNLOCK = "receive_evaluate_unlock"
ROLE_TRANSMIT_UNLOCK = "transmit_unlock"

VALID_STATION_ROLES = (
    ROLE_RECEIVE_ONLY,
    ROLE_RECEIVE_EVALUATE_UNLOCK,
    ROLE_TRANSMIT_UNLOCK,
)


def validate_station_role(role):
    if role not in VALID_STATION_ROLES:
        raise ValueError("STATION_ROLE must be receive_only, receive_evaluate_unlock, or transmit_unlock")
    return role


def role_uses_receiver(role):
    validate_station_role(role)
    return role in (ROLE_RECEIVE_ONLY, ROLE_RECEIVE_EVALUATE_UNLOCK)


def role_uses_transmitter(role):
    validate_station_role(role)
    return role in (ROLE_RECEIVE_EVALUATE_UNLOCK, ROLE_TRANSMIT_UNLOCK)


def should_transmit_unlock(role, is_badge_trigger, cooldown_ready):
    validate_station_role(role)
    return (
        role == ROLE_RECEIVE_EVALUATE_UNLOCK
        and is_badge_trigger
        and cooldown_ready
    )
