//
//  malicious_peer.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

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
  virtual void Init() override;
  virtual void SendChunk(const ip::udp::endpoint&);
  virtual int ProcessMessage(const std::vector<char>&,
                             const ip::udp::endpoint&) override;

  virtual void GetPoisonedChunk(std::vector<char>&);
  virtual void SetPersistentAttack(bool);
  virtual void SetOnOffAttack(bool, int);
  virtual void SetSelectiveAttack(bool, const std::vector<ip::udp::endpoint>);
};
}

#endif  // P2PSP_CORE_MALICIOUS_PEER_H
