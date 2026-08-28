#include <cassert>
#include <cstdint>
#include "../MFOC_Badge_Base_Station/protocol.h"

int main() {
    using namespace BadgeProtocol;

    assert(makeUnlockAddress(1) == 0xFB21);
    assert(makeUnlockAddress(2) == 0xFB22);
    assert(makeUnlockAddress(5) == 0xFB30);

    assert(isBadgeTriggerCommand(0x01));
    assert(isBadgeTriggerCommand(0x20));
    assert(isBadgeTriggerCommand(0x2F));
    assert(!isBadgeTriggerCommand(0x07));
    assert(!isBadgeTriggerCommand(0x30));

    assert(UNLOCK_COMMAND == 0x07);
    return 0;
}
