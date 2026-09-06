#include "Station04App.h"

#include <Arduino.h>
#include <IRremote.hpp>

#include "StationLogic.h"

using namespace Station04;

namespace {

constexpr uint8_t IR_RECEIVER_PIN = 2U;
constexpr uint8_t IR_TRANSMITTER_PIN = 3U;
constexpr uint8_t GREEN_STATUS_LED_PIN = 5U;
constexpr uint8_t BLUE_GUIDE_LED_PIN = 6U;
constexpr uint8_t LIGHT_SENSOR_PIN = A0;
constexpr uint8_t STATUS_LED_PIN = LED_BUILTIN;

constexpr bool BENCH_TEST_MODE = false;
constexpr uint8_t FULL_FRAME_TRANSMISSIONS = 3U;
constexpr unsigned long BETWEEN_FRAMES_MS = 120UL;
constexpr unsigned long READY_BLINK_MS = 200UL;
constexpr unsigned long SUCCESS_BLINK_MS = 250UL;
constexpr unsigned long SUCCESS_DURATION_MS = 5000UL;

// LDR wiring: 5 V -> LDR -> A0 -> 10 kΩ -> GND. Brighter means higher ADC.
enum RuntimePhase : uint8_t {
    PHASE_IDLE = 0U,
    PHASE_CALIBRATING = 1U,
    PHASE_PLAYING = 2U,
};

RuntimePhase phase = PHASE_IDLE;
unsigned long calibrationStartedAtMs = 0UL;
uint32_t calibrationTotal = 0UL;
uint32_t calibrationSamples = 0UL;
uint16_t coveredThreshold = 0U;
uint16_t uncoveredThreshold = 0U;
uint8_t currentEvent = 0U;
uint8_t eventCount = 0U;
bool eventExpectsShadow = false;
unsigned long eventHoldMs = 0UL;
bool sensorStateMatching = false;
unsigned long sensorStateSinceMs = 0UL;

void setAllOutputsLow() {
    digitalWrite(GREEN_STATUS_LED_PIN, LOW);
    digitalWrite(BLUE_GUIDE_LED_PIN, LOW);
    digitalWrite(STATUS_LED_PIN, LOW);
}

void disarmStation(const __FlashStringHelper* reason) {
    phase = PHASE_IDLE;
    setAllOutputsLow();
    Serial.print(F("Station idle: "));
    Serial.println(reason);
}

void printFrame(uint16_t address, uint8_t command) {
    Serial.print(F("RX NEC address=0x"));
    Serial.print(address, HEX);
    Serial.print(F(" command=0x"));
    Serial.println(command, HEX);
}

void pulseLed(uint8_t pin, unsigned long durationMs) {
    digitalWrite(pin, HIGH);
    delay(durationMs);
    digitalWrite(pin, LOW);
    delay(durationMs);
}

void signalReady() {
    setAllOutputsLow();
    for (uint8_t cycle = 0U; cycle < 2U; ++cycle) {
        pulseLed(BLUE_GUIDE_LED_PIN, READY_BLINK_MS);
        pulseLed(GREEN_STATUS_LED_PIN, READY_BLINK_MS);
    }
}

void signalSuccess() {
    setAllOutputsLow();
    const uint8_t blinkCount = static_cast<uint8_t>(
        SUCCESS_DURATION_MS / (SUCCESS_BLINK_MS * 2UL));
    for (uint8_t blink = 0U; blink < blinkCount; ++blink) {
        pulseLed(GREEN_STATUS_LED_PIN, SUCCESS_BLINK_MS);
    }
}

void setEventPrompt() {
    sensorStateMatching = false;
    eventHoldMs = static_cast<unsigned long>(
        random(MIN_EVENT_HOLD_MS, MAX_EVENT_HOLD_MS + 1UL));
    digitalWrite(GREEN_STATUS_LED_PIN, LOW);
    digitalWrite(BLUE_GUIDE_LED_PIN, eventExpectsShadow ? HIGH : LOW);

    Serial.print(F("EVENT "));
    Serial.print(currentEvent + 1U);
    Serial.print('/');
    Serial.print(eventCount);
    Serial.print(eventExpectsShadow ? F(": LED ON - hide sensor for ")
                                    : F(": LED OFF - uncover sensor for "));
    Serial.print(eventHoldMs);
    Serial.println(F(" ms"));
}

void armStation(unsigned long now) {
    phase = PHASE_CALIBRATING;
    calibrationStartedAtMs = now;
    calibrationTotal = 0UL;
    calibrationSamples = 0UL;
    sensorStateMatching = false;

    digitalWrite(GREEN_STATUS_LED_PIN, HIGH);
    digitalWrite(BLUE_GUIDE_LED_PIN, HIGH);
    digitalWrite(STATUS_LED_PIN, LOW);
    Serial.println(F("SAMPLING: both LEDs on; leave sensor uncovered"));
}

void sendUnlockFrames() {
    setAllOutputsLow();
    digitalWrite(STATUS_LED_PIN, HIGH);

    Serial.print(F("TX Station 4 unlock address=0x"));
    Serial.print(STATION_ADDRESS, HEX);
    Serial.print(F(" command=0x"));
    Serial.println(UNLOCK_COMMAND, HEX);
    for (uint8_t frameIndex = 0U;
         frameIndex < FULL_FRAME_TRANSMISSIONS;
         ++frameIndex) {
        IrSender.sendNEC(STATION_ADDRESS, UNLOCK_COMMAND, 0);
        if (frameIndex + 1U < FULL_FRAME_TRANSMISSIONS) {
            delay(BETWEEN_FRAMES_MS);
        }
    }
    IrReceiver.resume();
}

void completeEvent() {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);

