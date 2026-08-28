#pragma once

#include <stdint.h>

namespace BadgeProtocol {

constexpr uint16_t UNLOCK_ADDRESS_BASE = 0xFB20;
constexpr uint8_t UNLOCK_COMMAND = 0x07;
constexpr uint8_t MIN_STATION_NUMBER = 1;
constexpr uint8_t MAX_STATION_NUMBER = 5;

constexpr uint16_t makeUnlockAddress(uint8_t stationNumber) {
    return static_cast<uint16_t>(
        UNLOCK_ADDRESS_BASE |
        (static_cast<uint16_t>(1U) << (stationNumber - 1U)));
}

constexpr bool isBadgeTriggerCommand(uint8_t command) {
    return command == 0x01U || (command >= 0x20U && command <= 0x2FU);
}

}  // namespace BadgeProtocol
