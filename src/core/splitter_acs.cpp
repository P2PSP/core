//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  ACS: Adaptive Chunk-rate Set of rules
//

#include "splitter_acs.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterACS::SplitterACS()
    : SplitterDBS(),
      period_(0, &SplitterDBS::GetHash),
      period_counter_(0, &SplitterACS::GetHash),
      number_of_sent_chunks_per_peer_(0, &SplitterACS::GetHash) {
  magic_flags_ = Common::kACS;
  LOG("Initialized ACS");
}

SplitterACS::~SplitterACS() {}

void SplitterACS::InsertPeer(boost::asio::ip::udp::endpoint peer) {
  SplitterDBS::InsertPeer(peer);
  period_[peer] = 1;
  period_counter_[peer] = 1;
  number_of_sent_chunks_per_peer_[peer] = 0;

  // TODO: Find a __debug__ flag in c++
  LOG("Inserted " << peer);
  // End TODO
}
void SplitterACS::IncrementUnsupportivityOfPeer(
    boost::asio::ip::udp::endpoint peer) {
  SplitterDBS::IncrementUnsupportivityOfPeer(peer);
  try {
    if (peer != peer_list_[0]) {
      period_[peer] += 1;
      period_counter_[peer] = period_[peer];
    }
  } catch (std::exception e) {
    LOG("Error: " << e.what());
  }
}
void SplitterACS::RemovePeer(boost::asio::ip::udp::endpoint peer) {}
void SplitterACS::ResetCounters() {}
void SplitterACS::SendChunk(std::vector<char> &message,
                            boost::asio::ip::udp::endpoint destination) {}
void SplitterACS::ComputeNextPeerNumber() {}
}