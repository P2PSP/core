//
//  peer_strpeds_malicious.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//


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
  PeerStrpeDsMalicious(){
    magic_flags_ = Common::kSTRPE;
  };
  ~PeerStrpeDsMalicious(){};
  virtual void Init() override;
  virtual void SetBadMouthAttack(bool, std::string);
  virtual void SetSelectiveAttack(bool, std::string);
  virtual void SetOnOffAttack(bool, int) override;
  virtual void SetPersistentAttack(bool) override;
  virtual void GetPoisonedChunk(std::vector<char>&) override;
  virtual void SendChunk(const ip::udp::endpoint&) override;
  virtual int DbsProcessMessage(const std::vector<char>&,
                                const ip::udp::endpoint&);
  virtual int ProcessMessage(const std::vector<char>&,
                             const ip::udp::endpoint&) override;
};
}

#endif  // P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H
