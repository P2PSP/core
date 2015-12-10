
#include "trusted_peer.h"

namespace p2psp {

void TrustedPeer::Init() {
  next_sampled_index_ = 0;
  counter_ = 1;
  LOG("Initialized");
}
void TrustedPeer::SetCheckAll(bool value) { check_all_ = value; };
  
int TrustedPeer::CalculateNextSampled() {
  if (check_all_) {
    return 0;
  }
  int max_random = (int)(peer_list_.size() / kSamplingEffort);
  return (int)((std::rand() % std::max(1, max_random)) + kPassNumber);
};
}