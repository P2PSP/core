//
//  monitor_ems.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#include "monitor_ems.h"

namespace p2psp {

MonitorEMS::MonitorEMS(){
    magic_flags_ = Common::kEMS;
};

MonitorEMS::~MonitorEMS(){};


}
