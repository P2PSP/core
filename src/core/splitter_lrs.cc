//
//  splitter_lrs.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunk Recovery Set of rules
//

#include "splitter_lrs.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterLRS::SplitterLRS() : SplitterACS(), buffer_(buffer_size_) {
  magic_flags_ = Common::kLRS;
  LOG("Initialized LRS");
}

SplitterLRS::~SplitterLRS() {}

void SplitterLRS::ProcessLostChunk(int lost_chunk_number,
                                   const boost::asio::ip::udp::endpoint &sender) {
  SplitterDBS::ProcessLostChunk(lost_chunk_number, sender);
  std::vector<char> message = buffer_.at(lost_chunk_number % buffer_size_);
  asio::ip::udp::endpoint peer = peer_list_.at(0);

  system::error_code ec;

  // TODO: Check if peer is the correct destination to send the message instead
  // of sender
  team_socket_.send_to(asio::buffer(message), peer, 0, ec);

  if (ec) {
    LOG("LRS - Error sending chunk: " << ec.message());
  }

  // TODO: Find a __debug__ flag in c++
  LOG("Re-sending " << to_string(lost_chunk_number) << " to " << peer);
  // End TODO
}

void SplitterLRS::SendChunk(const std::vector<char> &message,
                            const boost::asio::ip::udp::endpoint &destination) {
  SplitterDBS::SendChunk(message, destination);
  buffer_[chunk_number_ % buffer_size_] = message;
}
}