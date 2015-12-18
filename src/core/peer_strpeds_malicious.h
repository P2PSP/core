// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2015, the P2PSP team.
// http://www.p2psp.org

#ifndef P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H
#define P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H

#include <vector>
#include <boost/asio.hpp>

#include "peer_strpeds.h"
#include "../util/trace.h"

namespace p2psp {

using namespace boost::asio;

class PeerStrpeDsMalicious : public PeerStrpeDs {
 protected:
 public:
  PeerStrpeDsMalicious(){};
  ~PeerStrpeDsMalicious(){};
  virtual void Init();
};
}

#endif  // P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H
