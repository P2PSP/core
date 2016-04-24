//
//  monitor_nts.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#ifndef P2PSP_CORE_MONITOR_NTS_H
#define P2PSP_CORE_MONITOR_NTS_H

#include "monitor_dbs.h"
#include "peer_nts.h"

namespace p2psp {

class MonitorNTS : public PeerNTS {
 protected:
  // These two are from MonitorDBS:
  virtual void Complain(uint16_t);
  virtual int FindNextChunk() override;

  // Receive the generated ID for this peer from splitter and disconnect
  virtual void DisconnectFromTheSplitter() override;

  // Handle NTS messages; pass other messages to base class
  virtual int ProcessMessage(const std::vector<char>& message_bytes,
      const ip::udp::endpoint& sender) override;

 public:
  MonitorNTS();
  ~MonitorNTS();
  virtual void Init() override;
};
}

#endif  // P2PSP_CORE_MONITOR_NTS_H
