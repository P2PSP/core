//
//  splitter_strpe.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_strpe.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterSTRPE::SplitterSTRPE()
    : SplitterLRS(),
      logging_(kLogging),
      log_file_(kLogFile),
      current_round_(kCurrentRound) {
  LOG("STrPe");
}

SplitterSTRPE::~SplitterSTRPE() {}

void SplitterSTRPE::AddTrustedPeer(boost::asio::ip::udp::endpoint peer) {
  trusted_peers_.push_back(peer);
}
}