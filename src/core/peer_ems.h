//
//  peer_ems.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#ifndef P2PSP_CORE_PEER_EMS_H
#define P2PSP_CORE_PEER_EMS_H

#include <vector>
#include <string>
#include <map>
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <arpa/inet.h>
#include <ctime>
#include "../util/trace.h"
#include "peer_dbs.h"

using namespace boost::asio;

namespace p2psp {

  class PeerEMS : public PeerDBS {
  /* the only extension is a slightly modified hello method*/

  public:
    PeerEMS();
    ~PeerEMS();

    virtual void SayHello(const ip::udp::endpoint&) override;


  };
}

#endif  // P2PSP_CORE_PEER_EMS_H
