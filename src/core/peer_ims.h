//
//  peer_ims.h -- P2PSP's IP multicast transmission
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: Ip Multicasting Set of rules
//

#ifndef P2PSP_CORE_PEER_IMS_H
#define P2PSP_CORE_PEER_IMS_H

/* #include <arpa/inet.h> */
/* #include <boost/array.hpp> */
/* #include <boost/asio.hpp> */
/* #include <boost/date_time/posix_time/posix_time.hpp> */
/* #include <boost/thread/thread.hpp> */
/* #include <ctime> */
/* #include <fstream> */
/* #include <string> */
/* #include <tuple> */
/* #include <vector> */
/* #include "../util/trace.h" */
#include "peer_core.h"

namespace p2psp {

  class Peer_IMS : public Peer_core {

  protected:

    uint16_t mcast_port_;

  public:

    Peer_IMS();
    ~Peer_IMS();
    void Init();
    void ReceiveTheMcastChannel();
    void ListenToTheTeam();
    int ProcessMessage(const std::vector<char>&,
                               const ip::udp::endpoint&);
    ip::address GetMcastAddr();

  };
}

#endif  // P2PSP_CORE_PEER_IMS_H
