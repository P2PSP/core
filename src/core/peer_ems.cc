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

    PeerIMS::ConnectToTheSplitter();

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
