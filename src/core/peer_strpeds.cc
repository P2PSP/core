//
//  peer_strpeds.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

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
void PeerStrpeDs::ReceiveTheNextMessage(std::vector<char> &message,
                                        ip::udp::endpoint &sender) {
  PeerIMS::ReceiveTheNextMessage(message, sender);
  current_sender_ = sender;
}
void PeerStrpeDs::ReceiveDsaKey() {
  int number_of_bytes = 256 + 256 + 256 + 40;
  std::vector<char> message(number_of_bytes);
  read(splitter_socket_, ::buffer(message));
  // TODO: finish implementation
}

void PeerStrpeDs::ProcessBadMessage(const std::vector<char> &message,
                                    const ip::udp::endpoint &sender) {
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
    /*
     TODO:
     uint16_t chunk_number = ntohs(*(short *)message.data());
    std::string chunk(message.data() + 2, message.data() + 2 + 1024);
    int k1 = boost::lexical_cast<int>(
        "0x" +
        std::string(message.data() + 2 + 1024, message.data() + 2 + 1024 + 40));
    int k2 = boost::lexical_cast<int>(
        "0x" + std::string(message.data() + 2 + 1024 + 40,
                           message.data() + 2 + 1024 + 40 + 40));*/

    // TODO: DSA
    // sign = (self.convert_to_long(k1), self.convert_to_long(k2))
    // m = str(chunk_number) + str(chunk) + str(sender)
    // return self.dsa_key.verify(SHA256.new(m).digest(), sign)
  }

  return true;
}

int PeerStrpeDs::HandleBadPeersRequest() {
  std::string bad("bad");
  std::vector<char> header(5);
  std::vector<char> msg(8);
  std::copy(bad.begin(), bad.end(), header.begin());
  *((uint16_t *)(header.data() + bad.size())) = (uint16_t)bad_peers_.size();

  team_socket_.send_to(buffer(header), splitter_);

  for (std::vector<ip::udp::endpoint>::iterator peer = bad_peers_.begin();
       peer != bad_peers_.end(); ++peer) {
    char *raw_ip = (char *)((*peer).address().to_v4().to_ulong());
    in_addr net_ip;
    inet_aton(raw_ip, &net_ip);

    std::memcpy(msg.data(), &net_ip, sizeof(net_ip));
    int port = peer->port();
    std::memcpy(msg.data() + sizeof(net_ip), &port, sizeof(port));

    team_socket_.send_to(buffer(msg), splitter_);
  }

  return -1;
}

int PeerStrpeDs::ProcessMessage(const std::vector<char> &message,
                                const ip::udp::endpoint &sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) ==
      bad_peers_.end()) {
    return -1;
  }

  if (IsCurrentMessageFromSplitter() || CheckMessage(message, sender)) {
    if (IsControlMessage(message) and (message[0] == 'B')) {
      return HandleBadPeersRequest();
    } else {
      return PeerDBS::ProcessMessage(message, sender);
    }
  } else {
    ProcessBadMessage(message, sender);
  }

  return -1;
}
}