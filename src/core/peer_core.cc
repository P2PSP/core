//
//  peer_core.cc - P2PSP's core implementation
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//
//  Copyright (C) 2016, the P2PSP team.
//
//  http://www.p2psp.org
//

#include "peer_core.h"

namespace p2psp {

  constexpr char Peer_core::kSplitterAddr[];

  Peer_core::Peer_core()
    : io_service_(),
      splitter_socket_(io_service_),
      team_socket_(io_service_) {
    // {{{

    //player_port_ = kPlayerPort;
    splitter_addr_ = ip::address::from_string(kSplitterAddr);
    splitter_port_ = kSplitterPort;
    team_port_ = kTeamPort;
    use_localhost_ = kUseLocalhost;
    //buffer_status_ = kBufferStatus;
    //show_buffer_ = kShowBuffer;
    //buffer_size_ = 0;
    //chunk_size_ = 0;
    chunks_ = std::vector<Chunk>();
    //header_size_in_chunks_ = 0;
    //mcast_addr_ = ip::address::from_string("0.0.0.0");
    //mcast_port_ = 0;
    played_chunk_ = 0;
    player_alive_ = false;
    received_counter_ = 0;
    recvfrom_counter_ = 0;
    sendto_counter_ = -1;
    received_flag_ = std::vector<bool>();

    // }}}
  }

  Peer_core::~Peer_core() {}

  void Peer_core::Init() {};

  void Peer_core::ReceiveMcastChannel() {
    // {{{

    boost::array<char, 6> buffer;
    read(splitter_socket_, ::buffer(buffer));

    char *raw_data = buffer.data();

    in_addr ip_raw = *(in_addr *)(raw_data);
    mcast_addr_ = ip::address::from_string(inet_ntoa(ip_raw));
    mcast_port_ = ntohs(*(short *)(raw_data + 4));

    TRACE("mcast_endpoint = ("
	  << mcast_addr_.to_string()
	  << ","
          << std::to_string(mcast_port_)
	  << ")");

    // }}}
  }

