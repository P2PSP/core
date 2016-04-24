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
#include "../util/trace.h"

namespace p2psp {

MonitorNTS::MonitorNTS(){}

MonitorNTS::~MonitorNTS(){}

void MonitorNTS::Init() { LOG("Initialized"); }

// This is from MonitorDBS
void MonitorNTS::Complain(uint16_t chunk_number) {
  std::ostringstream msg_str;
  CommonNTS::Write<uint16_t>(msg_str, chunk_number);

  this->SendMessage(msg_str.str(), splitter_);

  DEBUG("lost chunk:" << std::to_string(chunk_number));
};

// This is from MonitorDBS
int MonitorNTS::FindNextChunk() {
  uint16_t chunk_number = (played_chunk_ + 1) % Common::kMaxChunkNumber;

  while (!chunks_[chunk_number % buffer_size_].received) {
    Complain(chunk_number);
    chunk_number = (chunk_number + 1) % Common::kMaxChunkNumber;
  }
  return chunk_number;
}

void MonitorNTS::DisconnectFromTheSplitter() {
  this->StartSendHelloThread();

  // Receive the generated ID for this peer from splitter
  this->ReceiveId();

  // There are currently no other peers in the team,
  // so this->initial_peer_list_ remains empty

  // Close the TCP socket
  PeerDBS::DisconnectFromTheSplitter();
}

int MonitorNTS::ProcessMessage(const std::vector<char>& message_bytes,
    const ip::udp::endpoint& sender) {
  // Handle NTS messages; pass other messages to base class
  std::string message(message_bytes.data(), message_bytes.size());

  if (sender != this->splitter_ &&
      (message.size() == CommonNTS::kPeerIdLength ||
       message.size() == CommonNTS::kPeerIdLength+1)) {
    // Hello message received from peer
    LOG("Received hello (ID "
        << message.substr(0, CommonNTS::kPeerIdLength) << ") from " << sender);
    // Send acknowledge
    this->SendMessage(message, sender);

    LOG("Forwarding ID " << message.substr(0, CommonNTS::kPeerIdLength)
        << " and source port " << sender.port() << " to splitter");
    std::ostringstream msg_str;
    msg_str << message;
    CommonNTS::Write<uint16_t>(msg_str, (uint16_t) sender.port());
    message_t message_data = std::make_pair(msg_str.str(), this->splitter_);
    this->SendMessage(message_data);
  } else if (sender == this->splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 6) {
    // [say hello to (X)] received from splitter
    std::istringstream msg_str(message);
    std::string peer_id =
        CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
    ip::address IP_addr = ip::address_v4(CommonNTS::Receive<uint32_t>(msg_str));
    uint16_t port = CommonNTS::Receive<uint16_t>(msg_str);
    ip::udp::endpoint peer(IP_addr, port);
    LOG("Received peer ID " << peer_id << ' ' << peer);
    // Sending hello not needed as monitor and peer already communicated
    if (!CommonNTS::Contains(this->peer_list_, peer)) {
      LOG("Appending peer " << peer_id << ' ' << peer << " to list");
      this->peer_list_.push_back(peer);
      this->debt_[peer] = 0;
    }
  } else {
    return PeerNTS::ProcessMessage(message_bytes, sender);
  }

  // No chunk number, as no chunk was received
  return -1;
}

}
