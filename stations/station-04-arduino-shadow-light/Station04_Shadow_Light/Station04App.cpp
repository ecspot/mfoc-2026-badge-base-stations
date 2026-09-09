#include "Station04App.h"

#include <Arduino.h>
#include <IRremote.hpp>

#include "StationLogic.h"

using namespace Station04;

namespace {

constexpr uint8_t IR_RECEIVER_PIN = 2U;
constexpr uint8_t IR_TRANSMITTER_PIN = 3U;
constexpr uint8_t ILLUMINATION_LED_PIN = 5U;
constexpr uint8_t GUIDE_LED_PIN = 6U;
constexpr uint8_t LIGHT_SENSOR_PIN = A0;
constexpr uint8_t STATUS_LED_PIN = LED_BUILTIN;

constexpr uint8_t FULL_FRAME_TRANSMISSIONS = 3U;
constexpr unsigned long BETWEEN_FRAMES_MS = 120UL;

// LDR wiring: 5 V -> LDR -> A0 -> 10 kΩ -> GND. Brighter means higher ADC.
enum RuntimePhase : uint8_t {
    PHASE_IDLE = 0U,
    PHASE_CALIBRATING = 1U,
    PHASE_PLAYING = 2U,
};

RuntimePhase phase = PHASE_IDLE;
unsigned long gameStartedAtMs = 0UL;
unsigned long calibrationStartedAtMs = 0UL;
uint32_t calibrationTotal = 0UL;
uint32_t calibrationSamples = 0UL;
uint16_t coveredThreshold = 0U;
uint16_t uncoveredThreshold = 0U;
ShadowStep currentStep = STEP_COVER_FIRST;
bool sensorStateMatching = false;
unsigned long sensorStateSinceMs = 0UL;

void setAllOutputsLow() {
    digitalWrite(ILLUMINATION_LED_PIN, LOW);
    digitalWrite(GUIDE_LED_PIN, LOW);
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

void setStepPrompt(ShadowStep step) {
    sensorStateMatching = false;
    digitalWrite(GUIDE_LED_PIN, expectsShadow(step) ? LOW : HIGH);

    if (step == STEP_COVER_FIRST) {
        Serial.println(F("STEP 1/3: cover the light sensor for one second"));
    } else if (step == STEP_UNCOVER) {
        Serial.println(F("STEP 2/3: uncover the light sensor for one second"));
    } else if (step == STEP_COVER_SECOND) {
        Serial.println(F("STEP 3/3: cover the light sensor for one second"));
    }
}

void armStation(unsigned long now) {
    phase = PHASE_CALIBRATING;
    gameStartedAtMs = now;
    calibrationStartedAtMs = now;
    calibrationTotal = 0UL;
    calibrationSamples = 0UL;
    currentStep = STEP_COVER_FIRST;
    sensorStateMatching = false;

    digitalWrite(ILLUMINATION_LED_PIN, HIGH);
    digitalWrite(GUIDE_LED_PIN, HIGH);
    digitalWrite(STATUS_LED_PIN, LOW);
    Serial.println(F("ARMED: leave sensor uncovered for one-second calibration"));
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

void completeStep(unsigned long now) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);

    currentStep = nextStep(currentStep);
    sensorStateMatching = false;
    sensorStateSinceMs = now;

    if (currentStep == STEP_COMPLETE) {
        Serial.println(F("SUCCESS: shadow sequence complete"));
        sendUnlockFrames();
        delay(250);
        disarmStation(F("success; waiting for next badge"));
        return;
    }

    setStepPrompt(currentStep);
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
        disarmStation(F("calibration too dim; improve illumination and retry"));
        return;
    }

    coveredThreshold = shadowThreshold(baseline);
    uncoveredThreshold = lightThreshold(baseline);
    Serial.print(F("Covered <= "));
    Serial.print(coveredThreshold);
    Serial.print(F(", uncovered >= "));
    Serial.println(uncoveredThreshold);

    phase = PHASE_PLAYING;
    currentStep = STEP_COVER_FIRST;
    setStepPrompt(currentStep);
}

void updateGame(unsigned long now) {
    const uint16_t reading = static_cast<uint16_t>(analogRead(LIGHT_SENSOR_PIN));
    const bool matches = sensorMatchesStep(
        currentStep,
        reading,
        coveredThreshold,
        uncoveredThreshold);

    if (!matches) {
        sensorStateMatching = false;
        return;
    }

    if (!sensorStateMatching) {
        sensorStateMatching = true;
        sensorStateSinceMs = now;
        return;
    }

    if (shouldAdvanceStep(true, now - sensorStateSinceMs)) {
        completeStep(now);
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
    pinMode(ILLUMINATION_LED_PIN, OUTPUT);
    pinMode(GUIDE_LED_PIN, OUTPUT);
    pinMode(STATUS_LED_PIN, OUTPUT);
    setAllOutputsLow();

    Serial.begin(115200);
    delay(250);
    Serial.println(F("MFOC Station 4 - Arduino shadow-light game"));
    Serial.println(F("Locked address=0xFB24 command=0x07"));
    Serial.println(F("IR RX D2, IR TX D3, lamp D5, guide D6, LDR A0"));

    IrReceiver.begin(IR_RECEIVER_PIN, DISABLE_LED_FEEDBACK);
    IrSender.begin(IR_TRANSMITTER_PIN);
    Serial.println(F("Station idle: waiting for badge"));
}

void station04Loop() {
    const unsigned long now = millis();
    pollBadge(now);

    if (phase != PHASE_IDLE && (now - gameStartedAtMs) >= GAME_TIMEOUT_MS) {
        disarmStation(F("45-second interaction timeout"));
        return;
    }

    if (phase == PHASE_CALIBRATING) {
        updateCalibration(now);
    } else if (phase == PHASE_PLAYING) {
        updateGame(now);
    }
}
