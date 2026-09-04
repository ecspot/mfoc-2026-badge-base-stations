#include "Station02App.h"

#include <Arduino.h>
#include <Servo.h>

#include "StationLogic.h"

using namespace Station02;

namespace {

constexpr uint8_t SERVO_PIN = 5U;
constexpr uint8_t BUTTON_PIN = 6U;
constexpr uint8_t STATUS_LED_PIN = 7U;

constexpr unsigned long SERVO_STEP_INTERVAL_MS = 12UL;
constexpr unsigned long INTERACTION_TIMEOUT_MS = 30000UL;

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
    // If held at startup, require release before accepting a press.
    buttonPressReported = buttonCandidatePressed;

    Serial.print(F("D6 startup raw="));
    Serial.println(buttonCandidatePressed ? F("LOW / pressed") : F("HIGH / released"));

    attachServo();
    targetServo.write(servoPositionDegrees);
    digitalWrite(STATUS_LED_PIN, HIGH);

    Serial.println(F("Station armed: target sweeping; press in 85-95 degree zone"));
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
        Serial.println(F("BENCH TEST: IR unlock transmission disabled"));
        disarmStation(F("success; reset to play again"));
        return;
    }

    reportMiss();
}

void updateButton(unsigned long now) {
    const bool isPressed = digitalRead(BUTTON_PIN) == LOW;
    if (isPressed != buttonCandidatePressed) {
        buttonCandidatePressed = isPressed;
        buttonCandidateSinceMs = now;
        Serial.print(F("D6 raw="));
        Serial.println(isPressed ? F("LOW / pressed") : F("HIGH / released"));
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

}  // namespace

void station02Setup() {
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    Serial.begin(115200);
    delay(250);
    Serial.println(F("MFOC Station 2 - Arduino servo target"));
    Serial.println(F("BENCH TEST: IR disabled, servo D5, button D6, status D7"));
    armStation(millis());
}

void station02Loop() {
    const unsigned long now = millis();

    updateButton(now);
    updateServo(now);

    if (stationArmed && (now - armedAtMs) >= INTERACTION_TIMEOUT_MS) {
        disarmStation(F("30-second interaction timeout"));
    }
}
