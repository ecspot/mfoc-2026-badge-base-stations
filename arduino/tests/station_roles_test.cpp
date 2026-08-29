#include "../MFOC_Badge_Base_Station/StationRoles.h"

static_assert(roleUsesReceiver(StationRole::ReceiveOnly));
static_assert(!roleUsesTransmitter(StationRole::ReceiveOnly));
static_assert(!shouldTransmitUnlock(StationRole::ReceiveOnly, true, true));

static_assert(roleUsesReceiver(StationRole::ReceiveEvaluateUnlock));
static_assert(roleUsesTransmitter(StationRole::ReceiveEvaluateUnlock));
static_assert(shouldTransmitUnlock(StationRole::ReceiveEvaluateUnlock, true, true));
static_assert(!shouldTransmitUnlock(StationRole::ReceiveEvaluateUnlock, false, true));
static_assert(!shouldTransmitUnlock(StationRole::ReceiveEvaluateUnlock, true, false));

static_assert(!roleUsesReceiver(StationRole::TransmitUnlock));
static_assert(roleUsesTransmitter(StationRole::TransmitUnlock));

int main() {
    return 0;
}
