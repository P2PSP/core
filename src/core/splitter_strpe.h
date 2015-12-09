//
//  splitter_strpe.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_SPLITTER_STRPE_H_
#define P2PSP_CORE_SPLITTER_STRPE_H_

#include <stdio.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "../util/trace.h"
#include "splitter_lrs.h"
#include "common.h"

namespace p2psp {
class SplitterSTRPE : public SplitterLRS {
 protected:
  const bool kLogging = false;
  const std::string kLogFile = "";
  const int kCurrentRound = 0;

  bool logging_;
  std::string log_file_;
  int current_round_;

  std::vector<boost::asio::ip::udp::endpoint> trusted_peers_;

 public:
  SplitterSTRPE();
  ~SplitterSTRPE();
  void AddTrustedPeer(boost::asio::ip::udp::endpoint peer);
};
}

#endif  // defined P2PSP_CORE_SPLITTER_STRPE_H_
