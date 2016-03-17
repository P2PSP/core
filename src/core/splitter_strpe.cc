//
//  splitter_strpe.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_strpe.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterSTRPE::SplitterSTRPE()
    : SplitterLRS(), logging_(kLogging), current_round_(kCurrentRound) {
  magic_flags_ = Common::kSTRPE;
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

  LOG("Exiting moderate the team");
}

void SplitterSTRPE::AddTrustedPeer(const boost::asio::ip::udp::endpoint &peer) {
  trusted_peers_.push_back(peer);
}

void SplitterSTRPE::PunishMaliciousPeer(const boost::asio::ip::udp::endpoint &peer) {
  if (logging_) {
    LogMessage("!!! malicious peer" + peer.address().to_string() + ":" +
               to_string(peer.port()));
  }

  LOG("!!! malicious peer " << peer);

  RemovePeer(peer);
}

void SplitterSTRPE::ProcessChunkHashMessage(const std::vector<char> &message) {
  uint16_t chunk_number = *(uint16_t *)message.data();
  std::vector<char> hash(32);

  copy(message.data() + sizeof(uint16_t), message.data() + message.size(),
       hash.data());

  std::vector<char> chunk_message = buffer_[chunk_number % buffer_size_];

  uint16_t stored_chunk_number = *(uint16_t *)chunk_message.data();
  std::vector<char> chunk;
  copy(chunk_message.data() + sizeof(uint16_t),
       chunk_message.data() + chunk_size_, chunk.data());

  stored_chunk_number = ntohs(stored_chunk_number);

  std::vector<char> digest(32);
  Common::sha256(chunk, digest);
  if (stored_chunk_number == chunk_number && digest != hash) {
    asio::ip::udp::endpoint peer =
        destination_of_chunk_[chunk_number % buffer_size_];
    PunishMaliciousPeer(peer);
  }
}

void SplitterSTRPE::SetLogFile(const std::string &filename) {
  log_file_.open(filename);
}

void SplitterSTRPE::SetLogging(bool enabled) { logging_ = enabled; }

void SplitterSTRPE::LogMessage(const std::string &message) {
  log_file_ << BuildLogMessage(message);
  // TODO: Where to close the ofstream?
}

string SplitterSTRPE::BuildLogMessage(const std::string &message) {
  return to_string(time(NULL)) + "\t" + message;
}

void SplitterSTRPE::Run() {
  ReceiveTheHeader();

  /* A DBS splitter runs 4 threads. The main one and the
   "handle_arrivals" thread are equivalent to the daemons used
   by the IMS splitter. "moderate_the_team" and
   "reset_counters_thread" are new.
   */

  LOG("waiting for the monitor peers ...");

  std::shared_ptr<asio::ip::tcp::socket> connection =
      make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
  acceptor_.accept(*connection);
  HandleAPeerArrival(connection);

  // Threads
  thread t1(bind(&SplitterIMS::HandleArrivals, this));
  thread t2(bind(&SplitterSTRPE::ModerateTheTeam, this));
  thread t3(bind(&SplitterDBS::ResetCountersThread, this));

  vector<char> message(sizeof(uint16_t) + chunk_size_);
  asio::ip::udp::endpoint peer;

  while (alive_) {
    asio::streambuf chunk;
    size_t bytes_transferred = ReceiveChunk(chunk);
    try {
      peer = peer_list_.at(peer_number_);

      (*(uint16_t *)message.data()) = htons(chunk_number_);

      copy(asio::buffer_cast<const char *>(chunk.data()),
           asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
           message.data() + sizeof(uint16_t));

      SendChunk(message, peer);

      destination_of_chunk_[chunk_number_ % buffer_size_] = peer;
      chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;
      ComputeNextPeerNumber(peer);

      if (logging_) {
        if (peer_number_ == 0) {
          current_round_++;

          // TODO: Add the peers contained in peer_list_ to the message
          std::string message =
              to_string(current_round_) + to_string(peer_list_.size());
          LogMessage(message);
        }
      }
    } catch (const std::out_of_range &oor) {
      LOG("The monitor peer has died!");
      exit(-1);
    }

    chunk.consume(bytes_transferred);
  }
}

void SplitterSTRPE::Start() {
  LOG("Start");
  thread_.reset(new boost::thread(boost::bind(&SplitterSTRPE::Run, this)));
}
}
