
#include "trusted_peer.h"

namespace p2psp {

void TrustedPeer::Init() {
  next_sampled_index_ = 0;
  counter_ = 1;
  LOG("Initialized");
}
}