//
// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2014, the P2PSP team.
// http://www.p2psp.org
//
// DBS: Data Broadcasting Set of rules
//

#ifndef P2PSP_CORE_PEER_DBS_H
#define P2PSP_CORE_PEER_DBS_H

#include <vector>
#include <string>
#include <tuple>
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <arpa/inet.h>
#include <ctime>
#include "../util/trace.h"
#include "peer_ims.h"

using namespace boost::asio;

namespace p2psp {

class PeerDBS : PeerIMS {
 public:
  PeerDBS();
  ~PeerDBS();
};
}

#endif  // P2PSP_CORE_PEER_DBS_H
