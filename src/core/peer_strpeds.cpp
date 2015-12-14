
#include "peer_strpeds.h"

namespace p2psp {

void PeerStrpeDs::Init() {
  // message_format variable is not used in C++
  // self.message_format += '40s40s'
  bad_peers_ = std::vector<ip::udp::endpoint>();

  LOG("Initialized");
}

bool PeerStrpeDs::IsCurrentMessageFromSplitter() {
  return current_sender_ == splitter_;
}
void PeerStrpeDs::ReceiveTheNextMessage(std::vector<char> *message,
                                        ip::udp::endpoint *sender) {
  PeerIMS::ReceiveTheNextMessage(message, sender);
  current_sender_ = *sender;
}
}