    ++currentEvent;
    sensorStateMatching = false;

    if (currentEvent >= eventCount) {
        Serial.println(F("SUCCESS: all randomized light events complete"));
        signalSuccess();
        if (BENCH_TEST_MODE) {
            Serial.println(F("BENCH TEST: IR unlock transmission disabled"));
        } else {
            sendUnlockFrames();
        }
        delay(250);
        disarmStation(BENCH_TEST_MODE
            ? F("success; reset to play again")
            : F("success; waiting for next badge"));
        return;
    }

    eventExpectsShadow = !eventExpectsShadow;
    setEventPrompt();
}

void updateCalibration(unsigned long now) {
    calibrationTotal += static_cast<uint16_t>(analogRead(LIGHT_SENSOR_PIN));
    ++calibrationSamples;

    if ((now - calibrationStartedAtMs) < CALIBRATION_MS) {
        return;
    }

    const uint16_t baseline = static_cast<uint16_t>(
        calibrationTotal / calibrationSamples);
    Serial.print(F("Calibration baseline="));
    Serial.println(baseline);

    if (!isCalibrationUsable(baseline)) {
        Serial.println(F("Calibration too dim; sampling again with both LEDs on"));
        calibrationStartedAtMs = now;
        calibrationTotal = 0UL;
        calibrationSamples = 0UL;
        return;
    }

    coveredThreshold = shadowThreshold(baseline);
    uncoveredThreshold = lightThreshold(baseline);
    Serial.print(F("Covered <= "));
    Serial.print(coveredThreshold);
    Serial.print(F(", uncovered >= "));
    Serial.println(uncoveredThreshold);

    digitalWrite(GREEN_STATUS_LED_PIN, LOW);
    digitalWrite(BLUE_GUIDE_LED_PIN, LOW);
    Serial.println(F("Calibration complete; signaling ready"));
    signalReady();

    eventCount = static_cast<uint8_t>(random(MIN_GAME_EVENTS, MAX_GAME_EVENTS + 1U));
    currentEvent = 0U;
    eventExpectsShadow = random(0L, 2L) == 1L;
    phase = PHASE_PLAYING;
    setEventPrompt();
}

void updateGame(unsigned long now) {
    const uint16_t reading = static_cast<uint16_t>(analogRead(LIGHT_SENSOR_PIN));
    const bool matches = sensorMatchesExpectation(
        eventExpectsShadow,
        reading,
        coveredThreshold,
        uncoveredThreshold);

    if (!matches) {
        digitalWrite(GREEN_STATUS_LED_PIN, LOW);
        sensorStateMatching = false;
        return;
    }

    digitalWrite(GREEN_STATUS_LED_PIN, HIGH);

    if (!sensorStateMatching) {
        sensorStateMatching = true;
        sensorStateSinceMs = now;
        return;
    }

    if ((now - sensorStateSinceMs) >= eventHoldMs) {
        completeEvent();
    }
}

void pollBadge(unsigned long now) {
    if (!IrReceiver.decode()) {
        return;
    }

    const auto& frame = IrReceiver.decodedIRData;
    const bool isCompleteNecFrame =
        frame.protocol == NEC && !(frame.flags & IRDATA_FLAGS_IS_REPEAT);
    const uint16_t address = static_cast<uint16_t>(frame.address);
    const uint8_t command = static_cast<uint8_t>(frame.command);

    if (isCompleteNecFrame) {
        printFrame(address, command);
    }
    IrReceiver.resume();

    if (isCompleteNecFrame && isBadgeTriggerCommand(command)) {
        if (phase == PHASE_IDLE) {
            armStation(now);
        } else {
            Serial.println(F("Station already armed; badge trigger ignored"));
        }
    }
}

}  // namespace

void station04Setup() {
    pinMode(GREEN_STATUS_LED_PIN, OUTPUT);
    pinMode(BLUE_GUIDE_LED_PIN, OUTPUT);
    pinMode(STATUS_LED_PIN, OUTPUT);
    setAllOutputsLow();

    Serial.begin(115200);
    delay(250);
    randomSeed(static_cast<unsigned long>(analogRead(A1)) ^ micros());
    Serial.println(F("MFOC Station 4 - Arduino shadow-light game"));
    Serial.println(F("Green status D5, blue guide D6, LDR A0"));
    if (BENCH_TEST_MODE) {
        Serial.println(F("BENCH TEST: IR disabled; starting automatically"));
        armStation(millis());
    } else {
        Serial.println(F("Locked address=0xFB28 command=0x07"));
        IrReceiver.begin(IR_RECEIVER_PIN, DISABLE_LED_FEEDBACK);
        IrSender.begin(IR_TRANSMITTER_PIN);
        Serial.println(F("Station idle; waiting for badge trigger"));
    }
}

void station04Loop() {
    const unsigned long now = millis();
    if (!BENCH_TEST_MODE) {
        pollBadge(now);
    }

    if (phase == PHASE_CALIBRATING) {
        updateCalibration(now);
    } else if (phase == PHASE_PLAYING) {
        updateGame(now);
    }
}
