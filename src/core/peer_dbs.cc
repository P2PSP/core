//
//  peer_dbs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  DBS: Data Broadcasting Set of rules
//

#include "peer_dbs.h"

namespace p2psp {

  PeerDBS::PeerDBS() {
    magic_flags_ = Common::kDBS;
  }

  PeerDBS::~PeerDBS() {}

  void PeerDBS::Init() {
    TRACE("max_chunk_debt =" << std::to_string(kMaxChunkDebt));
    TRACE("Initialized");
  }

  void PeerDBS::SayHello(const ip::udp::endpoint &node) {
    std::string hello("H");

    team_socket_.send_to(buffer(hello), node);

    TRACE("[Hello] sent to "
          << "(" << node.address().to_string() << ","
          << std::to_string(node.port()) << ")");
  }

  void PeerDBS::SayGoodbye(const ip::udp::endpoint &node) {
    std::string goodbye("G");

    team_socket_.send_to(buffer(goodbye), node);

    TRACE("[Goodbye] sent to "
          << "(" << node.address().to_string() << ","
          << std::to_string(node.port()) << ")");
  }

  void PeerDBS::ReceiveMagicFlags() {
    std::vector<char> magic_flags(1);
    read(splitter_socket_, ::buffer(magic_flags));
    TRACE("Magic flags = " << std::bitset<8>(magic_flags[0]));
    if (this->magic_flags_ != magic_flags[0]) {
      ERROR("The splitter has different magic flags ("
        << std::bitset<8>(magic_flags[0]) << ") than this peer ("
        << std::bitset<8>(magic_flags_) << ").");
      ERROR("Please run splitter with a different parameter, or compile peer "
        << "with a different set of rules.");
      exit(1);
    }
  }

  void PeerDBS::ReceiveTheNumberOfPeers() {
    boost::array<char, 2> buffer;

    // sys.stdout.write(Color.green)
    TRACE("Requesting the number of monitors and peers to ("
          << splitter_socket_.remote_endpoint().address().to_string() << ","
          << std::to_string(splitter_socket_.remote_endpoint().port()) << ")");
    read(splitter_socket_, ::buffer(buffer));
    number_of_monitors_ = ntohs(*(short *)(buffer.c_array()));
    TRACE("The number of monitors is " << number_of_monitors_);
    read(splitter_socket_, ::buffer(buffer));
    number_of_peers_ = ntohs(*(short *)(buffer.c_array()));
    TRACE("The size of the team is " << number_of_peers_ << " (apart from me)");
  }

  void PeerDBS::ReceiveTheListOfPeers() {
    boost::array<char, 6> buffer;
    char *raw_data = buffer.data();
    ip::address ip_addr;
    ip::udp::endpoint peer;
    int port;

    // sys.stdout.write(Color.green)
    TRACE("Requesting" << number_of_peers_ << " peers to ("
          << splitter_socket_.remote_endpoint().address().to_string()
          << "," << std::to_string(
                                   splitter_socket_.remote_endpoint().port())
          << ")");
    // number_of_peers =
    // socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
    //_print_("The size of the team is", number_of_peers, "(apart from me)")

    int tmp = number_of_peers_;
    while (tmp > 0) {
      read(splitter_socket_, ::buffer(buffer));
      in_addr ip_raw = *(in_addr *)(raw_data);
      ip_addr = ip::address::from_string(inet_ntoa(ip_raw));
      port = ntohs(*(short *)(raw_data + 4));

      peer = ip::udp::endpoint(ip_addr, port);
      TRACE("[hello] sent to (" << peer.address().to_string() << ","
            << std::to_string(peer.port()) << ")");
      SayHello(peer);

      TRACE(std::to_string((number_of_peers_ - tmp) / number_of_peers_));

      peer_list_.push_back(peer);
      debt_[peer] = 0;
      tmp--;
      //}
    }

    TRACE("List of peers received");
  }

  void PeerDBS::ReceiveMyEndpoint() {
    boost::array<char, 6> buffer;
    char *raw_data = buffer.data();
    ip::address ip_addr;
    ip::udp::endpoint peer;
    int port;

    read(splitter_socket_, ::buffer(buffer));
    in_addr ip_raw = *(in_addr *)(raw_data);
    ip_addr = ip::address::from_string(inet_ntoa(ip_raw));
    port = ntohs(*(short *)(raw_data + 4));

    me_ = ip::udp::endpoint(ip_addr, port);

    TRACE("me = (" << me_.address().to_string() << ","
          << std::to_string(me_.port()) << ")");
  }

