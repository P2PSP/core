//
//  peer_symsp.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "peer_symsp.h"
#include "common_nts.h"

namespace p2psp {

PeerSYMSP::PeerSYMSP(){
  this->port_step_ = 1;
}

PeerSYMSP::~PeerSYMSP(){}

void PeerSYMSP::Init() { LOG("Initialized"); }

void PeerSYMSP::SendMessage(std::string message,
    boost::asio::ip::udp::endpoint endpoint) {
  {
    std::unique_lock<std::mutex> lock(this->endpoints_mutex_);
    if (!CommonNTS::Contains(this->endpoints_, endpoint)) {
      this->endpoints_.push_back(endpoint);
      for (unsigned int i = 0; i < this->port_step_; i++) {
        ip::udp::endpoint local_endpoint(ip::address_v4::any(),
            this->splitter_socket_.local_endpoint().port());
        ip::udp::socket socket(this->io_service_);
        socket.open(local_endpoint.protocol());
        //~ socket.set_option(ip::udp::socket::reuse_address(true));
        //~ socket.bind(local_endpoint);
        //~ socket.bind(ip::udp::endpoint(ip::udp::v4(), this->team_socket_.local_endpoint().port()+i));
        socket.send_to(buffer(std::string()), endpoint);
        socket.close();
      }
    }
  }
  PeerNTS::SendMessage(message, endpoint);
}

}
