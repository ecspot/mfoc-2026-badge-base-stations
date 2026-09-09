#include "../MFOC_Badge_Base_Station/protocol.h"

using namespace BadgeProtocol;

static_assert(makeUnlockAddress(1) == 0xFB21, "station 1 address mismatch");
static_assert(makeUnlockAddress(2) == 0xFB22, "station 2 address mismatch");
static_assert(makeUnlockAddress(3) == 0xFB23, "station 3 address mismatch");
static_assert(makeUnlockAddress(4) == 0xFB24, "station 4 address mismatch");
static_assert(makeUnlockAddress(5) == 0xFB25, "station 5 address mismatch");
static_assert(makeUnlockAddress(6) == 0xFB26, "station 6 address mismatch");
static_assert(makeUnlockAddress(7) == 0xFB80, "station 7 address mismatch");

static_assert(isBadgeTriggerCommand(0x01), "advertisement must trigger");
static_assert(isBadgeTriggerCommand(0x20), "report range start must trigger");
static_assert(isBadgeTriggerCommand(0x2F), "report range end must trigger");
static_assert(!isBadgeTriggerCommand(0x07), "unlock must not trigger a response");
static_assert(!isBadgeTriggerCommand(0x30), "out-of-range report must not trigger");

static_assert(UNLOCK_COMMAND == 0x07, "badge unlock command mismatch");

int main() {
    return 0;
}
