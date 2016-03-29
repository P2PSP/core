//
//  peer.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "core/peer_core.h"

int main(int argc, const char* argv[]) {
  try {
    return p2psp::run(argc, argv);
  } catch (boost::system::system_error e) {
    TRACE(e.what());
  }

  return -1;
}
