//
//  splitter_lrs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunk Recovery Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_LRS_H_
#define P2PSP_CORE_SPLITTER_LRS_H_

#include <stdio.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "splitter_acs.h"
#include "common.h"

namespace p2psp {
class SplitterLRS : public SplitterACS {
 protected:
  /* Massively lost chunks are retransmitted. So, the splitter
   needs to remember the chunks sent recently. Buffer is A
   circular array of messages (chunk_number, chunk) in network
   endian format. */
  std::vector<std::vector<char>> buffer_;

 public:
  SplitterLRS();
  ~SplitterLRS();
  void ProcessLostChunk(int lost_chunk_number,
                        const boost::asio::ip::udp::endpoint &sender) override;
  void SendChunk(const std::vector<char> &message,
                 const boost::asio::ip::udp::endpoint &destination) override;
};
}

#endif  // defined P2PSP_CORE_SPLITTER_LRS_H_
