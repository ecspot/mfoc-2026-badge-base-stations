#include "../MFOC_Badge_Base_Station/protocol.h"

using namespace BadgeProtocol;

static_assert(makeUnlockAddress(1) == 0xFB21, "station 1 address mismatch");
static_assert(makeUnlockAddress(2) == 0xFB22, "station 2 address mismatch");
static_assert(makeUnlockAddress(5) == 0xFB30, "station 5 address mismatch");

static_assert(isBadgeTriggerCommand(0x01), "advertisement must trigger");
static_assert(isBadgeTriggerCommand(0x20), "report range start must trigger");
static_assert(isBadgeTriggerCommand(0x2F), "report range end must trigger");
static_assert(!isBadgeTriggerCommand(0x07), "unlock must not trigger a response");
static_assert(!isBadgeTriggerCommand(0x30), "out-of-range report must not trigger");

static_assert(UNLOCK_COMMAND == 0x07, "badge unlock command mismatch");

int main() {
    return 0;
}
