//
//  peer_ems.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#include "peer_ems.h"

namespace p2psp {

  PeerEMS::PeerEMS() {
    magic_flags_ = Common::kEMS;
  }

  PeerEMS::~PeerEMS() {}

  //method from IMS but with sending of local endpoint added
  void PeerEMS::ConnectToTheSplitter() throw(boost::system::system_error) {
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
          << splitter_tcp_endpoint.address().to_string() << ","
          << std::to_string(splitter_tcp_endpoint.port()) << ") from " << my_ip);
    if (team_port_ != 0) {
      TRACE("I'm using port" << std::to_string(team_port_));
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), team_port_);
      splitter_socket_.set_option(ip::udp::socket::reuse_address(true));
    } else {
      tcp_endpoint = ip::tcp::endpoint(ip::address::from_string(my_ip), 0);
    }

    splitter_socket_.bind(tcp_endpoint);

    // Should throw an exception
    splitter_socket_.connect(splitter_tcp_endpoint);

    TRACE("Connected to the splitter at ("
          << splitter_tcp_endpoint.address().to_string() << ","
          << std::to_string(splitter_tcp_endpoint.port()) << ")");

    //send local address to splitter

    std::string local_ip = splitter_socket_.local_endpoint().address().to_string();

    char message[6];
    in_addr addr;
    inet_aton(splitter_socket_.local_endpoint().address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(splitter_socket_.local_endpoint().port());
    splitter_socket_.send(boost::asio::buffer(message));

    TRACE("send to splitter local endpoint = (" << splitter_socket_.local_endpoint().address().to_string() << ","
          << std::to_string(splitter_socket_.local_endpoint().port()) << ")");
  }

}
