//
//  peer_dbs.h - Data Broadcasting Set of rules.
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "peer_dbs.h"

namespace p2psp {

  Peer_DBS::Peer_DBS() {
    // {{{

    max_chunk_debt_ = kMaxChunkDebt;
    ready_to_leave_the_team_ = false;
      
    // }}}
  }

  Peer_DBS::~Peer_DBS() {}

  void Peer_DBS::Init() {
    // {{{

#if defined __DEBUG__ || defined __SORS__
    TRACE("Initialized");
#endif
#if defined __DEBUG__ || defined __PARAMS__
    //TRACE("max_chunk_debt = " + std::to_string(kMaxChunkDebt));
    TRACE("max_chunk_debt = "
	  << max_chunk_debt_);
#endif

    // }}}
  }

  std::vector<ip::udp::endpoint> *Peer_DBS::GetPeerList() {
    return &peer_list_;
  }

  /*void Peer_DBS::SetTeamPort(uint16_t team_port) {
    team_port_ = team_port;
  }

  uint16_t Peer_DBS::GetTeamPort() {
    return team_port_;
  }

  uint16_t Peer_DBS::GetDefaultTeamPort() {
    return kTeamPort;
    }*/

  // Unused in this layer!
  void Peer_DBS::ReceiveMyEndpoint() {
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

#if defined __DEBUG__ || defined __TRAFFIC__
    TRACE("me = ("
	  << me_.address().to_string()
	  << ","
          << std::to_string(me_.port())
	  << ")");
#endif
    
  }

  void Peer_DBS::SayHello(const ip::udp::endpoint &node) {
    // {{{

    std::string hello("H");

    team_socket_.send_to(buffer(hello), node);

#if defined __DEBUG__ || defined __CHURN__
    TRACE("[Hello] sent to "
          << "(" << node.address().to_string()
	  << ","
          << std::to_string(node.port())
	  << ")");
#endif
    
    // }}}
  }

  void Peer_DBS::SayGoodbye(const ip::udp::endpoint &node) {
    // {{{

    std::string goodbye("G");

    team_socket_.send_to(buffer(goodbye), node);

#if defined __DEBUT__ || defined __TRAFFIC__
    TRACE("[Goodbye] sent to "
          << "(" << node.address().to_string()
	  << ","
          << std::to_string(node.port())
	  << ")");
#endif
    
    // }}}
  }

  /*void Peer_DBS::ReceiveMagicFlags() {
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
  }*/

  void Peer_DBS::ReceiveTheNumberOfPeers() {
    // {{{

    boost::array<char, 2> buffer;

#if defined __DEBUG__ || defined __TRAFFIC__
    // sys.stdout.write(Color.green)
    TRACE("Requesting the number of monitors and peers to ("
          << splitter_socket_.remote_endpoint().address().to_string()
	  << ","
          << std::to_string(splitter_socket_.remote_endpoint().port())
	  << ")");
#endif
    
    read(splitter_socket_, ::buffer(buffer));
    number_of_monitors_ = ntohs(*(short *)(buffer.c_array()));
#if defined __DEBUG__ || defined __TRAFFIC__
    TRACE("The number of monitors = "
	  << number_of_monitors_);
#endif
    
    read(splitter_socket_, ::buffer(buffer));
    number_of_peers_ = ntohs(*(short *)(buffer.c_array()));
#if defined __DEBUG__ || defined __TRAFFIC__
    TRACE("Total number of peers in the team (excluding me) = "
	  << number_of_peers_);
#endif
    
    // }}}
  }

