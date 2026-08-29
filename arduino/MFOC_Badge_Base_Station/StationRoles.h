#pragma once

#include <stdint.h>

enum class StationRole : uint8_t {
    ReceiveOnly = 0,
    ReceiveEvaluateUnlock = 1,
    TransmitUnlock = 2
};

constexpr bool isValidStationRole(StationRole role) {
    return role == StationRole::ReceiveOnly ||
           role == StationRole::ReceiveEvaluateUnlock ||
           role == StationRole::TransmitUnlock;
}

constexpr bool roleUsesReceiver(StationRole role) {
    return role == StationRole::ReceiveOnly ||
           role == StationRole::ReceiveEvaluateUnlock;
}

constexpr bool roleUsesTransmitter(StationRole role) {
    return role == StationRole::ReceiveEvaluateUnlock ||
           role == StationRole::TransmitUnlock;
}

constexpr bool shouldTransmitUnlock(
    StationRole role,
    bool isBadgeTrigger,
    bool cooldownReady) {
    return role == StationRole::ReceiveEvaluateUnlock &&
           isBadgeTrigger &&
           cooldownReady;
}
