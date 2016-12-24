//
//  monitor_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "monitor_nts.h"
#include "../util/trace.h"

namespace p2psp {

  Monitor_NTS::Monitor_NTS(){
    //magic_flags_ = Common::kNTS;
  }

  Monitor_NTS::~Monitor_NTS(){}

  void Monitor_NTS::Init() { INFO("Initialized"); }

  // This is from Monitor_DBS
  void Monitor_NTS::Complain(uint16_t chunk_number) {
    std::ostringstream msg_str;
    Common_NTS::Write<uint16_t>(msg_str, chunk_number);

    this->SendMessage(msg_str.str(), splitter_);

    DEBUG("lost chunk:" << std::to_string(chunk_number));
  };

  // This is from Monitor_DBS
  /*int Monitor_NTS::FindNextChunk() {
    uint16_t chunk_number = (played_chunk_ + 1) % Common::kMaxChunkNumber;

    while (!chunks_[chunk_number % buffer_size_].received) {
      Complain(chunk_number);
      chunk_number = (chunk_number + 1) % Common::kMaxChunkNumber;
    }
    return chunk_number;
    }*/

  void Monitor_NTS::ConnectToTheSplitter() throw(boost::system::system_error) {
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
    char monitor[1] = {'M'};
    splitter_socket_.send(boost::asio::buffer(monitor));
    // }}}
  }

  void Monitor_NTS::DisconnectFromTheSplitter() {
    this->StartSendHelloThread();

    // Receive the generated ID for this peer from splitter
    this->ReceiveId();

    // There are currently no other peers in the team,
    // so this->initial_peer_list_ remains empty

    // Close the TCP socket
    Peer_DBS::DisconnectFromTheSplitter();
  }

  int Monitor_NTS::ProcessMessage(const std::vector<char>& message_bytes,
				 const ip::udp::endpoint& sender) {
    // Handle NTS messages; pass other messages to base class
    std::string message(message_bytes.data(), message_bytes.size());

    if (sender != this->splitter_ &&
	(message.size() == Common_NTS::kPeerIdLength ||
	 message.size() == Common_NTS::kPeerIdLength+1)) {
      // Hello message received from peer
      INFO("Received hello (ID "
	  << message.substr(0, Common_NTS::kPeerIdLength) << ") from " << sender);
      // Send acknowledge
      this->SendMessage(message, sender);

      INFO("Forwarding ID " << message.substr(0, Common_NTS::kPeerIdLength)
	  << " and source port " << sender.port() << " to splitter");
      std::ostringstream msg_str;
      msg_str << message;
      Common_NTS::Write<uint16_t>(msg_str, (uint16_t) sender.port());
      message_t message_data = std::make_pair(msg_str.str(), this->splitter_);
      this->SendMessage(message_data);
    } else if (sender == this->splitter_ &&
	       message.size() == Common_NTS::kPeerIdLength + 6) {
      // [say hello to (X)] received from splitter
      std::istringstream msg_str(message);
      std::string peer_id =
        Common_NTS::ReceiveString(msg_str, Common_NTS::kPeerIdLength);
      ip::address IP_addr = ip::address_v4(Common_NTS::Receive<uint32_t>(msg_str));
      uint16_t port = Common_NTS::Receive<uint16_t>(msg_str);
      ip::udp::endpoint peer(IP_addr, port);
      INFO("Received peer ID " << peer_id << ' ' << peer);
      // Sending hello not needed as monitor and peer already communicated
      if (!Common_NTS::Contains(this->peer_list_, peer)) {
	INFO("Appending peer " << peer_id << ' ' << peer << " to list");
	this->peer_list_.push_back(peer);
	this->debt_[peer] = 0;
      }
    } else {
      return Peer_NTS::ProcessMessage(message_bytes, sender);
    }

    // No chunk number, as no chunk was received
    return -1;
  }

}