  void Peer_DBS::ReceiveTheListOfPeers() {
    // {{{

    boost::array<char, 6> buffer;
    char *raw_data = buffer.data();
    ip::address ip_addr;
    ip::udp::endpoint peer;
    int port;

    ReceiveTheNumberOfPeers();
    
#if defined __DEBUG__ || defined __TRAFFIC__
    // sys.stdout.write(Color.green)
    TRACE("Requesting"
	  << number_of_peers_
	  << " peers to ("
          << splitter_socket_.remote_endpoint().address().to_string()
          << ","
	  << std::to_string(splitter_socket_.remote_endpoint().port())
          << ")");
#endif
    
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
#if defined __DEBUG__ ||  defined __CHURN__
      TRACE("[hello] sent to ("
	    << peer.address().to_string()
	    << ","
            << std::to_string(peer.port())
	    << ")");
#endif
      SayHello(peer);

      /*#if defined __DEBUG_TRAFFIC__
      TRACE(std::to_string((number_of_peers_ - tmp) / number_of_peers_));
      #endif*/
      
      peer_list_.push_back(peer);
      debt_[peer] = 0;
      tmp--;
      //}
    }

#if defined __DEBUG__ || defined __TRAFFIC__
    TRACE("List of peers received");
#endif

    // }}}
  }

  void Peer_DBS::ListenToTheTeam() {
    // {{{

#if defined __DEBUG__ || defined __PARAMS__
    TRACE("splitter port = "
	  << splitter_socket_.local_endpoint().port());
#endif
    
    ip::udp::endpoint endpoint(ip::address_v4::any(),
                               splitter_socket_.local_endpoint().port());

    team_socket_.open(endpoint.protocol());
    team_socket_.set_option(ip::udp::socket::reuse_address(true));
    team_socket_.bind(endpoint);

    // This is the maximum time the peer will wait for a chunk
    // (from the splitter or from another peer).
    team_socket_.set_option(socket_base::linger(true, 30));

    // }}}

  }

  int Peer_DBS::ProcessMessage(const std::vector<char> &message,
			       const ip::udp::endpoint &sender) {
    // {{{
    
    // Now, receive and send.

      /*#if defined __DEBUG_TRAFFIC__
    TRACE("Size: "
	  << message.size()
	  << " vs "
	  << message_size_)
	  #endif*/
    
      // TODO: remove hardcoded values
      if (message.size() == message_size_) {
	// {{{

	// A video chunk has been received
	ip::udp::endpoint peer;
	
	uint16_t chunk_number = ntohs(*(uint16_t *) message.data());

	chunk_ptr[chunk_number % buffer_size_].data
	  = std::vector<char>(message.data() + sizeof(uint16_t), message.data() + message.size());
	chunk_ptr[chunk_number % buffer_size_].chunk_number = chunk_number /*% buffer_size_*/;

	/*chunks_[chunk_number % buffer_size_] = {
	  std::vector<char>(message.data() + sizeof(uint16_t),
			    message.data() + sizeof(uint16_t) + chunk_size_),
			    true};*/
	
#if defined __DEBUG__ || defined __BUFFERING__
	TRACE("Chunk Inserted at: "
	      << (chunk_number % buffer_size_));
#endif
	
	received_counter_++;

	if (sender == splitter_) {
	  // {{{

	  // Send the previous chunk in burst sending
	  // mode if the chunk has not been sent to all
	  // the peers of the list of peers.

#if defined __DEBUG__ || defined __TRAFFIC__
	  TRACE("("
		<< team_socket_.local_endpoint().address().to_string()
		<< ","
		<< std::to_string(team_socket_.local_endpoint().port())
		<< ")"
		<< "<-"
		<< std::to_string(chunk_number)
		<< "-"
		<< "("
		<< sender.address().to_string()
		<< ","
		<< std::to_string(sender.port())
		<< ")");
#endif
	  
	  while (receive_and_feed_counter_ < (int) peer_list_.size()
		 && (receive_and_feed_counter_ > 0 or modified_list_)) {
	    // {{{

	    peer = peer_list_[receive_and_feed_counter_];
	    
	    team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
	    sendto_counter_++;

#if defined __DEBUG__ || defined __TRAFFIC__
	    TRACE("("
		  << team_socket_.local_endpoint().address().to_string()
		  << ","
		  << std::to_string(team_socket_.local_endpoint().port())
		  << ")"
		  << "-"
		  << std::to_string(ntohs(*(uint16_t *)receive_and_feed_previous_.data()))
		  << "->"
		  << "(" << peer.address().to_string()
		  << ","
		  << std::to_string(peer.port())
		  << ")");
#endif

	    debt_[peer]++;
	      
	    if (debt_[peer] > max_chunk_debt_/*kMaxChunkDebt*/) {
#if defined __DEBUG__ || defined __CHURN__
	      TRACE("("
		    << peer.address().to_string()
		    << ","
		    << std::to_string(peer.port())
		    << ")"
		    << " removed by unsupportive (" + std::to_string(debt_[peer]) + " lossess)");
#endif
	      debt_.erase(peer);
	      peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), peer));
	      //receive_and_feed_counter_--;
	    }
	    
	    receive_and_feed_counter_++;

	    // }}}
	  }

	  // Start playback with the first chunk received from the splitter //
	  std::vector<char> empty(message_size_, 0);
	  if (receive_and_feed_previous_ == empty) {
	    // {{{

	    played_chunk_ = ntohs(*(uint16_t *)message.data());
#if defined __DEBUG__ || defined __BUFFERING__
	    TRACE("First chunk to play modified "
		  << std::to_string(played_chunk_));
#endif

	    // }}}
	  }
	  // --------------------------------------------- //
	    
	  modified_list_ = false;

