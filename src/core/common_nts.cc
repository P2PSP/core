//
//  common_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GNU_GENERAL_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "common_nts.h"

namespace p2psp {
  
  const std::chrono::seconds Common_NTS::kHelloPacketTiming{1};
  
  const std::chrono::seconds Common_NTS::kMaxPeerArrivingTime{15};
  
  const std::chrono::seconds Common_NTS::kMaxTotalIncorporationTime{60};

}
