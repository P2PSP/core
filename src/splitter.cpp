//
//  splitter.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#include <iostream>
#include "core/splitter_ims.h"
#include "core/splitter_dbs.h"
#include "core/splitter_acs.h"
#include "core/splitter_lrs.h"

int main(int argc, const char *argv[]) {
  // TODO: Argument parser.

  // TODO: Configure splitter

  // TODO: Start the splitter's main thread

  // TODO: Print information about the status of the splitter

  p2psp::SplitterLRS splitter;
  splitter.Start();

  while (splitter.isAlive()) {
    boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
  }

  return 0;
}