  void Peer_core::ConnectToTheSplitter() throw(boost::system::system_error) {
    // {{{

    std::string my_ip;

    // TCP endpoint object to connect to splitter
    ip::tcp::endpoint splitter_tcp_endpoint(splitter_addr_, splitter_port_);

    // UDP endpoint object to connect to splitter
    splitter_ = ip::udp::endpoint(splitter_addr_, splitter_port_);

    ip::tcp::endpoint tcp_endpoint;

    TRACE("use_localhost = " << std::string((use_localhost_ ? "True" : "False")));
    if (use_localhost_) {
      my_ip = "0.0.0.0";
    } else {
      ip::udp::socket s(io_service_);
      try {
        s.connect(splitter_);
      } catch (boost::system::system_error e) {
        ERROR(e.what());
      }

      my_ip = s.local_endpoint().address().to_string();
      s.close();
    }

    splitter_socket_.open(splitter_tcp_endpoint.protocol());

    TRACE("Connecting to the splitter at ("
          << splitter_tcp_endpoint.address().to_string()
	  << ","
          << std::to_string(splitter_tcp_endpoint.port())
	  << ") from "
	  << my_ip);
    
    if (team_port_ != 0) {
      TRACE("I'm using port"
	    << std::to_string(team_port_));
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), team_port_);
      splitter_socket_.set_option(ip::udp::socket::reuse_address(true));      
    } else {    
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), 0);
    }

    splitter_socket_.bind(tcp_endpoint);

    // Could throw an exception
    splitter_socket_.connect(splitter_tcp_endpoint);

    TRACE("Connected to the splitter at ("
          << splitter_tcp_endpoint.address().to_string() << ","
          << std::to_string(splitter_tcp_endpoint.port()) << ")");

    // }}}
  }

  void Peer_core::DisconnectFromTheSplitter() {
    // {{{

    splitter_socket_.close();

    // }}}
  }

  void Peer_core::ReceiveChunkSize() {
    // {{{

    boost::array<char, 2> buffer;
    read(splitter_socket_, ::buffer(buffer));
    chunk_size_ = ntohs(*(short *)(buffer.c_array()));
    message_size_=kChunkIndexSize+chunk_size_;
    TRACE("chunk_size (bytes) = "
	  << std::to_string(chunk_size_));

    // }}}
  }

  void Peer_core::ReceiveBufferSize() {
    // {{{

    boost::array<char, 2> buffer;
    read(splitter_socket_, ::buffer(buffer));
    buffer_size_ = ntohs(*(short *)(buffer.c_array()));
    TRACE("buffer_size_ = "
	  << std::to_string(buffer_size_));

    // }}}
  }

  int Peer_core::ProcessMessage(const std::vector<char>&,
				const ip::udp::endpoint&) { return 0; }
  
  void Peer_core::BufferData() {
    // {{{

    // The peer dies if the player disconnects.
    player_alive_ = true;

    // The last chunk sent to the player.
    played_chunk_ = 0;

    // Counts the number of executions of the recvfrom() function.
    recvfrom_counter_ = 0;

    // The buffer of chunks is a structure that is used to delay the
    // consumption of the chunks in order to accommodate the network
    // jittter. Two components are needed: (1) the "chunks" buffer
    // that stores the received chunks and (2) the "received" buffer
    // that stores if a chunk has been received or not. Notice that
    // each peer can use a different buffer_size: the smaller the
    // buffer size, the lower start-up time, the higher chunk-loss
    // ratio. However, for the sake of simpliticy, all peers will use
    // the same buffer size.

    chunks_.resize(buffer_size_);
    received_counter_ = 0;

    // Wall time (execution time plus waiting time).
    clock_t start_time = clock();

    // We will send a chunk to the player when a new chunk is
    // received. Besides, those slots in the buffer that have not been
    // filled by a new chunk will not be send to the
    // player. Moreover, chunks can be delayed an unknown time.
    // This means that (due to the jitter) after chunk X, the chunk
    // X+Y can be received (instead of the chunk X+1). Alike, the
    // chunk X-Y could follow the chunk X. Because we implement the
    // buffer as a circular queue, in order to minimize the
    // probability of a delayed chunk overwrites a new chunk that is
    // waiting for traveling the player, we wil fill only the half
    // of the circular queue.

    TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
          << std::to_string(team_socket_.local_endpoint().port()) << ")"
          << "\b: buffering = 000.00%");
    TraceSystem::Flush();

    // First chunk to be sent to the player.  The
    // process_next_message() procedure returns the chunk number if a
    // packet has been received or -2 if a time-out exception has been
    // arised.

    int chunk_number = ProcessNextMessage();
    while (chunk_number < 0) {
      chunk_number = ProcessNextMessage();
      TRACE(std::to_string(chunk_number));
    }
    played_chunk_ = chunk_number;
    TRACE("First chunk to play " << std::to_string(played_chunk_));
    TRACE("(" << team_socket_.local_endpoint().address().to_string() << ","
          << std::to_string(team_socket_.local_endpoint().port()) << ")"
          << "\b: buffering (\b" << std::to_string(100.0 / buffer_size_));
    // TODO: Justify: .rjust(4)

    // Now, fill up to the half of the buffer.

    // float BUFFER_STATUS = 0.0f;
    while ((chunk_number - played_chunk_)< buffer_size_/2) {
      // TODO Format string
      // LOG("{:.2%}\r".format((1.0*x)/(buffer_size_/2)), end='');
      // BUFFER_STATUS = (100 * x) / (buffer_size_ / 2.0f) + 1;

      //if (!Common::kConsoleMode) {
        // GObject.idle_add(buffering_adapter.update_widget,BUFFER_STATUS)
      //} else {
        // pass
      //}
      TRACE("!");
      TraceSystem::Flush();

      while ((chunk_number = ProcessNextMessage()) < 0)
        ;
    }

    latest_chunk_number_ = chunk_number;

    TRACE("");
    TRACE("latency = " << std::to_string((clock() - start_time) /
                                         (float)CLOCKS_PER_SEC)
          << " seconds");
    TRACE("buffering done.");
    TraceSystem::Flush();

    // }}}
  }

  void Peer_core::ReceiveNextMessage(std::vector<char> &message, ip::udp::endpoint &sender) {
    // {{{

    TRACE("Waiting for a chunk at ("
          << team_socket_.local_endpoint().address().to_string()
	  << ","
          << std::to_string(team_socket_.local_endpoint().port())
	  << ")");

    size_t bytes_transferred = team_socket_.receive_from(buffer(message), sender);
    message.resize(bytes_transferred);
    recvfrom_counter_++;

    TRACE("Received a message from ("
          << sender.address().to_string()
	  << ","
	  << std::to_string(sender.port())
          << ") of length " << std::to_string(message.size()));

    if (message.size() < 10) {
      TRACE("Message content = " << std::string(message.data()));
    }

    // }}}
  }

  // Change the name of this function
  int Peer_core::ProcessNextMessage() {
    // {{{

    // (Chunk number + chunk payload) length
    std::vector<char> message(message_size_);
    ip::udp::endpoint sender;

    try {
      ReceiveNextMessage(message, sender);
    } catch (std::exception e) {
      return -2;
    }

    return ProcessMessage(message, sender);

    // }}}
  }

  void Peer_core::KeepTheBufferFull() {
    // {{{

    // Receive chunks while the buffer is not full
    // while True:
    //    chunk_number = self.process_next_message()
    //    if chunk_number >= 0:
    //        break

    int chunk_number = ProcessNextMessage();
    while (chunk_number < 0) {
      chunk_number = ProcessNextMessage();
    }
    // while ((chunk_number - self.played_chunk) % self.buffer_size) <
    // self.buffer_size/2:
    /*
    while (received_counter_ < buffer_size_ / 2) {
      chunk_number = ProcessNextMessage();
      while (chunk_number < 0) {
        chunk_number = ProcessNextMessage();
      }
    }
     */

    PlayNextChunk(chunk_number);
#ifdef _SHOW_BUFFER_
    std::string bf="";
    for (int i = 0; i<buffer_size_; i++) {
      if (chunks_[i].received) {
	// TODO: Avoid line feed in LOG function
	//TRACE(std::to_string(i % 10));
	bf=bf+"1";
      } else {
	//TRACE(".");
	bf=bf+"0";
      }
      LOG("Buffer state: "+bf);
    }
#endif
    
    // print (self.team_socket.getsockname(),)
    // sys.stdout.write(Color.none)

    // }}}
  }

  void Peer_core::PlayChunk(std::vector<char> chunk) {}
  
  void Peer_core::PlayNextChunk(int chunk_number) {
    // {{{

    /*played_chunk_ = FindNextChunk();
      
    //played_chunk_++;
    //if (chunks_[played_chunk_ % buffer_size_].received){
    PlayChunk(played_chunk_);
    chunks_[played_chunk_ % buffer_size_].received = false;
    received_counter_--;
    LOG("Chunk Consumed at: " << played_chunk_ % buffer_size_)
    //}else{
    //TRACE("lost chunk " << std::to_string(played_chunk_));
    //}*/
    
    for (int i = 0; i < (chunk_number-latest_chunk_number_);i++) {
      if (chunks_[chunk_number % buffer_size_].received == true){
	//PlayChunk(played_chunk_);
	PlayChunk(chunks_[played_chunk_ % buffer_size_].data);
	chunks_[played_chunk_ % buffer_size_].received = false;
	received_counter_--;
	LOG("Chunk Consumed at:" << played_chunk_ % buffer_size_)
	  }else{
	LOG("Chunk lost at: " << played_chunk_ % buffer_size_)
	  }
      
      played_chunk_++;
    }
    
    if ((latest_chunk_number_ % Common::kMaxChunkNumber) < chunk_number)
      latest_chunk_number_=chunk_number;

    // }}}
  }

  // Delete?
  void Peer_core::LogMessage(const std::string &message) {
    // {{{

    // TODO: self.LOG_FILE.write(self.build_log_message(message) + "\n")
    // print >>self.LOG_FILE, self.build_log_message(message)
	log_file_ << BuildLogMessage(message+"\n");
	log_file_.flush();

	// }}}
  }

  std::string Peer_core::BuildLogMessage(const std::string &message) {
    // {{{

    // return "{0}\t{1}".format(repr(time.time()), message)
	  return std::to_string(time(NULL)) + "\t" + message;

	  // }}}
  }

  void Peer_core::Run() {
    // {{{

    while (player_alive_) {
      KeepTheBufferFull();
      //PlayNextChunk();
    }

    // }}}
  }

  void Peer_core::Start() {
    // {{{

    thread_group_.interrupt_all();
    thread_group_.add_thread(new boost::thread(&Peer_core::Run, this));

    // }}}
  }

  int Peer_core::GetBufferSize() {
    // {{{

    return buffer_size_;

    // }}}
  }

  bool Peer_core::IsPlayerAlive() {
    // {{{

    return player_alive_;

    // }}}
  }

  int Peer_core::GetPlayedChunk() {
    // {{{

    return played_chunk_;

    // }}}
  }

  int Peer_core::GetChunkSize() {
    // {{{

    return chunk_size_;

    // }}}
  }

  int Peer_core::GetRecvfromCounter() {
    // {{{

    return recvfrom_counter_;

    // }}}
  }

  int Peer_core::GetSendtoCounter() {
    // {{{

    return sendto_counter_;

    // }}}
  }

  void Peer_core::SetSendtoCounter(int sendto_counter) {
    // {{{

    sendto_counter_ = sendto_counter;

    // }}}
  }

    void Peer_core::SetTeamPort(uint16_t team_port) {
    team_port_ = team_port;
  }

  //void Peer_core::SetSplitterAddr(std::string splitter_addr) {
  void Peer_core::SetSplitterAddr(ip::address splitter_addr) {
    // {{{

    splitter_addr_ = splitter_addr;//ip::address::from_string(splitter_addr);

    // }}}
  }

  void Peer_core::SetSplitterPort(uint16_t splitter_port) {
    // {{{

    splitter_port_ = splitter_port;

    // }}}
  }

  uint16_t Peer_core::GetSplitterPort() {
    // {{{

    return splitter_port_;

    // }}}
  }

  ip::address Peer_core::GetSplitterAddr() {
    // {{{

    return splitter_addr_;

    // }}}
  }

  void Peer_core::SetUseLocalHost(bool use_localhost) {
    // {{{

    use_localhost_ = use_localhost;

    // }}}
  }

  bool Peer_core::GetUseLocalHost() {
    // {{{

    return use_localhost_;

    // }}}
  }

  /*uint16_t Peer_core::GetDefaultPlayerPort() {
    // {{{

    return kPlayerPort;

    // }}}
    }*/
  
  uint16_t Peer_core::GetDefaultTeamPort() {
    // {{{

    return kTeamPort;

    // }}}
  }
  
  uint16_t Peer_core::GetDefaultSplitterPort() {
    // {{{

    return kSplitterPort;

    // }}}
  }

  ip::address Peer_core::GetDefaultSplitterAddr() {
    // {{{

    return ip::address::from_string(kSplitterAddr);;

    // }}}
  }

  ip::address Peer_core::GetMcastAddr() {
    // {{{

    //return mcast_addr_.to_string();
    return mcast_addr_;

    // }}}
  }

  uint16_t Peer_core::GetMcastPort() {
    // {{{

    return mcast_port_;

    // }}}
  }

  void Peer_core::ReceiveMagicFlags() {
    // {{{

    std::vector<char> magic_flags(1);
    read(splitter_socket_, ::buffer(magic_flags));
    TRACE("Magic flags = "
	  << std::bitset<8>(magic_flags[0]));

    // }}}
 }

  char Peer_core::GetMagicFlags() {
    return magic_flags_;
  }

}
