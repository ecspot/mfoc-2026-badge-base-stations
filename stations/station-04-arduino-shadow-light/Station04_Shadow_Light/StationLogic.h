#pragma once

#include <stdint.h>

namespace Station04 {

constexpr uint16_t STATION_ADDRESS = 0xFB28U;
constexpr uint8_t UNLOCK_COMMAND = 0x07U;
constexpr uint16_t MIN_USABLE_BASELINE = 200U;
constexpr uint32_t CALIBRATION_MS = 1000UL;
constexpr uint8_t MIN_GAME_EVENTS = 3U;
constexpr uint8_t MAX_GAME_EVENTS = 6U;
constexpr uint32_t MIN_EVENT_HOLD_MS = 1000UL;
constexpr uint32_t MAX_EVENT_HOLD_MS = 4000UL;

constexpr uint32_t encodeNecFrame(uint16_t address, uint8_t command) {
    return static_cast<uint32_t>(address) |
        (static_cast<uint32_t>(command) << 16U) |
        (static_cast<uint32_t>(command ^ 0xFFU) << 24U);
}

constexpr bool isBadgeTriggerCommand(uint8_t command) {
    return command == 0x01U || (command >= 0x20U && command <= 0x2FU);
}

constexpr bool isCalibrationUsable(uint16_t baseline) {
    return baseline >= MIN_USABLE_BASELINE;
}

constexpr uint16_t shadowThreshold(uint16_t baseline) {
    return static_cast<uint16_t>(
        (static_cast<uint32_t>(baseline) * 60UL) / 100UL);
}

constexpr uint16_t lightThreshold(uint16_t baseline) {
    return static_cast<uint16_t>(
        (static_cast<uint32_t>(baseline) * 80UL) / 100UL);
}

constexpr bool sensorMatchesExpectation(
    bool expectsShadow,
    uint16_t sensorReading,
    uint16_t coveredThreshold,
    uint16_t uncoveredThreshold) {
    return expectsShadow
        ? sensorReading <= coveredThreshold
        : sensorReading >= uncoveredThreshold;
}

constexpr bool isEventCountValid(uint8_t eventCount) {
    return eventCount >= MIN_GAME_EVENTS && eventCount <= MAX_GAME_EVENTS;
}

constexpr bool isEventDurationValid(uint32_t durationMs) {
    return durationMs >= MIN_EVENT_HOLD_MS && durationMs <= MAX_EVENT_HOLD_MS;
}

}  // namespace Station04
