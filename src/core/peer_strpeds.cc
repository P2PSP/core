
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

bool PeerStrpeDs::IsControlMessage(std::vector<char> message) {
  return message.size() != (1026 + 40 + 40);
}

bool PeerStrpeDs::CheckMessage(std::vector<char> message,
                               ip::udp::endpoint sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) ==
      bad_peers_.end()) {
    return false;
  }

  if (!IsControlMessage(message)) {
    uint16_t chunk_number = ntohs(*(short *)message.data());
    std::string chunk(message.data() + 2, message.data() + 2 + 1024);
    int k1 = boost::lexical_cast<int>(
        "0x" +
        std::string(message.data() + 2 + 1024, message.data() + 2 + 1024 + 40));
    int k2 = boost::lexical_cast<int>(
        "0x" + std::string(message.data() + 2 + 1024 + 40,
                           message.data() + 2 + 1024 + 40 + 40));

    // TODO: DSA
    // sign = (self.convert_to_long(k1), self.convert_to_long(k2))
    // m = str(chunk_number) + str(chunk) + str(sender)
    // return self.dsa_key.verify(SHA256.new(m).digest(), sign)
  }

  return true;
}
}