#if defined __DEBUG__ || defined __TRAFFIC__
	  TRACE("Sent "
		<< receive_and_feed_counter_
		<< " of "
		<< peer_list_.size());
	  TRACE("Last Chunk saved in receive and feed: "
		<< ntohs(*(uint16_t *)message.data()));
#endif
	  receive_and_feed_counter_ = 0;
	  receive_and_feed_previous_ = message;

	  // }}}
	} else {
	  // {{{

#if defined __DEBUG__ || defined __TRAFFIC__
	  TRACE("("
		<< team_socket_.local_endpoint().address().to_string()
		<< ","
		<< std::to_string(team_socket_.local_endpoint().port())
		<< ")"
		<< "<-"
		<< std::to_string(chunk_number)
		<< "-"
		<< "(" << sender.address().to_string()
		<< ","
		<< std::to_string(sender.port())
		<< ")");
#endif
	  if (peer_list_.end() == std::find(peer_list_.begin(), peer_list_.end(), sender)) {
	    // {{{

	    peer_list_.push_back(sender);
	    debt_[sender] = 0;
#if defined __DEBUG__ || defined __CHURN__
	    TRACE("("
		  << sender.address().to_string()
		  << ","
		  << std::to_string(sender.port())
		  << ")"
		  << " added by chunk "
		  << std::to_string(chunk_number));
#endif

	    // }}}
	  } else {
	    // {{{

	    debt_[sender]--;

	    // }}}
	  }

	  // }}}
	}
	
	// A new chunk has arrived and the previous must be forwarded
	// to next peer of the list of peers.
	
	std::vector<char> empty(message_size_, 0);
	
	if (receive_and_feed_counter_ < (int) peer_list_.size() && receive_and_feed_previous_!=empty) {
	  // {{{

	  // Send the previous chunk in congestion avoiding mode.
	  
	  peer = peer_list_[receive_and_feed_counter_];
#if defined __DEBUG__ || defined __TRAFFIC__
	  TRACE("Sending in congestion avoiding mode to "
		<< peer.address().to_string()
		<< ":"
		<< peer.port()
		<< "/ counter "
		<< receive_and_feed_counter_);
#endif
	  team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
	  sendto_counter_++;
	  
	  debt_[peer]++;
	  
	  if (debt_[peer] > max_chunk_debt_/*kMaxChunkDebt*/) {
	    // {{{

#if defined __DEBUG__ || defined __CHURN__
	    TRACE("("
		  << peer.address().to_string()
		  << ","
		  << std::to_string(peer.port())
		  << ")"
		  << " removed by unsupportive (" + std::to_string(debt_[peer]) + " lossess)");
#endif
	    debt_.erase(peer);
	    peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), peer));
	    //receive_and_feed_counter_--;

	    // }}}
	  }

