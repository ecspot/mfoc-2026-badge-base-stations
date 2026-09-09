#include <stdint.h>

#include "../Station04_Shadow_Light/StationLogic.h"

using namespace Station04;

static_assert(STATION_ADDRESS == 0xFB24U, "Station 4 address must remain locked");
static_assert(UNLOCK_COMMAND == 0x07U, "Unlock command must remain locked");
static_assert(
    encodeNecFrame(STATION_ADDRESS, UNLOCK_COMMAND) == 0xF807FB24UL,
    "Station 4 extended-NEC frame changed");

static_assert(isBadgeTriggerCommand(0x01U), "Advertisement must arm Station 4");
static_assert(isBadgeTriggerCommand(0x20U), "First report command must arm Station 4");
static_assert(isBadgeTriggerCommand(0x2FU), "Last report command must arm Station 4");
static_assert(!isBadgeTriggerCommand(0x00U), "Unknown command must not arm Station 4");
static_assert(!isBadgeTriggerCommand(0x30U), "Out-of-range report must not arm Station 4");

static_assert(CALIBRATION_MS == 1000UL, "Calibration must last one second");
static_assert(!isCalibrationUsable(199U), "Dim calibration must be rejected");
static_assert(isCalibrationUsable(200U), "Minimum usable calibration must pass");
static_assert(shadowThreshold(800U) == 480U, "Shadow threshold must be 60 percent");
static_assert(lightThreshold(800U) == 640U, "Light threshold must be 80 percent");

static_assert(isEventCountValid(3U), "Three events must be valid");
static_assert(isEventCountValid(6U), "Six events must be valid");
static_assert(!isEventCountValid(2U), "Two events must be rejected");
static_assert(!isEventCountValid(7U), "Seven events must be rejected");
static_assert(isEventDurationValid(1000UL), "One second must be valid");
static_assert(isEventDurationValid(4000UL), "Four seconds must be valid");
static_assert(!isEventDurationValid(999UL), "Sub-second events must be rejected");
static_assert(!isEventDurationValid(4001UL), "Events over four seconds must be rejected");

static_assert(sensorMatchesExpectation(true, 480U, 480U, 640U), "Hidden threshold must match");
static_assert(!sensorMatchesExpectation(true, 481U, 480U, 640U), "Too much light must not match hidden");
static_assert(sensorMatchesExpectation(false, 640U, 480U, 640U), "Uncovered threshold must match");
static_assert(!sensorMatchesExpectation(false, 639U, 480U, 640U), "Too little light must not match uncovered");

int main() {
    return 0;
}
