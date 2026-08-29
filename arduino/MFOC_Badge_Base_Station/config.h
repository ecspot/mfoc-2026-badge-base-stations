#pragma once

#include <Arduino.h>

#include "StationRoles.h"

#define MFOC_ROLE_RECEIVE_ONLY 0
#define MFOC_ROLE_RECEIVE_EVALUATE_UNLOCK 1
#define MFOC_ROLE_TRANSMIT_UNLOCK 2

// Arduino IDE users select one role here. PlatformIO environments override it
// with a build flag so each role can be built without editing this file.
#ifndef MFOC_STATION_ROLE
#define MFOC_STATION_ROLE MFOC_ROLE_RECEIVE_EVALUATE_UNLOCK
#endif

constexpr StationRole STATION_ROLE =
    static_cast<StationRole>(MFOC_STATION_ROLE);

// Arduino Uno/Nano wiring defaults.
constexpr uint8_t IR_RECEIVER_PIN = 2;        // OUT from 38 kHz demodulating receiver
constexpr uint8_t IR_TRANSMITTER_PIN = 3;     // Drives IR LED transistor input
constexpr uint8_t ATTRACTION_TRIGGER_PIN = 4; // Logic pulse to animation controller
constexpr uint8_t STATUS_LED_PIN = LED_BUILTIN;

// Station 1 unlocks the first one-hot message flag. Valid values: 1..5.
constexpr uint8_t STATION_NUMBER = 1;

constexpr unsigned long BROADCAST_INTERVAL_MS = 2000UL;
constexpr unsigned long RESPONSE_COOLDOWN_MS = 750UL;
constexpr unsigned long ATTRACTION_PULSE_MS = 250UL;
constexpr uint8_t FULL_FRAME_TRANSMISSIONS = 3;
constexpr unsigned long BETWEEN_FRAMES_MS = 120UL;
