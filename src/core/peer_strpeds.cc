
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
void PeerStrpeDs::ReceiveDsaKey() {
  int number_of_bytes = 256 + 256 + 256 + 40;
  std::vector<char> message(number_of_bytes);
  read(splitter_socket_, ::buffer(message));
  // TODO: finish implementation
}

void PeerStrpeDs::ProcessBadMessage(std::vector<char> message,
                                    ip::udp::endpoint sender) {
  LOG("bad peer: " << sender);
  bad_peers_.push_back(sender);
  peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), sender));
}
}