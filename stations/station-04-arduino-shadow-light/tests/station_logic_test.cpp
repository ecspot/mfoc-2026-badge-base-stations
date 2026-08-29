#include <stdint.h>

#include "../Station04_Shadow_Light/StationLogic.h"

using namespace Station04;

static_assert(STATION_ADDRESS == 0xFB28U, "Station 4 address must remain locked");
static_assert(UNLOCK_COMMAND == 0x07U, "Unlock command must remain locked");
static_assert(
    encodeNecFrame(STATION_ADDRESS, UNLOCK_COMMAND) == 0xF807FB28UL,
    "Station 4 extended-NEC frame changed");

static_assert(isBadgeTriggerCommand(0x01U), "Advertisement must arm Station 4");
static_assert(isBadgeTriggerCommand(0x20U), "First report command must arm Station 4");
static_assert(isBadgeTriggerCommand(0x2FU), "Last report command must arm Station 4");
static_assert(!isBadgeTriggerCommand(0x00U), "Unknown command must not arm Station 4");
static_assert(!isBadgeTriggerCommand(0x30U), "Out-of-range report must not arm Station 4");

static_assert(CALIBRATION_MS == 1000UL, "Calibration must last one second");
static_assert(STEP_HOLD_MS == 1000UL, "Each shadow step must be held for one second");
static_assert(!isCalibrationUsable(199U), "Dim calibration must be rejected");
static_assert(isCalibrationUsable(200U), "Minimum usable calibration must pass");
static_assert(shadowThreshold(800U) == 480U, "Shadow threshold must be 60 percent");
static_assert(lightThreshold(800U) == 640U, "Light threshold must be 80 percent");

static_assert(expectsShadow(STEP_COVER_FIRST), "First step must expect a shadow");
static_assert(!expectsShadow(STEP_UNCOVER), "Second step must expect uncovered light");
static_assert(expectsShadow(STEP_COVER_SECOND), "Final step must expect a shadow");
static_assert(sensorMatchesStep(STEP_COVER_FIRST, 480U, 480U, 640U), "Covered threshold must match");
static_assert(!sensorMatchesStep(STEP_COVER_FIRST, 481U, 480U, 640U), "Above covered threshold must not match");
static_assert(sensorMatchesStep(STEP_UNCOVER, 640U, 480U, 640U), "Uncovered threshold must match");
static_assert(!sensorMatchesStep(STEP_UNCOVER, 639U, 480U, 640U), "Below uncovered threshold must not match");
static_assert(!shouldAdvanceStep(true, 999UL), "Step must not advance before one second");
static_assert(shouldAdvanceStep(true, 1000UL), "Step must advance at one second");
static_assert(!shouldAdvanceStep(false, 5000UL), "Wrong light state must not advance");
static_assert(nextStep(STEP_COVER_FIRST) == STEP_UNCOVER, "First cover must lead to uncover");
static_assert(nextStep(STEP_UNCOVER) == STEP_COVER_SECOND, "Uncover must lead to final cover");
static_assert(nextStep(STEP_COVER_SECOND) == STEP_COMPLETE, "Final cover must complete game");

int main() {
    return 0;
}
