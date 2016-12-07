//
//  monitor_dbs.cc -- DBS peer monitor
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "monitor_dbs.h"

namespace p2psp {

  Monitor_DBS::Monitor_DBS() {
    //    magic_flags_ = Common::kDBS;
  };

  Monitor_DBS::~Monitor_DBS(){};

  void Monitor_DBS::ConnectToTheSplitter() throw(boost::system::system_error) {
    // {{{

    std::string my_ip;

    // TCP endpoint object to connect to splitter
    ip::tcp::endpoint splitter_tcp_endpoint(splitter_addr_, splitter_port_);

    // UDP endpoint object to connect to splitter
    splitter_ = ip::udp::endpoint(splitter_addr_, splitter_port_);

    ip::tcp::endpoint tcp_endpoint;

#if defined __D_PARAMS__
    TRACE("use_localhost = " << std::string((use_localhost_ ? "True" : "False")));
#endif

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

#if defined __D_TRAFFIC__
    TRACE("Connecting to the splitter at ("
          << splitter_tcp_endpoint.address().to_string()
    << ","
          << std::to_string(splitter_tcp_endpoint.port())
    << ") from "
    << my_ip);
#endif
    
    if (team_port_ != 0) {
#if defined __D_TRAFFIC__
      TRACE("I'm using port"
      << std::to_string(team_port_));
#endif
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), team_port_);
      splitter_socket_.set_option(ip::udp::socket::reuse_address(true));      
    } else {    
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), 0);
    }

    splitter_socket_.bind(tcp_endpoint);

    // Could throw an exception
    splitter_socket_.connect(splitter_tcp_endpoint);

#if defined __D_TRAFFIC__
    TRACE("Connected to the splitter at ("
          << splitter_tcp_endpoint.address().to_string() << ","
          << std::to_string(splitter_tcp_endpoint.port()) << ")");
#endif
    std::string monitor = "M";
    ip::udp::socket sock(io_service_);
    sock.send_to(boost::asio::buffer(monitor,monitor.length()),splitter_);
    sock.close();
    // }}}
  }

  void Monitor_DBS::Init() {
#if defined __D__ || defined __D_SORS__
    TRACE("Initialized");
#endif
  }

  void Monitor_DBS::Complain(uint16_t chunk_position) {
    std::vector<char> message(2);
    uint16_t chunk_number_network = htons(chunk_position);
    std::memcpy(message.data(), &chunk_number_network, sizeof(uint16_t));

    team_socket_.send_to(buffer(message), splitter_);

    TRACE("lost chunk:"
	  << std::to_string(chunk_position));
  };

#ifdef _1_
  
  /*int Monitor_DBS::FindNextChunk() {
    uint16_t chunk_number = (played_chunk_ + 1) % Common::kMaxChunkNumber;

    while (!chunks_[chunk_number % buffer_size_].received) {
      Complain(chunk_number);
      chunk_number = (chunk_number + 1) % Common::kMaxChunkNumber;
    }
    return chunk_number;
    }*/

  void Monitor_DBS::PlayNextChunk(int chunk_number) {
    for (int i = 0; i < (chunk_number-latest_chunk_number_);i++) {
      if (chunks_[chunk_number % buffer_size_].received) {
	//PlayChunk(played_chunk_);
	player_alive_ = PlayChunk(chunks_[played_chunk_ % buffer_size_].data);
	chunks_[played_chunk_ % buffer_size_].received = false;
	received_counter_--;
	INFO("Chunk Consumed at: "
	    << played_chunk_ % buffer_size_);
      } else {
	Complain(chunk_number); // <- Monitor specific 
	INFO("Chunk lost at: "
	    << played_chunk_ % buffer_size_);
      }

      played_chunk_++;
    }

    if ((latest_chunk_number_ % Common::kMaxChunkNumber) < chunk_number)
      latest_chunk_number_ = chunk_number;
  }

#endif
  
}
