#pragma once

#include <stdint.h>

namespace Station02 {

constexpr uint16_t STATION_ADDRESS = 0xFB22U;
constexpr uint8_t UNLOCK_COMMAND = 0x07U;
constexpr uint8_t SERVO_MIN_DEGREES = 20U;
constexpr uint8_t SERVO_MAX_DEGREES = 160U;
constexpr uint8_t TARGET_ZONE_MIN_DEGREES = 85U;
constexpr uint8_t TARGET_ZONE_MAX_DEGREES = 95U;
constexpr uint16_t BUTTON_DEBOUNCE_MS = 30U;

constexpr uint32_t encodeNecFrame(uint16_t address, uint8_t command) {
    return static_cast<uint32_t>(address) |
        (static_cast<uint32_t>(command) << 16U) |
        (static_cast<uint32_t>(command ^ 0xFFU) << 24U);
}

constexpr bool isBadgeTriggerCommand(uint8_t command) {
    return command == 0x01U || (command >= 0x20U && command <= 0x2FU);
}

constexpr bool isTargetInZone(uint8_t positionDegrees) {
    return positionDegrees >= TARGET_ZONE_MIN_DEGREES &&
        positionDegrees <= TARGET_ZONE_MAX_DEGREES;
}

constexpr int8_t nextSweepDirection(uint8_t positionDegrees, int8_t direction) {
    return positionDegrees >= SERVO_MAX_DEGREES
        ? -1
        : (positionDegrees <= SERVO_MIN_DEGREES ? 1 : direction);
}

constexpr uint8_t nextSweepPosition(uint8_t positionDegrees, int8_t direction) {
    return positionDegrees >= SERVO_MAX_DEGREES
        ? static_cast<uint8_t>(SERVO_MAX_DEGREES - 1U)
        : (positionDegrees <= SERVO_MIN_DEGREES
            ? static_cast<uint8_t>(SERVO_MIN_DEGREES + 1U)
            : static_cast<uint8_t>(positionDegrees + direction));
}

constexpr bool shouldReportButtonPress(
    bool isPressed,
    bool pressAlreadyReported,
    uint32_t stableDurationMs) {
    return isPressed && !pressAlreadyReported &&
        stableDurationMs >= BUTTON_DEBOUNCE_MS;
}

constexpr bool shouldRearmButton(bool isPressed, uint32_t stableDurationMs) {
    return !isPressed && stableDurationMs >= BUTTON_DEBOUNCE_MS;
}

}  // namespace Station02
