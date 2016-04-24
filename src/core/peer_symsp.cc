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
        ip::udp::socket socket(this->io_service_);
        socket.open(ip::udp::v4());
        try {
          socket.send_to(buffer(std::string()), endpoint);
        } catch (std::exception e) {
          ERROR(e.what());
        }
        socket.close();
      }
    }
  }
  PeerNTS::SendMessage(message, endpoint);
}

unsigned int PeerSYMSP::GetPortStep() {
  return this->port_step_;
}

void PeerSYMSP::SetPortStep(unsigned int port_step) {
  this->port_step_ = port_step;
}

}
