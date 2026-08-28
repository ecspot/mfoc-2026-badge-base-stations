#include "BaseStation.h"

#include <Arduino.h>
#include <IRremote.hpp>

#include "config.h"
#include "protocol.h"

using namespace BadgeProtocol;

static_assert(
    STATION_NUMBER >= MIN_STATION_NUMBER && STATION_NUMBER <= MAX_STATION_NUMBER,
    "STATION_NUMBER must be in the range 1..5");

namespace {

unsigned long lastTransmissionMs = 0;

void pulseAttractionOutput() {
    digitalWrite(ATTRACTION_TRIGGER_PIN, HIGH);
    delay(ATTRACTION_PULSE_MS);
    digitalWrite(ATTRACTION_TRIGGER_PIN, LOW);
}

void sendUnlockFrame(const __FlashStringHelper* reason) {
    const uint16_t address = makeUnlockAddress(STATION_NUMBER);

    digitalWrite(STATUS_LED_PIN, HIGH);
    Serial.print(F("TX unlock address=0x"));
    Serial.print(address, HEX);
    Serial.print(F(" command=0x"));
    Serial.print(UNLOCK_COMMAND, HEX);
    Serial.print(F(" reason="));
    Serial.println(reason);

    // Send complete NEC frames rather than NEC repeat codes. The badge firmware
    // expects address + command data and does not use the NEC repeat frame.
    for (uint8_t i = 0; i < FULL_FRAME_TRANSMISSIONS; ++i) {
        IrSender.sendNEC(address, UNLOCK_COMMAND, 0);
        if (i + 1U < FULL_FRAME_TRANSMISSIONS) {
            delay(BETWEEN_FRAMES_MS);
        }
    }

    pulseAttractionOutput();
    digitalWrite(STATUS_LED_PIN, LOW);
    lastTransmissionMs = millis();
}

void printReceivedFrame(uint16_t address, uint8_t command) {
    Serial.print(F("RX NEC address=0x"));
    Serial.print(address, HEX);
    Serial.print(F(" command=0x"));
    Serial.println(command, HEX);
}

}  // namespace

void baseStationSetup() {
    pinMode(STATUS_LED_PIN, OUTPUT);
    pinMode(ATTRACTION_TRIGGER_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);
    digitalWrite(ATTRACTION_TRIGGER_PIN, LOW);

    Serial.begin(115200);
    delay(250);
    Serial.println(F("MFOC badge base station alpha - Arduino"));
    Serial.print(F("IR RX D"));
    Serial.print(IR_RECEIVER_PIN);
    Serial.print(F(", IR TX D"));
    Serial.print(IR_TRANSMITTER_PIN);
    Serial.print(F(", attraction D"));
    Serial.println(ATTRACTION_TRIGGER_PIN);

    IrReceiver.begin(IR_RECEIVER_PIN, DISABLE_LED_FEEDBACK);
    IrSender.begin(IR_TRANSMITTER_PIN);

    if (STATION_MODE == StationMode::ContinuousBroadcast) {
        Serial.println(F("Mode: continuous broadcast"));
        // Cause the first frame to be sent immediately.
        lastTransmissionMs = millis() - BROADCAST_INTERVAL_MS;
    } else {
        Serial.println(F("Mode: triggered response"));
    }
}

void baseStationLoop() {
    const unsigned long now = millis();

    if (IrReceiver.decode()) {
        const auto& frame = IrReceiver.decodedIRData;
        if (frame.protocol == NEC && !(frame.flags & IRDATA_FLAGS_IS_REPEAT)) {
            const uint16_t address = static_cast<uint16_t>(frame.address);
            const uint8_t command = static_cast<uint8_t>(frame.command);
            printReceivedFrame(address, command);

            const bool ready = (now - lastTransmissionMs) >= RESPONSE_COOLDOWN_MS;
            const bool shouldRespond =
                STATION_MODE == StationMode::TriggeredResponse &&
                isBadgeTriggerCommand(command) && ready;

            IrReceiver.resume();
            if (shouldRespond) {
                sendUnlockFrame(F("badge trigger"));
            }
        } else {
            IrReceiver.resume();
        }
    }

    if (STATION_MODE == StationMode::ContinuousBroadcast &&
        (now - lastTransmissionMs) >= BROADCAST_INTERVAL_MS) {
        sendUnlockFrame(F("timer"));
    }
}