#if defined __DEBUG__ || defined __TRAFFIC__
	  TRACE("("
		<< team_socket_.local_endpoint().address().to_string()
		<< ","
		<< std::to_string(team_socket_.local_endpoint().port())
		<< ")"
		<< "-"
		<< std::to_string(ntohs(*(short *)receive_and_feed_previous_.data()))
		<< "->"
		<< "("
		<< peer.address().to_string()
		<< ","
		<< std::to_string(peer.port())
		<< ")");
#endif
	  
	  receive_and_feed_counter_++;

	  // }}}
	}
	
	return chunk_number;

	// }}}
      } else {
	// {{{

	// A control chunk has been received
#if defined __DEBUG__ || defined __CHURN__
	TRACE("Control message received");
#endif
	if (message[0] == 'H') {
	  // {{{

	  if (peer_list_.end() == std::find(peer_list_.begin(), peer_list_.end(), sender)) {
	    // {{{

	    // The peer is new
	    peer_list_.push_back(sender);
	    debt_[sender] = 0;
#if defined __DEBUG__ || defined __CHURN__
	    TRACE("("
		  << sender.address().to_string()
		  << ","
		  << std::to_string(sender.port())
		  << ")"
		  << " added by [hello] ");
#endif

	    // }}}
	  }

	  // }}}
	} else {
	  // {{{

	  if (peer_list_.end() != std::find(peer_list_.begin(), peer_list_.end(), sender)) {
	    // {{{

#if defined __DEBUG__ || defined __CHURN__
	    TRACE("("
		  << team_socket_.local_endpoint().address().to_string()
		  << ","
		  << std::to_string(team_socket_.local_endpoint().port())
		  << ") \b: received \"goodbye\" from ("
		  << sender.address().to_string()
		  << ","
		  << std::to_string(sender.port())
		  << ")");
#endif
	    // sys.stdout.write(Color.none)
	    peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(),sender));
	    debt_.erase(sender);
	    if (receive_and_feed_counter_ > 0){
	      // {{{

	      modified_list_ = true;
	      receive_and_feed_counter_--;

	      // }}}
	    }

	    // }}}
	  } else {
	    // {{{

	    if (sender == splitter_){
	      // {{{

#if defined __DEBUG__ || defined __CHURN__
	      TRACE("Goodbye received from splitter");
#endif
	      waiting_for_goodbye_ = false;

	      // }}}
	    }

	    // }}}
	  }

	  // }}}
	}
	
	return -1;

	// }}}
      }
    
    return -1;

    // }}}
  }

  float Peer_DBS::CalcBufferCorrectness() {
    // {{{

    std::vector<char> zerochunk(chunk_size_, 0);

    int goodchunks = 0;
    int badchunks = 0;

    for (std::vector<Chunk>::iterator it = chunks_.begin(); it != chunks_.end();
         ++it) {
      if (it->chunk_number != -1) {
        if (it->data == zerochunk) {
          badchunks++;
        } else {
          goodchunks++;
        }
      }
    }

    return goodchunks / (float)(goodchunks + badchunks);

    // }}}
  }

  float Peer_DBS::CalcBufferFilling() {
    // {{{

    int chunks = 0;

    for (std::vector<Chunk>::iterator it = chunks_.begin(); it != chunks_.end();
         ++it) {
      if (it->chunk_number != -1) {
        chunks++;
      }
    }

#if defined __DEBUG__ || defined __BUFFERING__
    TRACE("Chunks in Buffer: " << chunks)
#endif
    return chunks / (float)buffer_size_;

    // }}}
  }

  void Peer_DBS::PoliteFarewell() {
    // {{{

    std::vector<char> message(message_size_);
    ip::udp::endpoint sender;

#if defined __DEBUG__ || defined __CHURN__
    TRACE("Goodbye!");
#endif
    
    while (receive_and_feed_counter_ < (int) peer_list_.size()) {
      team_socket_.send_to(buffer(receive_and_feed_previous_), peer_list_[receive_and_feed_counter_]);
      team_socket_.receive_from(buffer(message), sender);
#if defined __DEBUG__ || defined __TRAFFIC__
      TRACE("("
	    << team_socket_.local_endpoint().address().to_string()
	    << ","
	    << std::to_string(team_socket_.local_endpoint().port())
	    << ")"
	    << "-"
	    << std::to_string(ntohs(*(uint16_t*)receive_and_feed_previous_.data()))
	    << "->"
	    << "("
	    << peer_list_[receive_and_feed_counter_].address().to_string()
	    << ","
	    << std::to_string(peer_list_[receive_and_feed_counter_].port()) << ")");
#endif
      receive_and_feed_counter_++;
    }
    
    for (std::vector<ip::udp::endpoint>::iterator it = peer_list_.begin(); it != peer_list_.end(); ++it) {
      SayGoodbye(*it);
      //team_socket_.receive_from(buffer(message), sender);
    }

    ready_to_leave_the_team_ = true;
#if defined __DEBUG__ || defined __CHURN__
    TRACE("Ready to leave the team!");
#endif
    
    // }}}
  }

  void Peer_DBS::BufferData() {
    // {{{

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
    receive_and_feed_previous_ = std::vector<char>(message_size_);

    sendto_counter_ = 0;

    debt_memory_ = 1 << max_chunk_debt_/*kMaxChunkDebt*/;

    waiting_for_goodbye_ = true;

    Peer_core::BufferData();

    // }}}
  }

  void Peer_DBS::Start() {
    // {{{

    thread_group_.interrupt_all();
    thread_group_.add_thread(new boost::thread(&Peer_DBS::Run, this));

    // }}}
  }

  void Peer_DBS::Run() {
    // {{{

    std::vector<char> message(message_size_);
    ip::udp::endpoint sender;
    
    while (player_alive_ or waiting_for_goodbye_) {
      KeepTheBufferFull();
      
      if (!player_alive_){
	//for (int i = 0; i < 1; i++) {
	// ProcessNextMessage();
	SayGoodbye(splitter_);
	//team_socket_.receive_from(buffer(message), sender);
	//}
      }
      //PlayNextChunk();
    }
    PoliteFarewell();

    // }}}
  }

  bool Peer_DBS::AmIAMonitor() {
    // {{{

    // Only the first peers of the team are monitor peers
    return number_of_peers_ < number_of_monitors_;

    // message = self.splitter_socket.recv(struct.calcsize("c"))
    // if struct.unpack("c", message)[0] == '1':
    //    return True
    // else:
    //    return False

    // }}}
  }

  int Peer_DBS::GetNumberOfPeers() {
    // {{{

    return number_of_peers_;

    // }}}
  }

  void Peer_DBS::SetMaxChunkDebt(int max_chunk_debt) {
    // {{{

    max_chunk_debt_ = max_chunk_debt;

    // }}}
  }

  int Peer_DBS::GetMaxChunkDebt() {
    // {{{

    return max_chunk_debt_;

    // }}}
  }

  int Peer_DBS::GetDefaultMaxChunkDebt() {
    // {{{

    return kMaxChunkDebt;

    // }}}
  }

  bool Peer_DBS::IsReadyToLeaveTheTeam(){
    // {{{
    
    return ready_to_leave_the_team_;

    // }}}
  }
}
