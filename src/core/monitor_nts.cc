//
//  monitor_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "monitor_nts.h"

namespace p2psp {

MonitorNTS::MonitorNTS(){};

MonitorNTS::~MonitorNTS(){};

void MonitorNTS::Init() { LOG("Initialized"); }


void MonitorNTS::DisconnectFromTheSplitter() {
  this->StartSendHelloThread();

  // Receive the generated ID for this peer from splitter
  this->ReceiveId();

  // There are currently no other peers in the team,
  // so this->initial_peer_list_ remains empty

  // Close the TCP socket
  PeerNTS::DisconnectFromTheSplitter();
}

int MonitorNTS::ProcessMessage(const std::vector<char>& message_bytes,
    const ip::udp::endpoint& sender) {
  // Handle NTS messages; pass other messages to base class
  std::string message(message_bytes.data(), message_bytes.size());

  if (sender != PeerNTS::splitter_ &&
      (message.size() == CommonNTS::kPeerIdLength ||
       message.size() == CommonNTS::kPeerIdLength+1)) {
    // Hello message received from peer
    // TODO: if __debug__:
    {
      LOG("NTS: Received hello (ID "
          << message.substr(0, CommonNTS::kPeerIdLength) << " from " << sender);
    }
    // Send acknowledge
    PeerNTS::team_socket_.send_to(buffer(message), sender);

    // TODO: if __debug__:
    {
      LOG("NTS: Forwarding ID " << message.substr(0, CommonNTS::kPeerIdLength)
          << " and source port " << sender.port() << " to splitter");
    }
    std::ostringstream msg_str(message);
    CommonNTS::Write(msg_str, sender.port());
    message_t message_data = std::make_pair(msg_str.str(), PeerNTS::splitter_);
    this->SendMessage(message_data);
  } else if (sender == PeerNTS::splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 6) {
    // [say hello to (X)] received from splitter
    std::istringstream msg_str(message);
    std::string peer_id =
        CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
    ip::address IP_addr = ip::address_v4(CommonNTS::Receive<uint32_t>(msg_str));
    uint16_t port = CommonNTS::Receive<uint16_t>(msg_str);
    ip::udp::endpoint peer(IP_addr, port);
    // TODO: if __debug__:
    {
      LOG("NTS: Received peer ID " << peer_id << ' ' << peer);
    }
    // Sending hello not needed as monitor and peer already communicated
    if (!CommonNTS::Contains(PeerNTS::peer_list_, peer)) {
      LOG("NTS: Appending peer " << peer_id << ' ' << peer << " to list");
      PeerNTS::peer_list_.push_back(peer);
      PeerNTS::debt_[peer] = 0;
    }
  } else {
    return PeerNTS::ProcessMessage(message_bytes, sender);
  }

  // No chunk number, as no chunk was received
  return -1;
}

}
