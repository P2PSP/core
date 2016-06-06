//
//  common_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "common_nts.h"

namespace p2psp
{

const std::chrono::seconds CommonNTS::kHelloPacketTiming{1};

const std::chrono::seconds CommonNTS::kMaxPeerArrivingTime{15};

const std::chrono::seconds CommonNTS::kMaxTotalIncorporationTime{60};

}
