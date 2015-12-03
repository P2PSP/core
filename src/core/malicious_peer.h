// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2015, the P2PSP team.
// http://www.p2psp.org

#ifndef P2PSP_CORE_MALICIOUS_PEER_H
#define P2PSP_CORE_MALICIOUS_PEER_H

#include <vector>
#include <boost/asio.hpp>

#include "peer_dbs.h"
#include "../util/trace.h"

namespace p2psp {

using namespace boost::asio;

class MaliciousPeer : public PeerDBS {
 protected:
  bool persistent_attack_ = false;
  bool on_off_attack_ = false;
  int on_off_ratio_ = 100;
  bool selective_attack_ = false;
  std::vector<ip::udp::endpoint> selected_peers_for_attack_;

 public:
  MaliciousPeer();
  ~MaliciousPeer();
  virtual void Init();
  void SendChunk(ip::udp::endpoint);

  void GetPoisonedChunk(std::vector<char>*);
  void SetPersistentAttack(bool);
  void SetOnOffAttack(bool, int);
  void SetSelectiveAttack(bool, const std::vector<ip::udp::endpoint>);
};
}

#endif  // P2PSP_CORE_MALICIOUS_PEER_H
