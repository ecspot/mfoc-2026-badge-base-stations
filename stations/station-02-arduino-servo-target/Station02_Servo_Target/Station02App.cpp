#include "Station02App.h"

#include <Arduino.h>
#include <IRremote.hpp>
#include <Servo.h>

#include "StationLogic.h"

using namespace Station02;

namespace {

constexpr uint8_t IR_RECEIVER_PIN = 2U;
constexpr uint8_t IR_TRANSMITTER_PIN = 3U;
constexpr uint8_t SERVO_PIN = 5U;
constexpr uint8_t BUTTON_PIN = 6U;
constexpr uint8_t STATUS_LED_PIN = LED_BUILTIN;

constexpr unsigned long SERVO_STEP_INTERVAL_MS = 20UL;
constexpr unsigned long INTERACTION_TIMEOUT_MS = 30000UL;
constexpr uint8_t FULL_FRAME_TRANSMISSIONS = 3U;
constexpr unsigned long BETWEEN_FRAMES_MS = 120UL;

Servo targetServo;
bool stationArmed = false;
bool servoAttached = false;
unsigned long armedAtMs = 0UL;
unsigned long lastServoStepMs = 0UL;
uint8_t servoPositionDegrees = SERVO_MIN_DEGREES;
int8_t servoDirection = 1;

bool buttonCandidatePressed = false;
bool buttonPressReported = false;
unsigned long buttonCandidateSinceMs = 0UL;

void printFrame(uint16_t address, uint8_t command) {
    Serial.print(F("RX NEC address=0x"));
    Serial.print(address, HEX);
    Serial.print(F(" command=0x"));
    Serial.println(command, HEX);
}

void attachServo() {
    if (!servoAttached) {
        targetServo.attach(SERVO_PIN);
        servoAttached = true;
    }
}

void detachServo() {
    if (servoAttached) {
        targetServo.detach();
        servoAttached = false;
    }
}

void disarmStation(const __FlashStringHelper* reason) {
    stationArmed = false;
    detachServo();
    digitalWrite(STATUS_LED_PIN, LOW);
    Serial.print(F("Station idle: "));
    Serial.println(reason);
}

void armStation(unsigned long now) {
    stationArmed = true;
    armedAtMs = now;
    lastServoStepMs = now;
    servoPositionDegrees = SERVO_MIN_DEGREES;
    servoDirection = 1;

    buttonCandidatePressed = digitalRead(BUTTON_PIN) == LOW;
    buttonCandidateSinceMs = now;
    // If held while the badge arrives, require release before accepting a press.
    buttonPressReported = buttonCandidatePressed;

    attachServo();
    targetServo.write(servoPositionDegrees);
    digitalWrite(STATUS_LED_PIN, HIGH);

    Serial.println(F("Station armed: target sweeping; press in 80-100 degree zone"));
}

void sendUnlockFrames() {
    detachServo();
    digitalWrite(STATUS_LED_PIN, HIGH);

    Serial.print(F("TX Station 2 unlock address=0x"));
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

void reportMiss() {
    Serial.print(F("MISS position="));
    Serial.print(servoPositionDegrees);
    Serial.println(F(" degrees; release and try again"));

    digitalWrite(STATUS_LED_PIN, LOW);
    delay(100);
    digitalWrite(STATUS_LED_PIN, HIGH);
}

void handleButtonPress() {
    if (isTargetInZone(servoPositionDegrees)) {
        Serial.print(F("SUCCESS position="));
        Serial.println(servoPositionDegrees);
        sendUnlockFrames();
        disarmStation(F("success; waiting for next badge"));
        return;
    }

    reportMiss();
}

void updateButton(unsigned long now) {
    const bool isPressed = digitalRead(BUTTON_PIN) == LOW;
    if (isPressed != buttonCandidatePressed) {
        buttonCandidatePressed = isPressed;
        buttonCandidateSinceMs = now;
        return;
    }

    const unsigned long stableDurationMs = now - buttonCandidateSinceMs;
    if (shouldRearmButton(isPressed, stableDurationMs)) {
        buttonPressReported = false;
    }

    if (!stationArmed ||
        !shouldReportButtonPress(
            isPressed,
            buttonPressReported,
            stableDurationMs)) {
        return;
    }

    buttonPressReported = true;
    handleButtonPress();
}

void updateServo(unsigned long now) {
    if (!stationArmed || (now - lastServoStepMs) < SERVO_STEP_INTERVAL_MS) {
        return;
    }

    const int8_t nextDirection =
        nextSweepDirection(servoPositionDegrees, servoDirection);
    const uint8_t nextPosition =
        nextSweepPosition(servoPositionDegrees, servoDirection);
    servoDirection = nextDirection;
    servoPositionDegrees = nextPosition;
    targetServo.write(servoPositionDegrees);
    lastServoStepMs = now;
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
        if (!stationArmed) {
            armStation(now);
        } else {
            Serial.println(F("Station already armed; badge trigger ignored"));
        }
    }
}

}  // namespace

void station02Setup() {
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    Serial.begin(115200);
    delay(250);
    Serial.println(F("MFOC Station 2 - Arduino servo target"));
    Serial.println(F("Locked address=0xFB22 command=0x07"));
    Serial.println(F("IR RX D2, IR TX D3, servo D5, button D6"));

    IrReceiver.begin(IR_RECEIVER_PIN, DISABLE_LED_FEEDBACK);
    IrSender.begin(IR_TRANSMITTER_PIN);
    Serial.println(F("Station idle: waiting for badge"));
}

void station02Loop() {
    const unsigned long now = millis();

    pollBadge(now);
    updateButton(now);
    updateServo(now);

    if (stationArmed && (now - armedAtMs) >= INTERACTION_TIMEOUT_MS) {
        disarmStation(F("30-second interaction timeout"));
    }
}