  void PeerDBS::ListenToTheTeam() {
    ip::udp::endpoint endpoint(ip::address_v4::any(),
                               splitter_socket_.local_endpoint().port());

    team_socket_.open(endpoint.protocol());
    team_socket_.set_option(ip::udp::socket::reuse_address(true));
    team_socket_.bind(endpoint);

    // This is the maximum time the peer will wait for a chunk
    // (from the splitter or from another peer).
    team_socket_.set_option(socket_base::linger(true, 30));
  }

  int PeerDBS::ProcessMessage(const std::vector<char> &message,
                              const ip::udp::endpoint &sender) {
    // Now, receive and send.

    // TODO: remove hardcoded values
    if (message.size() == message_size_) {
      // A video chunk has been received

      ip::udp::endpoint peer;

      uint16_t chunk_number = ntohs(*(short *)message.data());

      chunks_[chunk_number % buffer_size_] = {
        std::vector<char>(message.data() + sizeof(uint16_t),
                          message.data() + message.size()),
        true};

      received_counter_++;

      if (sender == splitter_) {
        // Send the previous chunk in burst sending
        // mode if the chunk has not been sent to all
        // the peers of the list of peers.

        TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
              << std::to_string(team_socket_.local_endpoint().port()) << ")"
              << "<-" << std::to_string(chunk_number) << "-"
              << "(" << sender.address().to_string() << ","
              << std::to_string(sender.port()) << ")");
        // No aqui. Tal vez, DIS

        if (kLogging) {
          LogMessage("buffer correctnes " +
                     std::to_string(CalcBufferCorrectness()));
          LogMessage("buffer filling " + std::to_string(CalcBufferFilling()));
        }

        while (receive_and_feed_counter_ < (int)peer_list_.size() &&
               receive_and_feed_counter_ > 0) {
          peer = peer_list_[receive_and_feed_counter_];
          team_socket_.send_to(::buffer(receive_and_feed_previous_), peer);
          sendto_counter_++;

          TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
                << std::to_string(team_socket_.local_endpoint().port()) << ")"
                << "-" << std::to_string(ntohs(receive_and_feed_previous_[0]))
                << "->"
                << "(" << peer.address().to_string() << ","
                << std::to_string(peer.port()) << ")");

          debt_[peer]++;

          if (debt_[peer] > kMaxChunkDebt) {
            TRACE("(" << peer.address().to_string() << ","
                  << std::to_string(peer.port()) << ")"
                  << " removed by unsupportive (" +
                  std::to_string(debt_[peer]) + " lossess)");
            debt_.erase(peer);
            peer_list_.erase(
                             std::find(peer_list_.begin(), peer_list_.end(), peer));
          }

          receive_and_feed_counter_++;
        }

        receive_and_feed_counter_ = 0;
        receive_and_feed_previous_ = message;
      } else {
        TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
              << std::to_string(team_socket_.local_endpoint().port()) << ")"
              << "<-" << std::to_string(chunk_number) << "-"
              << "(" << sender.address().to_string() << ","
              << std::to_string(sender.port()) << ")");

