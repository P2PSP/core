//
//  splitter_strpe.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_strpe.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterSTRPE::SplitterSTRPE()
    : SplitterLRS(), logging_(kLogging), current_round_(kCurrentRound) {
  LOG("STrPe");
}

SplitterSTRPE::~SplitterSTRPE() {}

void SplitterSTRPE::ModerateTheTeam() {
  // TODO: Check if something fails and a try catch statement has to be added

  std::vector<char> message(34);
  asio::ip::udp::endpoint sender;

  while (alive_) {
    size_t bytes_transferred = ReceiveMessage(message, sender);

    if (bytes_transferred == 2) {
      /*
       The peer complains about a lost chunk.

       In this situation, the splitter counts the number of
       complains. If this number exceeds a threshold, the
       unsupportive peer is expelled from the
       team.
       */

      uint16_t lost_chunk_number = GetLostChunkNumber(message);
      ProcessLostChunk(lost_chunk_number, sender);

    } else if (bytes_transferred == 34) {
      /*
       Trusted peer sends hash of received chunk
       number of chunk, hash (sha256) of chunk
       */

      if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) !=
          trusted_peers_.end()) {
        ProcessChunkHashMessage(message);
      }
    }

    else {
      /*
       The peer wants to leave the team.

       A !2-length payload means that the peer wants to go
       away.
       */

      // 'G'oodbye
      if (message.at(0) == 'G') {
        ProcessGoodbye(sender);
      }
    }
  }
}

void SplitterSTRPE::AddTrustedPeer(boost::asio::ip::udp::endpoint peer) {
  trusted_peers_.push_back(peer);
}

void SplitterSTRPE::PunishMaliciousPeer(boost::asio::ip::udp::endpoint peer) {
  if (logging_) {
    LogMessage("!!! malicious peer" + peer.address().to_string() + ":" +
               to_string(peer.port()));
  }

  LOG("!!! malicious peer " << peer);

  RemovePeer(peer);
}

void SplitterSTRPE::ProcessChunkHashMessage(std::vector<char> &message) {
  uint16_t chunk_number = *(uint16_t *)message.data();
  std::vector<char> hash(32);

  copy(message.data() + sizeof(uint16_t),
       message.data() + message.size() - sizeof(uint16_t), hash.data());

  std::vector<char> chunk_message = buffer_[chunk_number % buffer_size_];

  uint16_t stored_chunk_number = *(uint16_t *)chunk_message.data();
  std::vector<char> chunk;
  copy(chunk_message.data() + sizeof(uint16_t),
       chunk_message.data() + sizeof(uint16_t) + chunk_size_, chunk.data());

  stored_chunk_number = ntohs(stored_chunk_number);

  // TODO: && hashlib.sha256(chunk).digest() != hash
  if (stored_chunk_number == chunk_number) {
    asio::ip::udp::endpoint peer =
        destination_of_chunk_[chunk_number % buffer_size_];
    PunishMaliciousPeer(peer);
  }
}

void SplitterSTRPE::SetLogFile(std::string filename) {
  log_file_.open(filename);
}

void SplitterSTRPE::SetLogging(bool enabled) { logging_ = enabled; }

void SplitterSTRPE::LogMessage(std::string message) {
  log_file_ << BuildLogMessage(message);
  // TODO: Where to close the ofstream?
}

string SplitterSTRPE::BuildLogMessage(std::string message) {
  return to_string(time(NULL)) + "\t" + message;
}
}