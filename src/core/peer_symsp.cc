//
//  peer_symsp.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GNU_GENERAL_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "peer_symsp.h"
#include "common_nts.h"

using namespace p2psp;

Peer_SYMSP::Peer_SYMSP(){
  //magic_flags_ = Common::kNTS;
  this->port_step_ = 1;
  this->current_port_ = 0;
}

Peer_SYMSP::~Peer_SYMSP(){}

void Peer_SYMSP::Init() {
  INFO("Initialized");
}

void Peer_SYMSP::ReceiveNextMessage(std::vector<char> &message, ip::udp::endpoint &sender) {
  while (true) {
    for (auto& endpoint_socket : this->endpoints_) {
      ip::udp::socket& socket = endpoint_socket.second;
      if (socket.available() > 0) {
        size_t bytes_transferred = socket.receive_from(buffer(message), sender);
        message.resize(bytes_transferred);
        this->recvfrom_counter_++;

        #if defined __D_TRAFFIC__
        if (message.size() < 10) {
          TRACE("Message content = " << std::string(message.data()));
        }
        #endif
        return;
      }
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }
}

void Peer_SYMSP::SendMessage(std::string message, boost::asio::ip::udp::endpoint endpoint) {
  {
    std::unique_lock<std::mutex> lock(this->endpoints_mutex_);
    if (this->endpoints_.find(endpoint) == this->endpoints_.end()) {

      TRACE("New destination endpoint: " << endpoint);
      if (this->current_port_ == 0) {
        this->current_port_ = this->splitter_socket_.local_endpoint().port();
      } else {
        this->current_port_ += this->port_step_;
      }
      TRACE("Using source port: " << this->current_port_);

      this->endpoints_.emplace(std::piecewise_construct, std::forward_as_tuple(endpoint),
        std::forward_as_tuple(this->io_service_));
      ip::udp::socket& socket = this->endpoints_.at(endpoint);
      socket.open(ip::udp::v4());
      socket.set_option(ip::udp::socket::reuse_address(true));
      // This is the maximum time the peer will wait for a chunk
      // (from the splitter or from another peer).
      socket.bind(ip::udp::endpoint(ip::address_v4::any(), this->current_port_));
      socket.set_option(socket_base::linger(true, 1));
      //~ socket.set_option(socket_base::non_blocking(true));
    }
      
    try {
      this->endpoints_.at(endpoint).send_to(buffer(message), endpoint);
    } catch (std::exception e) {
      ERROR(e.what());
    }
  }
}

unsigned int Peer_SYMSP::GetPortStep() {
  return this->port_step_;
}

void Peer_SYMSP::SetPortStep(unsigned int port_step) {
  this->port_step_ = port_step;
}
