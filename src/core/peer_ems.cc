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


  void PeerEMS::SayHello(const ip::udp::endpoint &node) {
    //TODO: determine local address
    std::string hello("H");

    team_socket_.send_to(buffer(hello), node);

    TRACE("[Hello] sent to "
          << "(" << node.address().to_string() << ","
          << std::to_string(node.port()) << ")");
  }

}
