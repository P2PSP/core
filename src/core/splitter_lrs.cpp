//
//  splitter_lrs.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunk Recovery Set of rules
//

#include "splitter_lrs.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterLRS::SplitterLRS() : SplitterDBS(), buffer(buffer_size_) {
  magic_flags_ = Common::kLRS;
  LOG("Initialized LRS");
}

SplitterLRS::~SplitterLRS() {}
}