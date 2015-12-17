//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  ACS: Adaptive Chunk-rate Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_ACS_H_
#define P2PSP_CORE_SPLITTER_ACS_H_

#include <stdio.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "../util/trace.h"
#include "splitter_dbs.h"
#include "common.h"

namespace p2psp {
class SplitterACS : public SplitterDBS {
 protected:
  boost::unordered_map<boost::asio::ip::udp::endpoint, int,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      period_;
  boost::unordered_map<boost::asio::ip::udp::endpoint, int,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      period_counter_;
  boost::unordered_map<boost::asio::ip::udp::endpoint, int,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      number_of_sent_chunks_per_peer_;

 public:
  SplitterACS();
  ~SplitterACS();
  void InsertPeer(boost::asio::ip::udp::endpoint peer);
  void IncrementUnsupportivityOfPeer(boost::asio::ip::udp::endpoint peer);
  void RemovePeer(boost::asio::ip::udp::endpoint peer);
  void ResetCounters();
  virtual void SendChunk(std::vector<char> &message,
                         boost::asio::ip::udp::endpoint destination);
  void ComputeNextPeerNumber(boost::asio::ip::udp::endpoint peer);

  int GetPeriod(boost::asio::ip::udp::endpoint peer);
  int GetNumberOfSentChunksPerPeer(boost::asio::ip::udp::endpoint peer);
  void SetNumberOfSentChunksPerPeer(boost::asio::ip::udp::endpoint peer,
                                    int number_of_sent_chunks);
};
}
#endif  // defined P2PSP_CORE_SPLITTER_ACS_H_
