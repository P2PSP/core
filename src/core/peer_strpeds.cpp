
#include "peer_strpeds.h"

namespace p2psp {

void PeerStrpeDs::Init() {
  // message_format variable is not used in C++
  // self.message_format += '40s40s'
  bad_peers_ = std::vector<ip::udp::endpoint>();

  LOG("Initialized");
}
}