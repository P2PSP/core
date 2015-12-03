//
//  splitter_lrs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunk Recovery Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_LRS_H_
#define P2PSP_CORE_SPLITTER_LRS_H_

#include <stdio.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "../util/trace.h"
#include "splitter_dbs.h"
#include "common.h"

namespace p2psp {
class SplitterLRS : public SplitterDBS {};
}

#endif  // defined P2PSP_CORE_SPLITTER_LRS_H_
