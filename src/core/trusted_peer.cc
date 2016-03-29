//
//  trusted_peer.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "trusted_peer.h"

namespace p2psp {

void TrustedPeer::Init() {
  next_sampled_index_ = 0;
  counter_ = 1;
  LOG("Initialized");
}
void TrustedPeer::SetCheckAll(bool value) { check_all_ = value; };

int TrustedPeer::CalculateNextSampled() {
  if (check_all_) {
    return 0;
  }
  int max_random = (int)(peer_list_.size() / kSamplingEffort);
  return (int)((std::rand() % std::max(1, max_random)) + kPassNumber);
}

void TrustedPeer::SendChunkHash(int chunk_number) {
  Chunk chunk = chunks_[chunk_number % buffer_size_];

  std::vector<char> digest(32);
  Common::sha256(chunk.data, digest);

  std::vector<char> msg(34);

  *((uint16_t *)msg.data()) = htons((uint16_t)chunk_number);
  std::strcpy(msg.data() + sizeof(uint16_t), digest.data());

  team_socket_.send_to(buffer(msg), splitter_);
}

void TrustedPeer::ReceiveTheNextMessage(std::vector<char> &message,
                                        ip::udp::endpoint &sender) {
  PeerIMS::ReceiveTheNextMessage(message, sender);
  current_sender_ = sender;
}

float TrustedPeer::CalcBufferCorrectness() {
  std::vector<char> zerochunk(1024, 0);

  int goodchunks = 0;
  int badchunks = 0;

  for (std::vector<Chunk>::iterator it = chunks_.begin(); it != chunks_.end();
       ++it) {
    if (it->received) {
      if (it->data == zerochunk) {
        badchunks++;
      } else {
        goodchunks++;
      }
    }
  }

  return goodchunks / (float)(goodchunks + badchunks);
}

int TrustedPeer::ProcessNextMessage() {
  int chunk_number = PeerIMS::ProcessNextMessage();

  if (chunk_number > 0 && current_sender_ != splitter_) {
    if (counter_ == 0) {
      SendChunkHash(chunk_number);
      counter_ = CalculateNextSampled();
    } else {
      counter_--;
    }
  }

  return chunk_number;
}
}