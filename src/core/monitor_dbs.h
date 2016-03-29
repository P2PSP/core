//
//  monitor_dbs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  DBS: Data Broadcasting Set of rules
//

#ifndef P2PSP_CORE_MONITOR_DBS_H
#define P2PSP_CORE_MONITOR_DBS_H

#include "peer_dbs.h"
#include "../util/trace.h"

namespace p2psp {

class MonitorDBS : public PeerDBS {
 public:
  MonitorDBS();
  ~MonitorDBS();
  virtual void Init() override;
  virtual void Complain(uint16_t);
  virtual int FindNextChunk() override;
};
}

#endif  // P2PSP_CORE_MONITOR_DBS_H
