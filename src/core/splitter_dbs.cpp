//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#include "splitter_dbs.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterDBS::SplitterDBS()
    : SplitterIMS(), magic_flags_(1), losses_(0, &SplitterDBS::GetHash) {
  // TODO: Check if there is a better way to replace kMcastAddr with 0.0.0.0
  mcast_addr_ = "0.0.0.0";
  max_chunk_loss_ = kMaxChunkLoss;
  monitor_number_ = kMonitorNumber;

  peer_number_ = 0;
  destination_of_chunk_.reserve(buffer_size_);

  // TODO: Initialize magic_flags with Common.DBS value

  LOG("max_chunk_loss = " << max_chunk_loss_);
  LOG("mcast_addr = " << mcast_addr_);
  LOG("Initialized");
}

SplitterDBS::~SplitterDBS() {}

void SplitterDBS::InsertPeer(boost::asio::ip::udp::endpoint peer) {
  if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
    peer_list_.push_back(peer);
    losses_[peer] = 0;
    LOG("Inserted peer (" << peer.address().to_string() << ", "
                          << to_string(peer.port()) << ")");
  }
}

asio::ip::udp::endpoint SplitterDBS::GetLosser(int lost_chunk_number) {
  return destination_of_chunk_[lost_chunk_number % buffer_size_];
}

void SplitterDBS::RemovePeer(asio::ip::udp::endpoint peer) {
  try {
    peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer),
                     peer_list_.end());
    peer_number_--;

    losses_.erase(peer);

  } catch (std::exception e) {
    LOG("Error: " << e.what());
  }
}

void SplitterDBS::ProcessGoodbye(boost::asio::ip::udp::endpoint peer) {
  LOG("Received 'goodbye' from " << peer);

  // TODO: stdout flush?

  RemovePeer(peer);
}

void SplitterDBS::SetupTeamSocket() {
  system::error_code ec;
  asio::ip::udp::endpoint endpoint(asio::ip::udp::v4(), port_);

  team_socket_.open(asio::ip::udp::v4());

  asio::socket_base::reuse_address reuseAddress(true);
  team_socket_.set_option(reuseAddress, ec);
  team_socket_.bind(endpoint);

  if (ec) {
    LOG("Error: " << ec.message());
  }
}

void SplitterDBS::ResetCounters() {
  unordered::unordered_map<asio::ip::udp::endpoint, int>::iterator it;
  for (it = losses_.begin(); it != losses_.end(); ++it) {
    losses_[it->first] = it->second / 2;
  }
}

void SplitterDBS::ResetCountersThread() {
  while (alive_) {
    ResetCounters();

    // TODO: Use Common.COUNTERS_TIMING instead of a hard coded number
    this_thread::sleep(posix_time::milliseconds(1000));
  }
}

void SplitterDBS::ComputeNextPeerNumber() {
  peer_number_ = (peer_number_ + 1) % peer_list_.size();
}
}