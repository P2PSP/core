// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2014, the P2PSP team.
// http://www.p2psp.org

// DBS: Data Broadcasting Set of rules

#ifndef P2PSP_CORE_MONITOR_DBS_H
#define P2PSP_CORE_MONITOR_DBS_H

#include "peer_dbs.h"
#include "../util/trace.h"

namespace p2psp {

class MonitorDBS : public PeerDBS {
  MonitorDBS();
  ~MonitorDBS();
  void Complain(uint16_t);
  uint16_t FindNextChunk();
};
}

#endif  // P2PSP_CORE_MONITOR_DBS_H
