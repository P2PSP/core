//
//  trusted_peer.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_TRUSTED_PEER_H
#define P2PSP_CORE_TRUSTED_PEER_H

#include <vector>
#include <boost/asio.hpp>

#include "malicious_peer.h"
#include "../util/trace.h"
#include "common.h"

namespace p2psp {

using namespace boost::asio;

class TrustedPeer : public MaliciousPeer {
 protected:
  static const int kPassNumber = 10;
  static const int kSamplingEffort = 2;
  int counter_;
  int next_sampled_index_;
  bool check_all_;
  ip::udp::endpoint current_sender_;

 public:
  TrustedPeer(){
    magic_flags_ = Common::kDBS;
  };
  ~TrustedPeer(){};
  virtual void Init() override;

  virtual void SetCheckAll(bool);
  virtual int CalculateNextSampled();
  virtual void SendChunkHash(int);
  virtual void ReceiveTheNextMessage(std::vector<char> &,
                                     ip::udp::endpoint &) override;
  virtual float CalcBufferCorrectness() override;
  virtual int ProcessNextMessage() override;
};
}

#endif  // P2PSP_CORE_TRUSTED_PEER_H
