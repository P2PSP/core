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

  Peer_EMS::Peer_EMS() {

  }

  Peer_EMS::~Peer_EMS() {}

  //method from IMS but with sending of local endpoint added
  void Peer_EMS::ConnectToTheSplitter() throw(boost::system::system_error) {

    Peer_core::ConnectToTheSplitter();

    char message[7];
    in_addr addr;
    inet_aton(splitter_socket_.local_endpoint().address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(splitter_socket_.local_endpoint().port());
    (*(message+6))='P';
    splitter_socket_.send(boost::asio::buffer(message));

    INFO("send to splitter local endpoint = (" << splitter_socket_.local_endpoint().address().to_string() << ","
          << std::to_string(splitter_socket_.local_endpoint().port()) << ")");
  }

}
