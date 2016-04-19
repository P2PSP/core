//
//  splitter_acs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  ACS: Adaptive Chunk-rate Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_ACS_H_
#define P2PSP_CORE_SPLITTER_ACS_H_

#include <stdio.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
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
  void InsertPeer(const boost::asio::ip::udp::endpoint &peer) override;
  void IncrementUnsupportivityOfPeer(
      const boost::asio::ip::udp::endpoint &peer) override;
  void RemovePeer(const boost::asio::ip::udp::endpoint &peer) override;
  void ResetCounters() override;
  virtual void SendChunk(const std::vector<char> &message,
                         const boost::asio::ip::udp::endpoint &destination) override;
  void ComputeNextPeerNumber(boost::asio::ip::udp::endpoint &peer) override;

  int GetPeriod(const boost::asio::ip::udp::endpoint &peer);
  int GetNumberOfSentChunksPerPeer(const boost::asio::ip::udp::endpoint &peer);
  void SetNumberOfSentChunksPerPeer(const boost::asio::ip::udp::endpoint &peer,
                                    int number_of_sent_chunks);
};
}
#endif  // defined P2PSP_CORE_SPLITTER_ACS_H_
