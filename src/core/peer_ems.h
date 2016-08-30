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
#include "peer_nts.h"

using namespace boost::asio;

namespace p2psp {

  class Peer_EMS : public Peer_NTS {
  /* the only extension is a slightly modified connect to splitter method*/

  public:
    Peer_EMS();
    ~Peer_EMS();

    virtual void ConnectToTheSplitter() throw(boost::system::system_error)  override;


  };
}

#endif  // P2PSP_CORE_PEER_EMS_H
