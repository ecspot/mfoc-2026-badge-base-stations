#pragma once

#include <stdint.h>

namespace BadgeProtocol {

constexpr uint8_t UNLOCK_COMMAND = 0x07;
constexpr uint8_t MIN_STATION_NUMBER = 1;
constexpr uint8_t MAX_STATION_NUMBER = 7;
constexpr uint16_t UNLOCK_ADDRESSES[MAX_STATION_NUMBER] = {
    0xFB21,
    0xFB22,
    0xFB23,
    0xFB24,
    0xFB25,
    0xFB26,
    0xFB80,
};

constexpr uint16_t makeUnlockAddress(uint8_t stationNumber) {
    return UNLOCK_ADDRESSES[stationNumber - 1U];
}

constexpr bool isBadgeTriggerCommand(uint8_t command) {
    return command == 0x01U || (command >= 0x20U && command <= 0x2FU);
}

}  // namespace BadgeProtocol
