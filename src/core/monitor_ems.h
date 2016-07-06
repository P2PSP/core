//
//  monitor_ems.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#ifndef P2PSP_CORE_MONITOR_EMS_H
#define P2PSP_CORE_MONITOR_EMS_H

#include "peer_ems.h"
#include "../util/trace.h"

namespace p2psp {

class MonitorEMS : public PeerDBS {
 public:
  MonitorEMS();
  ~MonitorEMS();
};
}

#endif  // P2PSP_CORE_MONITOR_EMS_H
