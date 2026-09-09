#pragma once

#include <stdint.h>

namespace Station04 {

constexpr uint16_t STATION_ADDRESS = 0xFB24U;
constexpr uint8_t UNLOCK_COMMAND = 0x07U;
constexpr uint16_t MIN_USABLE_BASELINE = 200U;
constexpr uint32_t CALIBRATION_MS = 1000UL;
constexpr uint32_t STEP_HOLD_MS = 1000UL;
constexpr uint32_t GAME_TIMEOUT_MS = 45000UL;

enum ShadowStep : uint8_t {
    STEP_COVER_FIRST = 0U,
    STEP_UNCOVER = 1U,
    STEP_COVER_SECOND = 2U,
    STEP_COMPLETE = 3U,
};

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

constexpr bool expectsShadow(ShadowStep step) {
    return step == STEP_COVER_FIRST || step == STEP_COVER_SECOND;
}

constexpr bool sensorMatchesStep(
    ShadowStep step,
    uint16_t sensorReading,
    uint16_t coveredThreshold,
    uint16_t uncoveredThreshold) {
    return expectsShadow(step)
        ? sensorReading <= coveredThreshold
        : sensorReading >= uncoveredThreshold;
}

constexpr bool shouldAdvanceStep(bool sensorMatches, uint32_t stableDurationMs) {
    return sensorMatches && stableDurationMs >= STEP_HOLD_MS;
}

constexpr ShadowStep nextStep(ShadowStep step) {
    return step == STEP_COVER_FIRST
        ? STEP_UNCOVER
        : (step == STEP_UNCOVER ? STEP_COVER_SECOND : STEP_COMPLETE);
}

}  // namespace Station04
