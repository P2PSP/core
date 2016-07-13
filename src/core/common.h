//
//  common.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_COMMON_H
#define P2PSP_CORE_COMMON_H

#include <chrono>
#include <openssl/sha.h>
#include <vector>

namespace p2psp {

  class Common {

  public:

    static const int kMaxChunkNumber = 65536;
    // MAX_CHUNK_NUMBER = 2048
    // COUNTERS_TIMING = 0.1
    static const int kCountersTiming = 1; // In seconds

    static const bool kConsoleMode = true;

    // Set of rules flags
    static const char kIMS = 0x00; // IMS
    static const char kDBS = 0x01; // DBS
    static const char kACS = 0x02; // ACS
    static const char kLRS = 0x04; // LRS
    static const char kNTS = 0x08; // NIS
    //static const char kDIS = 0x10; // DIS
    static const char kSTRPE = 0x10; // This should be renamed to kCIS
    
    // TODO: Use colors
    // IMS_COLOR = Color.red
    // DBS_COLOR = Color.green
    // ACS_COLOR = Color.blue
    // LRS_COLOR = Color.cyan
    // NTS_COLOR = Color.purple
    // DIS_COLOR = Color.yellow

    static void sha256(std::vector<char> string, std::vector<char> &digest) {
      SHA256((unsigned char *)string.data(), string.size(),
    		  (unsigned char *)digest.data());
    }
  };
}

#endif  // P2PSP_CORE_COMMON_H
