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
  bool bad_mouth_attack_;

 public:
  PeerStrpeDsMalicious(){};
  ~PeerStrpeDsMalicious(){};
  virtual void Init();
  virtual void SetBadMouthAttack(bool, std::vector<ip::udp::endpoint>);
  virtual void SetSelectiveAttack(bool, std::vector<ip::udp::endpoint>);
  virtual void SetOnOffAttack(bool, int);
  virtual void SetPersistentAttack(bool);
  virtual void GetPoisonedChunk(std::vector<char>*);
  virtual void SendChunk(ip::udp::endpoint);
  virtual int DbsProcessMessage(std::vector<char>, ip::udp::endpoint);
};
}

#endif  // P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H
