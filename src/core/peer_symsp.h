//
//  peer_symsp.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#ifndef P2PSP_CORE_PEER_SYMSP_H
#define P2PSP_CORE_PEER_SYMSP_H

#include "peer_nts.h"
#include "../util/trace.h"
#include <list>
#include <mutex>

namespace p2psp {

class PeerSYMSP : public PeerNTS {
 protected:
  unsigned int port_step_;
  std::list<boost::asio::ip::udp::endpoint> endpoints_;
  std::mutex endpoints_mutex_;

  virtual void SendMessage(std::string message,
      boost::asio::ip::udp::endpoint endpoint) override;

 public:
  PeerSYMSP();
  ~PeerSYMSP();
  virtual void Init() override;

  unsigned int GetPortStep();
  void SetPortStep(unsigned int port_step);
};
}

#endif  // P2PSP_CORE_PEER_SYMSP_H