        if (peer_list_.end() ==
            std::find(peer_list_.begin(), peer_list_.end(), sender)) {
          peer_list_.push_back(sender);
          debt_[sender] = 0;
          TRACE("(" << sender.address().to_string() << ","
                << std::to_string(sender.port()) << ")"
                << " added by chunk " << std::to_string(chunk_number));
        } else {
          debt_[sender]--;
        }
      }

      // A new chunk has arrived and the previous must be forwarded to next peer
      // of
      // the list of peers.

      std::vector<char> empty(1024, 0);

      if (receive_and_feed_counter_ < (int)peer_list_.size() &&
          !receive_and_feed_previous_.empty()) {
        // Send the previous chunk in congestion avoiding mode.

        peer = peer_list_[receive_and_feed_counter_];
        team_socket_.send_to(::buffer(receive_and_feed_previous_), peer);
        sendto_counter_++;

        debt_[peer]++;

        if (debt_[peer] > kMaxChunkDebt) {
          TRACE("(" << peer.address().to_string() << ","
                << std::to_string(peer.port()) << ")"
                << " removed by unsupportive (" +
                std::to_string(debt_[peer]) + " lossess)");
          debt_.erase(peer);
          peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), peer));
        }

        TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
              << std::to_string(team_socket_.local_endpoint().port()) << ")"
              << "-" << std::to_string(ntohs(receive_and_feed_previous_[0]))
              << "->"
              << "(" << peer.address().to_string() << ","
              << std::to_string(peer.port()) << ")");

        receive_and_feed_counter_++;
      }

      return chunk_number;
    } else {
      // A control chunk has been received

      TRACE("Control message received");

      if (message[0] == 'H') {
        if (peer_list_.end() ==
            std::find(peer_list_.begin(), peer_list_.end(), sender)) {
          // The peer is new
          peer_list_.push_back(sender);
          debt_[sender] = 0;
          TRACE("(" << sender.address().to_string() << ","
                << std::to_string(sender.port()) << ")"
                << " added by [hello] ");
        } else {
          if (peer_list_.end() !=
              std::find(peer_list_.begin(), peer_list_.end(), sender)) {
            // sys.stdout.write(Color.red)
            TRACE("(" << team_socket_.local_endpoint().address().to_string()
                  << ","
                  << std::to_string(team_socket_.local_endpoint().port())
                  << ") \b: received \"goodbye\" from ("
                  << sender.address().to_string() << ","
                  << std::to_string(sender.port()) << ")");
            // sys.stdout.write(Color.none)
            peer_list_.erase(
                             std::find(peer_list_.begin(), peer_list_.end(), sender));
            debt_.erase(sender);
          }
        }

        return -1;
      }
    }

    return -1;
  }

  void PeerDBS::LogMessage(const std::string &message) {
    // TODO: self.LOG_FILE.write(self.build_log_message(message) + "\n")
    // print >>self.LOG_FILE, self.build_log_message(message)
  }

  void PeerDBS::BuildLogMessage(const std::string &message) {
    // return "{0}\t{1}".format(repr(time.time()), message)
  }

  float PeerDBS::CalcBufferCorrectness() {
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

  float PeerDBS::CalcBufferFilling() {
    int chunks = 0;

    for (std::vector<Chunk>::iterator it = chunks_.begin(); it != chunks_.end();
         ++it) {
      if (it->received) {
        chunks++;
      }
    }

    return chunks / (float)buffer_size_;
  }

  void PeerDBS::PoliteFarewell() {
    TRACE("Goodbye!");

    for (int i = 0; i < 3; i++) {
      // ProcessNextMessage();
      SayGoodbye(splitter_);
    }

    for (std::vector<ip::udp::endpoint>::iterator it = peer_list_.begin();
         it != peer_list_.end(); ++it) {
      SayGoodbye(*it);
    }
  }

  void PeerDBS::BufferData() {
    // Number of times that the previous received chunk has been sent to the team.
    // If this counter is smaller than the number of peers in the team, the
    // previous chunk must be sent in the burst mode because a new chunk from the
    // splitter has arrived and the previous received chunk has not been sent to
    // all the peers of the team. This can happen when one or more chunks that
    // were routed towards this peer have been lost.
    receive_and_feed_counter_ = 0;

    // This "private and static" variable holds the previous chunk received from
    // the splitter. It is used to send the previous received chunk in the
    // congestion avoiding mode. In that mode, the peer sends a chunk only when it
    // received a chunk from another peer or from the splitter.
    receive_and_feed_previous_ = std::vector<char>();

    sendto_counter_ = 0;

    debt_memory_ = 1 << kMaxChunkDebt;

    PeerIMS::BufferData();
  }

  void PeerDBS::Start() {
    thread_group_.interrupt_all();
    thread_group_.add_thread(new boost::thread(&PeerDBS::Run, this));
  }

  void PeerDBS::Run() {
    PeerIMS::Run();
    PoliteFarewell();
  }

  bool PeerDBS::AmIAMonitor() {
    // Only the first peers of the team are monitor peers
    return number_of_peers_ < number_of_monitors_;

    // message = self.splitter_socket.recv(struct.calcsize("c"))
    // if struct.unpack("c", message)[0] == '1':
    //    return True
    // else:
    //    return False
  }

  int PeerDBS::GetNumberOfPeers() {
    return number_of_peers_;
  }

  void PeerDBS::SetMaxChunkDebt(int max_chunk_debt) {
    max_chunk_debt_ = max_chunk_debt;
  }

  int PeerDBS::GetMaxChunkDebt() {
    return max_chunk_debt_;
  }

  int PeerDBS::GetDefaultMaxChunkDebt() {
    return kMaxChunkDebt;
  }

}
