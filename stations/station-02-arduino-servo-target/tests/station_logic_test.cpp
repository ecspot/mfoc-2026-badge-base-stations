#include <stdint.h>

#include "../Station02_Servo_Target/StationLogic.h"

using namespace Station02;

static_assert(STATION_ADDRESS == 0xFB22U, "Station 2 address must remain locked");
static_assert(UNLOCK_COMMAND == 0x07U, "Unlock command must remain locked");
static_assert(
    encodeNecFrame(STATION_ADDRESS, UNLOCK_COMMAND) == 0xF807FB22UL,
    "Station 2 extended-NEC frame changed");
static_assert(isBadgeTriggerCommand(0x01U), "Advertisement must arm Station 2");
static_assert(isBadgeTriggerCommand(0x20U), "First report command must arm Station 2");
static_assert(isBadgeTriggerCommand(0x2FU), "Last report command must arm Station 2");
static_assert(!isBadgeTriggerCommand(0x00U), "Unrecognized command must not arm Station 2");
static_assert(!isBadgeTriggerCommand(0x30U), "Out-of-range report must not arm Station 2");

static_assert(!isTargetInZone(84U), "84 degrees must be outside the target zone");
static_assert(isTargetInZone(85U), "85 degrees must be inside the target zone");
static_assert(isTargetInZone(90U), "90 degrees must be inside the target zone");
static_assert(isTargetInZone(95U), "95 degrees must be inside the target zone");
static_assert(!isTargetInZone(96U), "96 degrees must be outside the target zone");

static_assert(nextSweepPosition(90U, 1) == 91U, "Forward sweep must advance");
static_assert(nextSweepDirection(90U, 1) == 1, "Forward direction must continue");
static_assert(nextSweepPosition(160U, 1) == 159U, "Sweep must reverse at 160 degrees");
static_assert(nextSweepDirection(160U, 1) == -1, "Upper endpoint must reverse direction");
static_assert(nextSweepPosition(20U, -1) == 21U, "Sweep must reverse at 20 degrees");
static_assert(nextSweepDirection(20U, -1) == 1, "Lower endpoint must reverse direction");

static_assert(!shouldReportButtonPress(false, false, 100U), "Released button must not report");
static_assert(!shouldReportButtonPress(true, false, 29U), "Button must debounce for 30 ms");
static_assert(shouldReportButtonPress(true, false, 30U), "Stable press must report once");
static_assert(!shouldReportButtonPress(true, true, 100U), "Held button must not repeat");
static_assert(!shouldRearmButton(false, 29U), "Release must debounce for 30 ms");
static_assert(shouldRearmButton(false, 30U), "Stable release must re-arm button");
static_assert(!shouldRearmButton(true, 100U), "Pressed button must not re-arm");

int main() {
    return 0;
}
