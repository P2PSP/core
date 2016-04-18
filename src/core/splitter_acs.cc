//
//  splitter_acs.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  ACS: Adaptive Chunk-rate Set of rules
//

#include "splitter_acs.h"
#include "../util/trace.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterACS::SplitterACS()
    : SplitterDBS(),
      period_(0, &SplitterDBS::GetHash),
      period_counter_(0, &SplitterACS::GetHash),
      number_of_sent_chunks_per_peer_(0, &SplitterACS::GetHash) {
  magic_flags_ = Common::kACS;
  TRACE("Initialized ACS");
}

SplitterACS::~SplitterACS() {}

void SplitterACS::InsertPeer(const boost::asio::ip::udp::endpoint &peer) {
  SplitterDBS::InsertPeer(peer);
  period_[peer] = 1;
  period_counter_[peer] = 1;
  number_of_sent_chunks_per_peer_[peer] = 0;

  TRACE("Inserted " << peer);
}

void SplitterACS::IncrementUnsupportivityOfPeer(
    const boost::asio::ip::udp::endpoint &peer) {
  SplitterDBS::IncrementUnsupportivityOfPeer(peer);
  try {
    if (peer != peer_list_[0]) {
      period_[peer] += 1;
      period_counter_[peer] = period_[peer];
    }
  } catch (std::exception e) {
    ERROR(e.what());
  }
}

void SplitterACS::RemovePeer(const boost::asio::ip::udp::endpoint &peer) {
  SplitterDBS::RemovePeer(peer);
  period_.erase(peer);
  period_counter_.erase(peer);
  number_of_sent_chunks_per_peer_.erase(peer);
}

void SplitterACS::ResetCounters() {
  SplitterDBS::ResetCounters();

  unordered::unordered_map<asio::ip::udp::endpoint, int>::iterator it;
  for (it = period_.begin(); it != period_.end(); ++it) {
    period_[it->first] = it->second - 1;
    if (it->second < 1) {
      period_[it->first] = 1;
    }
  }
}

void SplitterACS::SendChunk(const std::vector<char> &message,
                            const boost::asio::ip::udp::endpoint &destination) {
  SplitterDBS::SendChunk(message, destination);

  try {
    number_of_sent_chunks_per_peer_[destination] += 1;
  } catch (std::exception e) {
    ERROR(e.what());
  }
}

void SplitterACS::ComputeNextPeerNumber(asio::ip::udp::endpoint &peer) {
  try {
    while (period_counter_[peer] != 0) {
      period_counter_[peer] -= 1;
      peer_number_ = (peer_number_ + 1) % peer_list_.size();
      peer = peer_list_[peer_number_];
    }
    period_counter_[peer] = period_[peer];
  } catch (std::exception e) {
    ERROR(e.what());
  }
}

int SplitterACS::GetPeriod(const boost::asio::ip::udp::endpoint &peer) {
  return period_[peer];
}

int SplitterACS::GetNumberOfSentChunksPerPeer(
    const boost::asio::ip::udp::endpoint &peer) {
  return number_of_sent_chunks_per_peer_[peer];
}

void SplitterACS::SetNumberOfSentChunksPerPeer(
    const boost::asio::ip::udp::endpoint &peer, int number_of_sent_chunks) {
  number_of_sent_chunks_per_peer_[peer] = number_of_sent_chunks;
}
}
